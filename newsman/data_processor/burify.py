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

from config import logging
import image_helper
from readability import Document
import transcoder


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
        logging.error('Cannot transcode nothing!')
        return None, None, None

    try:
        data = transcoder.prepare_link(link)
        if data:
            article = Document(data)
            if article:
                images = _collect_images(article.summary())
                return article.short_title(), article.summary(html_partial=False), images
            else:
                logging.error('Burify cannot recognize the data')
                return None, None, None
        else:
            logging.error('Cannot parse link correctly')
            return None, None, None
    except Exception as k:
        logging.exception(str(k))
        return None, None, None
