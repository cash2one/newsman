#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
illustrator is used to find all images from a web page
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 23, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulSoup
from config.settings import hparser
from config.settings import logger
from cStringIO import StringIO
from PIL import Image
import os
import re
import requests
import urllib2

# CONSTANTS
from config.settings import HEADERS
from config.settings import IMAGES_LOCAL_DIR
from config.settings import IMAGES_PUBLIC_DIR
from config.settings import MIN_IMAGE_SIZE
from config.settings import TRANSCODED_LOCAL_DIR
from config.settings import UCK_TIMEOUT

# creat images local directory if it does not exist
if not os.path.exists(IMAGES_LOCAL_DIR):
    os.mkdir(IMAGES_LOCAL_DIR)


class NormalizedImage:
    """
    Class of normalized image
    """
    def __init__(self, image_url=None, referer=None):
        if not image_url:
            logger.error('Method malformed!')
            raise Exception('Method malformed!')

        self._image_url, self._image_html = self._analyze(image_url, referer)
        self._image_size = self._calculate_size()

    def _analyze(self, image_url=None, referer=None):
        """
        remove CDN prefix, if any; and read image data
        """
        if not image_url:
            logger.error('Method malformed!')
            raise Exception('Method malformed!')

        image_url = image_url.replace("\/", "/").strip()
        image_url = urllib2.unquote(hparser.unescape(image_url))

        # as the name could be http://xxx.com/yyy--http://zzz.jpg
        # or http://xxx.com/yyy--https://zzz.jpg
        last_http_index = image_url.rfind('http')
        image_url = image_url[last_http_index:]

        response = None
        if referer:
            HEADERS['Referer'] = referer
        try:
            response = requests.get(image_url, headers=HEADERS, timeout=UCK_TIMEOUT)
            # avoid redirected URL
            image_url = response.url
            # either exception or wrong HTTP code
            if response.status_code >= 400:
                raise Exception('Response code %s' % response.status_code)
        except Exception as k:
            logger.info('%s for %s' % (str(k), str(image_url)))
            try:
                # CDN URL could be formed as http:/xxxx.jpg
                path = re.split('https?://?', image_url)[-1]
                scheme = requests.utils.urlparse(image_url).scheme
                image_url = '%s://%s' % (scheme, path)

                response = requests.get(image_url, headers=HEADERS, timeout=UCK_TIMEOUT)
                # avoid redirected URL
                image_url = response.url
                if response.status_code >= 400:
                    raise Exception('Response code %s' % response.status_code)
            except Exception as k:
                logger.error('%s for %s' % (str(k), str(image_url)))
                raise Exception('%s for %s' % (str(k), str(image_url)))

        if response and response.status_code < 400 and response.content:
            # GIF is not supported yet
            image_url_parsed = requests.utils.urlparse(image_url)
            image_url_address = image_url_parsed.netloc + image_url_parsed.path
            if image_url_address.lower().endswith('.gif'):
                raise Exception('GIF is not supported! %s' % str(image_url))
            else:
                return str(image_url), str(urllib2.unquote(hparser.unescape(response.content)))
        else:
            logger.error('Cannot parse %s' % str(image_url))
            raise Exception('Cannot parse %s' % str(image_url))

    def _calculate_size(self):
        """
        read data into memory and return the image size
        """
        try:
            if self._image_html:
                image_data = Image.open(StringIO(self._image_html))
                self._image_size = image_data.size  #width, height
            else:
                return None, None
        except Exception as k:
            logger.error('Problem:[%s] Source:[%s]' % (str(k), str(self._image_url)))
            return None, None

    def get_image_size(self):
        """
        output image size
        """
        return self._image_size

    def get_image_url(self):
        """
        output updated image url
        """
        return self._image_url

    def _is_valid_image(self):
        """
        check if the image has a resolution larger than MIN_IMAGE_SIZE
        """
        try:
            width, height = self._image_size
            if width and height:
                return True if width * height > MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1] else False
            return False
        except Exception as k:
            logger.error('Problem:[%s] Source:[%s]' % (str(k), str(self._image_url)))
            return False

    def normalize(self):
        """
        output image with proper format
        i.e. {'url':xxx, 'width':yyy, 'height':zzz}
        """
        try:
            if self._is_valid_image():
                width, height = self._image_size
                if width and height:
                    return [{'url': self._image_url, 'width': width, 'height': height}]
            return None
        except Exception as k:
            logger.error('Problem:[%s]\nSource:[%s]' % (str(k), str(self._image_url)))
            return None


def dedup_images(images=None):
    """
    remove same images
    image: {'url':xxx, 'width':yyy, 'height':zzz}
    images = [image, image, image]
    """
    if not images:
        logger.error('Image list is found VOID!')
        return None

    image_urls = []

    def _exists(image):
        """
        return boolean if image exists in the image_urls list
        """
        if image['url'] not in image_urls:
            image_urls.append(image['url'])
            return False
        else:
            return True

    try:
        return filter(lambda x: not _exists(x), images)
    except Exception as k:
        logger.info('Problem:[%s]\nSource:[%s]' % (str(k), str(images)))
        return None


def find_biggest_image(images=None):
    """
    find the biggest image in resolution from a list of images
    """
    if not images:
        logger.error('Image list is found VOID!')
        return None

    try:
        biggest = None
        resolution_max = MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1]
        for image in images:
            if 'width' in image and 'height' in image:
                resolution_image = int(image['width']) * int(image['height'])
                if resolution_image > resolution_max:
                    biggest = image
                    resolution_max = resolution_image
            else:
                logger.error('Height and width not found! %s' % str(image))
        return biggest
    except Exception as k:
        logger.error('Problem:[%s]\nSource:[%s]' % (str(k), str(images)))
        return None


def find_image(image_url=None, referer=None):
    """
    find an image from the link
    """
    if not image_url:
        logger.error('Image URL is not found!')
        return None

    try:
        ni = NormalizedImage(image_url, referer)
        return ni.normalize()
    except Exception as k:
        logger.error('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url)))
        return None


def find_images(self, content=None):
    """
    find out all images from content and its size info
    """
    if not content:
        return None
        """
        if isinstance(images, list):
            images_new = []
            for image in images:
                image_new = _check_image(image)
                if image_new:
                    images_new.append(image_new)
            return images_new if images_new else None
        """
    try:
        # determine the type of content
        if isinstance(content, str) and content.startswith(TRANSCODED_LOCAL_DIR):
            # then its a file
            f = open(content, 'r')
            content = f.read()

        #soup = BeautifulSoup(content.decode('utf-8', 'ignore'))
        soup = BeautifulSoup(str(content))
        images_normalized = []
        images = soup.findAll('img')

        for image in images:
            if image.get('src'):
                image_normalized = get_image(image.get('src'))
                if image_normalized:
                    images_normalized.append(image_normalized)

        return images_normalized
    except Exception as k:
        logger.error(str(k))
        return None


# TODO: relative path could be a url including its suffix like jpg/png
def generate_thumbnail(image_url=None, referer=None, relative_path=None):
    """
    generate a thumbnail
    """
    if not image_url:
        logger.error('Image URL not found!')
        return None
    if not relative_path:
        logger.error('Relative path for saving image not found!')
        return None

    try:
        image_data = None
        try:
            if referer:
                HEADERS['Referer'] = referer
            request = urllib2.Request(image_url, headers=HEADERS)
            response = urllib2.urlopen(request, timeout=UCK_TIMEOUT)
            image_data = Image.open(StringIO(response.read()))
        except Exception as k:
            logger.error('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url)))
            return None

        # generate thumbnail
        if image_data.size > MIN_IMAGE_SIZE:
            # get various paths
            image_thumbnail_local_path = '%s%si.jpg' % (IMAGES_LOCAL_DIR, relative_path)
            image_thumbnail_web_path = '%s%s.jpg' % (IMAGES_PUBLIC_DIR, relative_path)

            # thumbnailing
            image_data.thumbnail(MIN_IMAGE_SIZE, Image.ANTIALIAS)
            image_data = image_data.convert('RGB')
            image_data.save(image_thumbnail_local_path, 'JPEG')
            return image_thumbnail_web_path
        else:
            return image_url
    except Exception as k:
        logger.error('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url)))
        return None


def scale_image(image_url=None, image_size=None, referer=None, size_expected=MIN_IMAGE_SIZE, resize_by_width=True, crop_by_center=True, relative_path=None):
    """
    resize an image as requested
    resize_by_width: resize image according to its width(True)/height(False)
    crop_by_center: crop image from its center(True) or by point(0, 0)(False)
    """
    if not image_url: 
        logger.error('Image URL not found!')
        return None, None
    if not image_size:
        logger.error('Expected image size not found!')
        return None, None
    if not size_expected:
        logger.error('Expected image size not found!')
        return None, None
    if not relative_path:
        logger.error('Relative path for saving image not found!')
        return None, None

    try:
        width = int(image_size[0])
        height = int(image_size[0])
        width_expected = int(size_expected[0])
        height_expected = int(size_expected[1])

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

                image_data = None
                try:
                    if referer:
                        HEADERS['Referer'] = referer
                    request = urllib2.Request(image_url, headers=HEADERS)
                    response = urllib2.urlopen(request, timeout=UCK_TIMEOUT)
                    image_data = Image.open(StringIO(response.read()))
                except Exception as k:
                    logger.info('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url)))
                    return None, None

                # resize image according to new size
                image_data.thumbnail(size_new, Image.ANTIALIAS)

                # crop out unnecessary part
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

                # save to disk
                if image_cropped:
                    image_web_path = '%s%s.jpg' % (IMAGES_PUBLIC_DIR, relative_path)
                    image_local_path = '%s%s.jpg' % (IMAGES_LOCAL_DIR, relative_path)
                    image_cropped = image_cropped.convert('RGB')
                    image_cropped.save(image_local_path, 'JPEG')
                    return {'url': image_web_path, 'width': width_expected, 'height': height_expected}, {'url': image_local_path, 'width': width_expected, 'height': height_expected}
                else:
                    return None, None
            else:
                return scale_image(image_url=image_url, image_size=image_size, referer=referer, size_expected=size_expected, resize_by_width=not resize_by_width, crop_by_center=crop_by_center, relative_path=relative_path)
        else:
            return None, None
    except Exception as k:
        logger.info('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url)))
        return None, None
