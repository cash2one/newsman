#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
call baidu uck's api to transcode a web page
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from config import hparser
from config import logger
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
import image_helper
import thumbnail
import urllib2

# CONSTANTS
from config import UCK_TIMEOUT
from config import UCK_TRANSCODING


# TODO: test the code
# TODO: remove code that sanitize too much
def _sanitize(content):
    """
    modified uck content to suit news needs
    """
    if not content:
        return None

    try:
        soup = BeautifulSoup(content.decode('utf-8', 'ignore'))
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

        # clear away useless style
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

        # filter item
        img_count = 0
        for item in soup.contents:
            if isinstance(item, Tag):
                if item.name == 'img':
                    img_count = img_count + 1
        if img_count == len(soup.contents):
            return None
        else:
            return ''.join([str(item) for item in soup.contents])
    except Exception as k:
        logger.error(str(k))
        return None


def _collect_images(data):
    """
    find all possible images
    1. image_list
    2. images in the new content
    """
    if not data:
        return None

    try:
        images = []
        # first try to find images in image_list
        if 'image_list' in data and data.get('image_list'):
            for image in data.get('image_list'):
                if 'src' in image and image['src']:
                    image_normalized = image_helper.find_image(
                        image['src'].strip())
                    if image_normalized:
                        images.append(image_normalized)

        # then try to find images in the content
        images_from_content = image_helper.find_images(data['content'])
        if images_from_content:
            images.extend(images_from_content)

        # remove duplicated ones
        images = image_helper.dedupe_images(images) if images else None
        return images
    except Exception as k:
        logger.error(str(k))
        return None


def _extract(data):
    """
    extract images and text content
    """
    if not data:
        logger.error('Received no data from UCK server.')
        return None, None, None

    successful = int(data['STRUCT_PAGE_TYPE'])
    if successful == 0:
        logger.info('Cannot interpret the page! status != 1')
        return None, None, None

    try:
        # content
        content = data['content'].replace("\\", "")
        content = _sanitize(content)

        # images
        images = _collect_images(data)
        images = images if images else None

        # title
        title = None
        if 'title' in data:
            title = data['title']

        return title, content, images
    except Exception as k:
        logger.error(str(k))
        return None, None, None


def _transcode(link):
    """
    send link to uck server
    """
    try:
        uck_url = '%s%s' % (UCK_TRANSCODING, link)
        # timeout set to UCK_TIMEOUT, currently
        html = urllib2.urlopen(uck_url, timeout=UCK_TIMEOUT).read()
        # free data from html encoding
        data = urllib2.unquote(hparser.unescape(html))
        return data
    except Exception as k:
        logger.error(str(k))
        return None


def convert(link):
    """
    send link to uck api and reformat the content
    """
    if not link:
        logger.error('Cannot transcode nothing!')
        return None, None, None

    # send link to uck server and get data back
    try:
        raw_data = _transcode(link)
        if raw_data:
            # text is sanitized, images are found from image_list
            title, transcoded, images = _extract(eval(raw_data))
            return title, transcoded, images
        else:
            logger.info('Cannot read anything from UCK server')
            return None, None, None
    except Exception as k:
        logger.error('%s for %s' % (str(k), link))
        return None, None, None
