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
import httplib
from PIL import Image
import os
import re
import urllib2
import urlparse

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


class Illustrator:
    """
    Illustrator deals with images
    """

    def __init__(self, image_url=None, image_html=None, image_urls=None):
        if not image_url and not image_urls and not image_html:
            logger.error('Method malformed!')
            raise Exception('Method malformed!')

        if image_url:
            self._image_url = image_url
        elif image_html:
            self._image_html = image_html
        elif image_urls:
            self._image_urls = image_urls
        else:
            logger.error('Unrecognized input type!')
            raise Exception('Unrecognized input type!')

    def _check_image(self, image):
        """
        check an image if it matches with MIN_IMAGE_SIZE
        """
        if not image:
            logger.error('Method malformed!')
            return None

        try:
            if isinstance(image, dict) and 'url' in image:
                image_url = image['url']
                if self._is_valid_image(image_url):
                    width, height = get_image_size(image_url)
                    return {'url': image['url'], 'width': width, 'height': height}
            else:
                if self._is_valid_image(image):
                    width, height = get_image_size(image)
                    if width and height:
                        return {'url': image, 'width': width, 'height': height}
                    else:
                        logger.info('Cannot get image size')
                        return None
            return None
        except IOError as k:
            logger.error(str(k))
            return None

    def find_image(self, link=None):
        """
        find an image from the link
        """
        if not link:
            return None

        try:
            link_clean = _link_process(link)
            if link_clean:
                image_normalized = normalize(link_clean)
                return image_normalized[0] if image_normalized else None
            else:
                logger.info(
                    'Cannot parse [clean %s] [orginal %s] correctly' % (link_clean, link))
                return None
        except Exception as k:
            logger.error(str(k))
            return None

    def find_images(self, content=None):
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

            #soup = BeautifulSoup(content.decode('utf-8', 'ignore'))
            soup = BeautifulSoup(str(content))
            images_normalized = []
            images = soup.findAll('img')

            for image in images:
                if image.get('src'):
                    image_normalized = find_image(image.get('src'))
                    if image_normalized:
                        images_normalized.append(image_normalized)

            return images_normalized
        except Exception as k:
            logger.error(str(k))
            return None

    def get_image_size(self, image_url):
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
                HEADERS['Referer'] = image_url
                request = urllib2.Request(image_url, headers=HEADERS)
                response = urllib2.urlopen(request, timeout=UCK_TIMEOUT)
                image_web = StringIO(response.read())
            else:
                logger.info('image_url is data')
                image_web = image_url

            if image_web:
                im = Image.open(image_web)
                width, height = im.size
                return width, height
            else:
                return None, None
        except Exception as k:
            logger.info('Problem:[%s] Source:[%s]' % (str(k), image_url))
            return None, None

    def _is_valid_image(self, image_url):
        """
        find out if the image has a resolution larger than MIN_IMAGE_SIZE
        """
        if not image_url:
            logger.error('Method malformed! URL [%s] is incorrect' % image_url)
            return False

        try:
            if _url_image_exists(image_url):
                HEADERS['Referer'] = image_url
                request = urllib2.Request(image_url, headers=HEADERS)
                response = urllib2.urlopen(request, timeout=UCK_TIMEOUT)
                image_pil = Image.open(StringIO(response.read()))
                return True if image_pil.size[0] * image_pil.size[1] > MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1] else False
            else:
                logger.info('%s is not an image' % image_url)
                return False
        except Exception as k:
            logger.error('%s [%s]' % (image_url, str(k)))
            return False

    def _link_process(self, link):
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

                # gif is not needed
                if image_url.endswith('.gif') or image_url.endswith('.GIF'):
                    return None

                # response is the signal of a valid image
                response = None
                try:
                    HEADERS['Referer'] = image_url
                    request = urllib2.Request(image_url, headers=HEADERS)
                    response = urllib2.urlopen(request, timeout=UCK_TIMEOUT)
                except urllib2.URLError:
                    path = re.split('https?://?', image_url)[-1]
                    scheme = urlparse.urlparse(image_url).scheme
                    image_url = '%s://%s' % (scheme, path)

                    HEADERS['Referer'] = image_url
                    request = urllib2.Request(image_url, headers=HEADERS)
                    response = urllib2.urlopen(request, timeout=UCK_TIMEOUT)
                except urllib2.HTTPError as k:
                    logger.info('%s for %s' % (str(k), image_url))
                    return None
                except Exception as k:
                    logger.info('%s for %s' % (str(k), image_url))
                    return None

                if response:
                    return image_url
                else:
                    return None
            else:
                return None
        except Exception as k:
            logger.info('Problem:[%s] Source:[%s]' % (str(k), link))
            return None

    def normalize(self, images):
        """
        for list of images, remove images that don't match with MIN_IMAGE_SIZE;
        for an image, return None if it doesn't matches with MIN_IMAGE_SIZE
        """
        try:
            if isinstance(images, list):
                images_new = []
                for image in images:
                    image_new = _check_image(image)
                    if image_new:
                        images_new.append(image_new)
                return images_new if images_new else None
            elif isinstance(images, str) or isinstance(images, unicode):
                image = _check_image(images)
                return [image] if image else None
            return None
        except Exception as k:
            logger.exception(str(k))
            return None

    def _url_image_exists(self, url):
        """
        Code copied from
        http://jackdschultz.com/index.php/2013/09/13/validating-url-as-an-image-in-python/
        Check if the image exists
        """
        if not url:
            logger.error('Method malformed!')
            return False

        try:
            parse_obj = urlparse.urlparse(url)
            site = parse_obj.netloc
            path = parse_obj.path
            conn = httplib.HTTPConnection(site)
            conn.request('HEAD', path)
            response = conn.getresponse()
            conn.close()
            ctype = response.getheader('Content-Type')
            #return response.status < 400 and ctype.startswith('image')
            return response.status < 400 or ctype.startswith('image')
        except Exception as k:
            logger.info(str(k))
            return False


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
        logger.info('Problem:[%s]\nSource:[%s]' % (str(k), str(images))
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
        logger.error('Problem:[%s]\nSource:[%s]' % (str(k), str(images))
        return None


# TODO: relative path could be a url including its suffix like jpg/png
def generate_thumbnail(image_url, referer=None, relative_path):
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
            logger.error'Problem:[%s]\nSource:[%s]' % (str(k), str(image_url))
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
        logger.error('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url))
        return None


def scale_image(image_url=None, image_size=None, referer=None, size_expected=MIN_IMAGE_SIZE, resize_by_width=True, crop_by_center=True, relative_path=None):
    """
    resize an image as requested
    resize_by_width: resize image according to its width(True)/height(False)
    crop_by_center: crop image from its center(True) or by point(0, 0)(False)
    """
    if not image_url 
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
                    logger.info('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url))
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
        logger.info('Problem:[%s]\nSource:[%s]' % (str(k), str(image_url))
        return None, None
