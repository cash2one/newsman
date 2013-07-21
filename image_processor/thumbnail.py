#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import Image
from cStringIO import StringIO
import urllib2

from administration.config import THUMBNAIL_SIZE
from administration.config import THUMBNAIL_LOCAL_DIR
from administration.config import THUMBNAIL_WEB_DIR


# Todos
# boundary checker should not return None, instead probably an Exception 
def is_thumbnail(image_url):
    """
    docs needed
    """
    if not image_url:
        return None
    image_pil = Image.open(StrinIO(urllib2.urlopen(image_url).read())) 
    return True if image_pil.size < THUMBNAIL_SIZE else False


# Todos
# boundary checkers
# relative path could be a url including its suffix like jpg/png
def generate_thumbnail(image_url, relative_path):
    """
    docs needed!
    """
    if not image_url or not relative_path:
        return None
    image_web = StringIO(urllib2.urlopen(image_url).read())
    image_pil = Image.open(image_web)
    # generate thumbnail
    if image_pil.size > THUMBNAIL_SIZE:
        image_thumbnail_local_path = '%s%si.jpg' % (
            THUMBNAIL_LOCAL_DIR, relative_path)
        image_thumbnail_web_path = '%s%s.jpg' % (
            THUMBNAIL_WEB_DIR, relative_path)
        image_pil.thumbnail(config.THUMBNAIL_SIZE, Image.ANTIALIAS)
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
