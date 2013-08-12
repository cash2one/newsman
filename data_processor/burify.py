#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
call burify's implementation of readability code to transcode a web page
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 6, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import chardet
from data_processor import image_helper
from readability import Document
import urllib2

# CONSTANTS
from config import UCK_TIMEOUT


def _collect_images(content):
    """
    find all images from the content
    """
    return image_helper.find_images(content)


def _prepare_link(url):
    """
    decode with the correct encoding
    """
    html = urllib2.urlopen(url, timeout=UCK_TIMEOUT).read()
    if html:
        detected = chardet.detect(html)
        if detected:
            data = html.decode(detected['encoding'], 'ignore')
        else:
            data = html.decode('utf-8', 'ignore')
        return data
    else:
        raise Exception("ERROR: Cannot read %s" % url)


def convert(link):
    """
    use burify's readability implementation to transcode a web page
    and return the transcoded page and images found in it
    """
    if not link:
        raise Exception('ERROR: Cannot transcode nothing!')

    try:
        data = _prepare_link(link)
        article = Document(data)
        images = _collect_images(article.summary())
        return article.short_title(), article.summary(html_partial=False), images
    except Exception as k:
        print k
        return None, None, None
