#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import Image
from cStringIO import StringIO
import urllib2

from administration.config import MIN_IMAGE_SIZE
from administration.config import IMAGES_LOCAL_DIR
from administration.config import IMAGES_PUBLIC_DIR


# TODO: boundary checker should not return None, instead probably an Exception
# TODO: this method should be moved to image_helper
def is_valid_image(image_url):
    """
    find out if the image has a resolution larger than MIN_IMAGE_SIZE
    """
    if not image_url:
        return None
    image_pil = Image.open(StringIO(urllib2.urlopen(image_url).read()))
    return True if image_pil.size[0] * image_pil.size[1] > MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1] else False


# TODO: boundary checkers
# TODO: relative path could be a url including its suffix like jpg/png
def generate_thumbnail(image_url, relative_path):
    """
    docs needed!
    """
    if not image_url or not relative_path:
        return None
    image_web = StringIO(urllib2.urlopen(image_url).read())
    image_pil = Image.open(image_web)
    # generate thumbnail
    if image_pil.size > MIN_IMAGE_SIZE:
        image_thumbnail_local_path = '%s%si.jpg' % (
            IMAGES_LOCAL_DIR, relative_path)
        image_thumbnail_web_path = '%s%s.jpg' % (
            IMAGES_PUBLIC_DIR, relative_path)
        image_pil.thumbnail(config.MIN_IMAGE_SIZE, Image.ANTIALIAS)
        image_pil = image_pil.convert('RGB')
        image_pil.save(image_thumbnail_local_path, 'JPEG')
        return image_thumbnail_web_path
    else:
        return image_url


def get_image_size(image_url):
    """
    docs needed
    """
    try:
        image_web = StringIO(urllib2.urlopen(image_url).read())
    except Exception as e:
        print e
        image_web = image_url
    im = Image.open(image_web)
    width, height = im.size
    return width, height
