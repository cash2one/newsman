#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
A wrapper for UCK's new interface
"""
# @author chengdujin
# @contact chengudjin@gmail.com
# @created Aug. 25, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from config import hparser
from data_processor import image_helper
import urllib2

# CONSTANTS
from config import UCK_TIMEOUT
from config import UCK_TRANSCODING_NEW


def _collect_images(content):
    """
    find all images from the content
    """
    return image_helper.find_images(content)


def _transcode(link):
    """
    send link to uck and get the data
    """
    html = urllib2.urlopen('%s%s' % (UCK_TRANSCODING_NEW, link), timeout=UCK_TIMEOUT).read()
    return urllib2.unquote(hparser.unescape(html))


def _extract(link):
    """
    extract title, content and images
    """
    data_string = _transcode(link)
    if data_string:
        data = eval(data_string)
        if int(data['status']) == 1:
            title = None if 'title' not in data or not data['title'] else data['title']
            content = None if 'content' not in data or not data['content'] else data['content']
            images = _collect_images(content)
            return title, content, images
        else:
            print '[baidu_uck_new] ERROR: UCK cannot parse the link'
            return None, None, None
    else:
        print '[baidu_uck_new._extract] ERROR: Get nothing from UCK server'
        return None, None, None


def convert(link):
    """
    call UCK's new interface to get title, images and content
    """
    if not link:
        raise Exception('[baidu_uck_new.convert] ERROR: Cannot transcode nothing!')

    try:
        title, content, images = _extract(link)
        return title, content, images
    except Exception as k:
        print '[baidu_uck_new.convert]', str(k)
        return None, None, None
