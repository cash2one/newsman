#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
image_scraper is used to find all images from a web page
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 23, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulSoup
from config import hparser
from config import logging
from cStringIO import StringIO
import Image
import os
import re
import thumbnail
import urllib2
import urlparse

# CONSTANTS
from config import IMAGES_LOCAL_DIR
from config import IMAGES_PUBLIC_DIR
from config import MIN_IMAGE_SIZE
from config import TRANSCODED_LOCAL_DIR
from config import UCK_TIMEOUT

# creat images local directory if it does not exist
if not os.path.exists(IMAGES_LOCAL_DIR):
    os.mkdir(IMAGES_LOCAL_DIR)


def _link_process(link):
    """
    get rid of cdn prefix
    """
    if not link:
        return None

    try:
        link = link.replace("\/", "/").strip()
        image_url_complex = urllib2.unquote(hparser.unescape(link))

        if image_url_complex:
            # as the name could be http://xxx.com/yyy--http://zzz.jpg
            # or http://xxx.com/yyy--https://zzz.jpg
            last_http_index = image_url_complex.rfind('http')
            image_url = image_url_complex[last_http_index:]

            # response is the signal of a valid image
            response = None
            try:
                response = urllib2.urlopen(image_url, timeout=UCK_TIMEOUT)
            except urllib2.URLError as k:
                path = re.split('https?://?', image_url)[-1]
                scheme = urlparse.urlparse(image_url).scheme
                image_url = '%s://%s' % (scheme, path)
                try:
                    response = urllib2.urlopen(image_url, timeout=UCK_TIMEOUT)
                except urllib2.URLError as k:
                    logging.info(str(k))
                except Exception as k:
                    logging.info(str(k))
            if response:
                return image_url
            else:
                return None
        else:
            return None
    except Exception as k:
        pass
        logging.exception(str(k))
        return None


def find_image(link=None):
    """
    find an image from the link
    """
    if not link:
        return None

    try:
        link = _link_process(link)
        if link:
            image_normalized = normalize(link)
            return image_normalized[0] if image_normalized else None
        else:
            logging.error('Cannot parse link correctly')
            return None
    except Exception as k:
        pass
        logging.exception(str(k))
        return None


def find_images(content=None):
    """
    find out all images from content and its size info
    """
    if not content:
        return None

    try:
        # determine the type of content
        if isinstance(content, str) and content.startswith(TRANSCODED_LOCAL_DIR):
            # then its a file
            f = open(content, 'r')
            content = f.read()

        soup = BeautifulSoup(content.decode('utf-8', 'ignore'))
        images_normalized = []
        images = soup.findAll('img')

        for image in images:
            if image.get('src'):
                image_normalized = find_image(image.get('src'))
                if image_normalized:
                    images_normalized.append(image_normalized)

        return images_normalized
    except Exception as k:
        pass
        logging.exception(str(k))
        return None


def find_biggest_image(images=None):
    """
    find the biggest in resolution from a pile of images
    """
    if not images:
        return None

    try:
        biggest = None
        for image in images:
            resolution_max = MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1]
            resolution_image = int(image['width']) * int(image['height'])
            if resolution_image > resolution_max:
                biggest = image
                resolution_max = resolution_image
        return biggest
    except Exception as k:
        pass
        logging.exception(str(k))
        return None


def dedupe_images(images):
    """
    remove same images
    image: {'url':xxx, 'width':yyy, 'height':zzz}
    images = [image, image, image]
    """
    if not images:
        return None

    image_urls = []

    def _exists(image):
        """
        return boolean if image exists in list image_urls
        """
        exists = image['url'] in image_urls
        if not exists:
            image_urls.append(image['url'])
            return False
        else:
            return True

    try:
        return filter(lambda x: not _exists(x), images)
    except Exception as k:
        pass
        logging.exception(str(k))
        return None


# TODO: boundary checker
def scale_image(image=None, size_expected=MIN_IMAGE_SIZE,
                resize_by_width=True, crop_by_center=True, relative_path=None):
    """
    resize an image as requested
    resize_by_width: resize image according to its width(True)/height(False)
    crop_by_center: crop image from its center(True) or by point(0, 0)(False)
    """
    if not image or not size_expected or not relative_path:
        logging.error('Method malformed!')
        return None, None

    try:
        width = int(image['width'])
        height = int(image['height'])
        width_expected = size_expected[0]
        height_expected = size_expected[1]

        if width >= width_expected and height >= height_expected:
            if resize_by_width:
                height_new = width_expected * height / width
                width_new = width_expected
            else:
                width_new = height_expected * width / height
                height_new = height_expected

            # larger and equal than is important here
            if width_new >= width_expected and height_new >= height_expected:
                # resize
                size_new = width_new, height_new
                # possible exception raiser
                image_data = Image.open(
                    StringIO(urllib2.urlopen(image['url'], timeout=UCK_TIMEOUT).read()))
                image_data.thumbnail(size_new, Image.ANTIALIAS)

                # crop
                if crop_by_center:
                    left = (width_new - width_expected) / 2
                    top = (height_new - height_expected) / 2
                    right = (width_new + width_expected) / 2
                    bottom = (height_new + height_expected) / 2
                    image_cropped = image_data.crop((left, top, right, bottom))
                else:
                    left = 0
                    top = 0
                    right = width_expected
                    bottom = height_expected
                    image_cropped = image_data.crop((left, top, right, bottom))

                # storing
                if image_cropped:
                    image_web_path = '%s%s.jpg' % (
                        IMAGES_PUBLIC_DIR, relative_path)
                    image_local_path = '%s%s.jpg' % (
                        IMAGES_LOCAL_DIR, relative_path)
                    image_cropped = image_cropped.convert('RGB')
                    image_cropped.save(image_local_path, 'JPEG')
                    return {'url': image_web_path, 'width': width_expected, 'height': height_expected}, {'url': image_local_path, 'width': width_expected, 'height': height_expected}
                else:
                    return None, None
            else:
                return scale_image(image, size_expected, not resize_by_width, crop_by_center, relative_path)
        else:
            return None, None
    except Exception as k:
        pass
        logging.exception(str(k))
        return None, None


def normalize(images):
    """
    for list of images, remove images that don't match with MIN_IMAGE_SIZE;
    for an image, return None if it doesn't matches with MIN_IMAGE_SIZE
    """

    def _check_image(image):
        """
        check an image if it matches with MIN_IMAGE_SIZE
        """
        if not image:
            logging.error('Method malformed!')
            return None

        try:
            if 'url' in image:
                image_url = image['url']
                if thumbnail.is_valid_image(image_url):
                    return image
            else:
                if thumbnail.is_valid_image(image):
                    width, height = thumbnail.get_image_size(image)
                    if width and height:
                        return {'url': image, 'width': width, 'height': height}
                    else:
                        logging.error('Cannot get image size')
                        return None
            return None
        except IOError as k:
            pass
            logging.exception(str(k))
            return None

    try:
        if isinstance(images, str) or isinstance(images, unicode):
            image = _check_image(images)
            return [image] if image else None
        elif isinstance(images, list):
            images_new = []
            for image in images:
                image_new = _check_image(image)
                if image_new:
                    images_new.append(image_new)
            return images_new if images_new else None
    except Exception as k:
        pass
        logging.exception(str(k))
        return None
