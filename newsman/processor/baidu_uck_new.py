#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
A wrapper for UCK's new interface
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Aug. 25, 2013'

from newsman.config.settings import hparser
from newsman.config.settings import logger
import illustrator
import sys
import urllib2

# CONSTANTS
from newsman.config.settings import UCK_TIMEOUT
from newsman.config.settings import UCK_TRANSCODING_NEW

reload(sys)
sys.setdefaultencoding('UTF-8')


def _collect_images(content=None, referer=None):
    """
    find all images from the content
    """
    if not content:
        logger.error('Content/HTML is found VOID!')
        return None

    images, content_new = illustrator.find_images(content, referer)
    if content_new and content_new != content:
        content = content_new
    return images, content


def _transcode(link):
    """
    send link to uck and get the data
    """
    try:
        html = urllib2.urlopen(
            '%s%s' % (UCK_TRANSCODING_NEW, link), timeout=UCK_TIMEOUT).read()
        data = urllib2.unquote(hparser.unescape(html))
        return data
    except Exception as k:
        logger.info('Problem:[%s] Source:[%s]' % (str(k), link))
        return None


def _extract(link):
    """
    extract title, content and images
    """
    data_string = _transcode(link)
    if data_string:
        # syntax checker
        try:
            eval(data_string)
        except Exception:
            logger.info('Invalid syntax found for New UCK output')
            return None, None, None

        data = eval(data_string)

        if int(data['status']) == 1:
            title = None if 'title' not in data or not data[
                'title'] else data['title']
            content = None if 'content' not in data or not data[
                'content'] else data['content']
            images, content = _collect_images(content, link)
            return title, content, images
        else:
            logger.info('UCK cannot parse the link: status != 1')
            return None, None, None
    else:
        logger.info('Get nothing from UCK server')
        return None, None, None


def convert(link):
    """
    call UCK's new interface to get title, images and content
    """
    if not link:
        logger.error('Cannot transcode nothing!')
        return None, None, None

    try:
        title, content, images = _extract(link)
        return title, content, images
    except Exception as k:
        logger.error('%s for %s' % (str(k), str(link)))
        return None, None, None
