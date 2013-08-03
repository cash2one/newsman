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
from administration.config import TRANSCODING_BTN_AR
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
    'ind': TRANSCODING_BTN_IND, 'en-rIN': TRANSCODING_BTN_EN, 'ar': TRANSCODING_BTN_AR
}


def _generate_path(content, relative_path):
    """
    create local and web path
    """
    if not content or not relative_path:
        return None

    local_path = '%s%s.html' % (TRANSCODED_LOCAL_DIR, relative_path)
    web_path = '%s%s.html' % (TRANSCODED_PUBLIC_DIR, relative_path)
    f = open(local_path, 'w')
    f.write(hparser.unescape(content))
    f.close()
    return web_path, local_path


def _combine_template(content, language, title):
    """
    find a suitable template and embed content in it
    """
    if not content or not language or not title:
        return None

    # f reads the template
    f = None
    if language == 'ar':
        f = open(NEWS_TEMPLATE_ARABIC, 'r')
    else:
        f = open(NEWS_TEMPLATE, 'r')
    # a template is found
    if f:
        template = str(f.read())
        f.close()
        return template % (title, title, content, transcoding_button_language[language])
    else:
        return None


# TODO: test the code
# TODO: remove code that sanitize too much
def _sanitize(content):
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
def _extract(data):
    """
    extract images and text content
    """
    if data:
        successful = int(data['STRUCT_PAGE_TYPE'])
        if successful == 0:
            raise Exception('ERROR: Cannot interpret the page!')

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
                                pass
                            except Exception as k:
                                print k
                        if response:
                            width, height = thumbnail.get_image_size(image_url)
                            images.append({'url':image_url, 'width':width, 'height':height})
                    else:
                        print 'Cannot find enough content in src tag'
                else:
                    print 'Nothing found in image_list'
        images = images if images else None

        # content
        content = data['content'].replace("\\", "")
        new_content = _sanitize(content)

        return new_content, images
    else:
        # no data found
        raise Exception('ERROR: Have not received data from transcoding server.')


def _transcode(link):
    """
    send link to uck server
    """
    def _url_extract(url):
        """
        find the real link in a composite url address
        """
        last_http_index = url.rfind('http')
        return url[last_http_index:]

    uck_url = '%s%s' % (UCK_TRANSCODING, _url_extract(link))
    # timeout set to 10, currently
    try:
        f = urllib2.urlopen(uck_url, timeout=10)
        # free data from html encoding
        return urllib2.unquote(f.read())
    except IOError as k:
        raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))


# TODO: should separate images from transcoding
# TODO: return an exception when fucked up
def uck(language, title, link, relative_path):
    """
    send link to uck api and reformat the content
    """
    if not language or not title or not link or not relative_path:
        raise Exception('ERROR: Method not well formed!')

    # send link to uck server and get data back
    raw_data = _transcode(link)
    if raw_data:
        # text is sanitized, images are found from image_list
        transcoded, images = _extract(eval(raw_data))
        news = _combine_template(transcoded, language, title)

        if news:
            web_path, local_path = _generate_path(news, relative_path)
            if not web_path:
                raise Exception('ERROR: Cannot generate web path for %s properly!' % link)
            return web_path, local_path, images
        else:
            raise Exception('ERROR: Cannot generate news from template.')
    else:
        raise Exception('ERROR: Nothing found in return.')

