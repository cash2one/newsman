#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#
#@created Jan 2, 2013
#@updated Feb 5, 2013
#@updated Jul 13, 2013
#
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from decruft import Document
from administration.config import hparser
import Image
from administration.config import NEWS_TEMPLATE
from administration.config import NEWS_TEMPLATE_ARABIC
import os
import re
from cStringIO import StringIO
from image_processor import thumbnail
from administration.config import MIN_IMAGE_SIZE
from administration.config import TRANSCODING_BTN_EN
from administration.config import TRANSCODING_BTN_JA
from administration.config import TRANSCODING_BTN_TH
from administration.config import TRANSCODING_BTN_PT
from administration.config import TRANSCODING_BTN_IND
from administration.config import TRANSCODED_ENCODING   # lijun
from administration.config import TRANSCODED_LOCAL_DIR
from administration.config import TRANSCODED_PUBLIC_DIR
from administration.config import UCK_TRANSCODING
import urllib2
import urlparse


if not os.path.exists(TRANSCODED_LOCAL_DIR):
    os.mkdir(TRANSCODED_LOCAL_DIR)

transcoding_button_language = {
    'en': TRANSCODING_BTN_EN, 'ja': TRANSCODING_BTN_JA,
    'th': TRANSCODING_BTN_TH, 'pt': TRANSCODING_BTN_PT,
    'ind': TRANSCODING_BTN_IND, 'en-rIN': TRANSCODING_BTN_EN
}


def generate_path(content, relative_path):
    ''''''
    if not content or not relative_path:
        return None
    local_path = '%s%s.html' % (TRANSCODED_LOCAL_DIR, relative_path)
    web_path = '%s%s.html' % (TRANSCODED_PUBLIC_DIR, relative_path)
    f = open(local_path, 'w')
    f.write(hparser.unescape(content))
    f.close()
    return web_path, local_path


# TODO: test the code
# TODO: remove code that sanitize too much
def uck_sanitize(content):
    ''''''
    soup = BeautifulSoup(content.decode('utf-8'))
    # remove all <span>
    for span in soup.findAll('span'):
        span.extract()
    # sanitize <a>
    for a in soup.findAll('a'):
        img = a.find('img')
        if img:
            a.replaceWith(img)
        else:  # it might be a simple href
            a.replaceWith(a.text)
    # remove img prefix
    for img in soup.findAll('img'):
        img_source = img.get('src')
        if img_source:
            img_tuple = img_source.rpartition('src=')
            img['src'] = img_tuple[2]
            width, height = thumbnail.get_image_size(img['src'])
            if width >= 480:
                img['width'] = '100%'
                img['height'] = 'auto'
    # clear away useless style : lijun
    for style in soup.findAll('div', style='border-top:none;'):
        img = style.find('img')
        if not img:
            if not style.find('p'):
                style.extract()
        else:
            style.replaceWith(img)
    # remove navigble strings and <div>
    for component in soup.contents:
        if isinstance(component, NavigableString):
            if len(component.string.split()) < 10:
                component.extract()
        elif isinstance(component, Tag):
            if component.name == 'div':
                if not component.find('p'):
                    component.extract()
    # filter item by lijun
    img_count = 0
    for item in soup.contents:
        if isinstance(item, Tag):
            if item.name == 'img':
                img_count = img_count + 1
    if img_count == len(soup.contents):
        return None
    else:
        return ''.join([str(item) for item in soup.contents])


# TODO: extract image_list part into a new method
def uck_reformat(language, title, data):
    ''''''
    if data:
        successful = int(data['STRUCT_PAGE_TYPE'])
        if successful == 0:
            return None

        # images
        images = []
        if 'image_list' in data and data.get('image_list'):
            for image in data.get('image_list'):
                if 'src' in image and image['src']:
                    image_url_complex = urllib2.unquote(image['src'].strip())
                    if image_url_complex:
                        # as the name could be http://xxx.com/yyy--http://zzz.jpg
                        # or http://xxx.com/yyy--https://zzz.jpg
                        last_http_index = image_url_complex.rfind('http')
                        image_url = image_url_complex[last_http_index:]
                        # response is the signal of a valid image
                        response = None
                        try:
                            response = urllib2.urlopen(image_url)
                        except urllib2.URLError as k:
                            path = re.split('https?://?', image_url)[-1]
                            scheme = urlparse.urlparse(image_url).scheme
                            image_url = '%s://%s' % (scheme, path)
                            try:
                                response = urllib2.urlopen(image_url)
                            except urllib2.URLError as k:
                                print '[WARNING]', k, image_url
                            except Exception as e:
                                print e
                        if response:
                            width, height = thumbnail.get_image_size(image_url)
                            images.append({'url':image_url, 'width':width, 'height':height})
                    else:
                        print 'Cannot find enought content in src tag'
                else:
                    print 'Nothing found in image_list'
        images = images if images else None

        # content
        content = data['content'].replace("\\", "")
        new_content = uck_sanitize(content)
        if new_content:
            # f reads the template
            f = None
            if language == 'ar':
                f = open(NEWS_TEMPLATE_ARABIC, 'r')
            else:
                f = open(NEWS_TEMPLATE, 'r')
            if f:
                template = str(f.read())
                f.close()
                news = template % (title, title, new_content, transcoding_button_language[language])
                return news, images
            else:
                return None
        else:
            return None
    else:
        # no data found
        return None


def process_url(link):
    last_http_index = image_url_complex.rfind('http:/')
    image_url = image_url_complex[last_http_index:]
    path = re.split('https?://?', image_url)[-1]
    scheme = urlparse.urlparse(image_url).scheme
    image_url = '%s://%s' % (scheme, path)

    if link and link.count('http') > 1:
        p = link.rpartition('http')
        if p:
            return '%s%s' % (p[1], p[2])
        else:
            return None
    else:
        return link


def _transcode(language, title, link):
    """
    send link to uck server
    """
    link = process_url(link)
    uck_url = '%s%s' % (UCK_TRANSCODING, link)
    f = urllib2.urlopen(uck_url, timeout=5)
    recv = urllib2.unquote(f.read())
    return recv


# TODO: should separate images from transcoding
# TODO: return an exception when fucked up
def uck(language, title, link, relative_path):
    """
    send link to uck api and reformat the content
    """
    if not language or not title or not link or not relative_path:
        raise Exception('ERROR: Method not well formed!')

    transcoded_raw = _trasncode(language, title, link)
    results = _uck_reformat(language, title, eval(transcoded_raw))

    if results:
        transcoded, images = results
        # demo to return an exception
        if not transcoded:
            raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))
        # sanitizing work put here
        web_path, local_path = generate_path(transcoded, relative_path)
        if not web_path:
            raise Exception('ERROR: Cannot generate web path for %s properly!' % link)
        return web_path, local_path, images
    else:
        raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))
