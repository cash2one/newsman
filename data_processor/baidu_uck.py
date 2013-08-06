#!/usr/bin/python
# -*- coding: utf-8 -*-

# call baidu uck's api to transcode a web page
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import NavigableString
from BeautifulSoup import Tag
from image_processor import image_helper
from image_processor import thumbnail
import re
import urllib2
import urlparse

from administration.config import UCK_TRANSCODING


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


def _collect_images(data):
    """
    find all possible images
    1. image_list
    2. images in the new content
    """
    if not data:
        return None

    images = []
    # first try to find images in image_list
    if 'image_list' in data and data.get('image_list'):
        for image in data.get('image_list'):
            if 'src' in image and image['src']:
                image_normalized = image_helper.find_image(image['src'].strip())
                if image_normalized:
                    images.append(image_normalized)

    # then try to find images in the content
    images_from_content = image_helper.find_images(data['content'])
    if images_from_content:
        images.extend(images_from_content)

    # remove duplicated ones
    images = image_helper.dedupe_images(images) if images else None
    return images


def _extract(data):
    """
    extract images and text content
    """
    if data:
        successful = int(data['STRUCT_PAGE_TYPE'])
        if successful == 0:
            raise Exception('ERROR: Cannot interpret the page!')

        # content
        content = data['content'].replace("\\", "")
        content = _sanitize(content)

        # images
        images = _collect_images(data)
        images = images if images else None

        return content, images
    else:
        # no data found
        raise Exception('ERROR: Have not received data from transcoding server.')


def _transcode(link):
    """
    send link to uck server
    """
    uck_url = '%s%s' % (UCK_TRANSCODING, link)
    # timeout set to 10, currently
    try:
        f = urllib2.urlopen(uck_url, timeout=10)
        # free data from html encoding
        return urllib2.unquote(f.read())
    except IOError as k:
        raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))


def convert(link):
    """
    send link to uck api and reformat the content
    """
    if not link:
        raise Exception('ERROR: Cannot transcode nothing!')

    # send link to uck server and get data back
    try:
        raw_data = _transcode(link)
        if raw_data:
            # text is sanitized, images are found from image_list
            transcoded, images = _extract(eval(raw_data))
            return transcoded, images
        else:
            raise Exception('ERROR: Nothing found in return.')
    except Exception as k:
        print k
        return None, None
