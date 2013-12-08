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

from config.settings import logger
import illustrator
from readability import Document
import transcoder


def _collect_images(content, referer):
    """
    find all images from the content
    """
    if not content:
        logger.error('Content/HTML found VOID!')
        return None

    images, content_new = illustrator.find_images(content, referer)
    if content_new and content_new != content:
        content = content_new
    return images, content


def convert(link):
    """
    use burify's readability implementation to transcode a web page
    and return the transcoded page and images found in it
    """
    if not link:
        logger.error('Cannot transcode nothing!')
        return None, None, None

    try:
        data = transcoder.prepare_link(link)
        if data:
            article = Document(data)
            if article:
                images, content  = _collect_images(article.summary(html_partial=False), link)
                return article.short_title(), content, images
            else:
                logger.info('Burify cannot recognize the data')
                return None, None, None
        else:
            logger.info('Cannot parse %s correctly' % link)
            return None, None, None
    except Exception as k:
        logger.error('%s for %s' % (str(k), str(link)))
        return None, None, None
