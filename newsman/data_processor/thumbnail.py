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

from config import logger
from cStringIO import StringIO
import Image
import urllib2

# CONSTANTS
from config import MIN_IMAGE_SIZE
from config import IMAGES_LOCAL_DIR
from config import IMAGES_PUBLIC_DIR
from config import UCK_TIMEOUT


# TODO: this method should be moved to image_helper
def is_valid_image(image_url):
    """
    find out if the image has a resolution larger than MIN_IMAGE_SIZE
    """
    if not image_url:
        logger.error('Method malformed!')
        return False

    # check if image could be downloaded
    image_downloaded = None
    try:
        try:
            image_downloaded = urllib2.urlopen(image_url, timeout=UCK_TIMEOUT).read()
        except urllib2.URLError as k:
            logger.info(str(k))
        except Exception:
            logger.info('%s cannot be downloaded' % image_url)
            return False

        if image_downloaded:
            # possible exception raiser
            try:
                image_pil = Image.open(StringIO(image_downloaded))
            except Exception as k:
                logger.info(str(k))
                return False

            # to avoid line length limit
            if image_pil.size[0] * image_pil.size[1] > MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1]:
                return True
            else:
                return False
        else:
            logger.info('Nothing obtained from %s' % image_url)
            return False
    except Exception as k:
        logger.error('%s' % str(k))
        return False


# TODO: relative path could be a url including its suffix like jpg/png
def generate_thumbnail(image_url, relative_path):
    """
    generate a thumbnail
    """
    if not image_url or not relative_path:
        logger.error('Method malformed!')
        return None

    try:
        # possible exception raiser
        image_pil = Image.open(
            StringIO(urllib2.urlopen(image_url, timeout=UCK_TIMEOUT).read()))

        # generate thumbnail
        if image_pil.size > MIN_IMAGE_SIZE:
            # get various paths
            image_thumbnail_local_path = '%s%si.jpg' % (
                IMAGES_LOCAL_DIR, relative_path)
            image_thumbnail_web_path = '%s%s.jpg' % (
                IMAGES_PUBLIC_DIR, relative_path)

            # thumbnailing
            image_pil.thumbnail(MIN_IMAGE_SIZE, Image.ANTIALIAS)
            image_pil = image_pil.convert('RGB')
            image_pil.save(image_thumbnail_local_path, 'JPEG')
            return image_thumbnail_web_path
        else:
            return image_url
    except urllib2.URLError as k:
        logger.info(str(k))
        return None
    except Exception as k:
        logger.error(str(k))
        return None


def get_image_size(image_url):
    """
    docs needed
    """
    if not image_url:
        logger.error('Method malformed!')
        return None, None

    try:
        image_web = None
        if isinstance(image_url, str) or isinstance(image_url, unicode):
            logger.info('opening %s' % image_url)
            image_web = StringIO(
                urllib2.urlopen(image_url, timeout=UCK_TIMEOUT).read())
        else:
            logger.info('image_url is data')
            image_web = image_url

        if image_web:
            im = Image.open(image_web)
            width, height = im.size
            return width, height
        else:
            return None, None
    except urllib2.URLError as k:
        logger.info(str(k))
        return None, None
    except Exception as k:
        logger.error(str(k))
        return None, None
