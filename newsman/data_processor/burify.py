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

import image_helper
import transcoder
from readability import Document

# CONSTANTS
from config import UCK_TIMEOUT


def _collect_images(content):
    """
    find all images from the content
    """
    return image_helper.find_images(content)


def convert(link):
    """
    use burify's readability implementation to transcode a web page
    and return the transcoded page and images found in it
    """
    if not link:
        raise Exception('[burify.convert] ERROR: Cannot transcode nothing!')

    try:
        data = transcoder.prepare_link(link)
        article = Document(data)
        images = _collect_images(article.summary())
        return article.short_title(), article.summary(html_partial=False), images
    except Exception as k:
        print '[burify.convert]', str(k)
        return None, None, None
