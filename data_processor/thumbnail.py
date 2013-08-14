#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
thumbnail used to make thumbnails
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul., 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from cStringIO import StringIO
import Image
import urllib2

# CONSTANTS
from config import MIN_IMAGE_SIZE
from config import IMAGES_LOCAL_DIR
from config import IMAGES_PUBLIC_DIR
from config import UCK_TIMEOUT


# TODO: boundary checker should not return None, instead probably an Exception
# TODO: this method should be moved to image_helper
def is_valid_image(image_url):
    """
    find out if the image has a resolution larger than MIN_IMAGE_SIZE
    """
    if not image_url:
        return None
    image_pil = None
    try:
        image_pil = Image.open(StringIO(urllib2.urlopen(image_url, timeout=UCK_TIMEOUT).read()))
    except Exception as k:
        print '[thumbnail.is_valid_image]', str(k)
        raise k
    # to avoid line length limit
    if image_pil.size[0] * image_pil.size[1] > MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1]:
        return True
    else:
        return False


# TODO: boundary checkers
# TODO: relative path could be a url including its suffix like jpg/png
def generate_thumbnail(image_url, relative_path):
    """
    docs needed!
    """
    if not image_url or not relative_path:
        return None
    image_pil = None
    try:
        image_pil = Image.open(StringIO(
            urllib2.urlopen(image_url, timeout=UCK_TIMEOUT).read()))
    except Exception as k:
        print '[thumbnail.generate_thumbnail]', str(k)
        raise k
    # generate thumbnail
    if image_pil.size > MIN_IMAGE_SIZE:
        image_thumbnail_local_path = '%s%si.jpg' % (
            IMAGES_LOCAL_DIR, relative_path)
        image_thumbnail_web_path = '%s%s.jpg' % (
            IMAGES_PUBLIC_DIR, relative_path)
        image_pil.thumbnail(MIN_IMAGE_SIZE, Image.ANTIALIAS)
        image_pil = image_pil.convert('RGB')
        image_pil.save(image_thumbnail_local_path, 'JPEG')
        return image_thumbnail_web_path
    else:
        return image_url


def get_image_size(image_url):
    """
    docs needed
    """
    image_web = None
    if isinstance(image_url, str) or isinstance(image_url, unicode):
        print '[thumbnail.get_image_size] opening %s' % image_url 
        image_web = StringIO(urllib2.urlopen(image_url, timeout=UCK_TIMEOUT).read())
    else:
        print '[thumbnail.get_image_size] image_url is data'
        image_web = image_url
    im = Image.open(image_web)
    width, height = im.size
    return width, height
