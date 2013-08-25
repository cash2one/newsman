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


def _fetch_data(link):
    """
    send link to uck and parse the result
    """
    html = urllib2.urlopen('%s%s' % (UCK_TRANSCODING_NEW, link), timeout=UCK_TIMEOUT).read()


def convert(link):
    """
    call UCK's new interface to get title, images and content
    """
    if not link:
        raise Exception('[baidu_uck_new.convert] ERROR: Cannot transcode nothing!')

    try:
        title, content, images = _fetch_data(link)
        return title, content, images
    except Exception as k:
        print '[baidu_uck_new.convert]', str(k)
        return None, None, None
