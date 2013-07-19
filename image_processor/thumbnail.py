#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')


import Image
from cStringIO import StringIO
import urllib2


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
        image_thumbnail_local_path = '%s%s.jpeg' % (
            THUMBNAIL_LOCAL_DIR, relative_path)
        image_thumbnail_web_path = '%s%s.jpeg' % (
            THUMBNAIL_WEB_DIR, relative_path)
        image_pil.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        image_pil = image_pil.convert('RGB')
        image_pil.save(image_thumbnail_local_path, 'JPEG')
        return image_thumbnail_web_path
    else:
        return image_url
