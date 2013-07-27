#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# image_scraper is used to find all images from
# a web page
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jul. 23, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulSoup
from administration.config import THUMBNAIL_SIZE
from administration.config import TRANSCODED_LOCAL_DIR

def find_images(content):
    """
    find out all images and its size info
    """
    if not content:
        return None

    # determine the type of content
    if content.startswith(TRANSCODED_LOCAL_DIR):
        # then its a file
        f = open(content, 'r')
        content = f.read()
    
    soup = BeautifulSoup(content.decode('utf-8'))
    images_new = []
    if soup.img:
        if soup.img.get('src'):
            image_paths = soup.img['src']
            if isinstance(image_paths, str):
                try:
                    if not thumbnail.is_valid_image(image_paths):
                        width, height = thumbnail.get_image_size(image_paths)
                        images_new.append({'url': image_paths, 'width': width, 'height': height})
                except IOError as k:
                    print k
            elif isinstance(image_paths, list):
                for image_path in image_paths:
                    try:
                        if not thumbnail.is_valid_image(image_path):
                            width, height = thumbnail.get_image_size(image_path)
                            image = {'url': image_path, 'width': width, 'height': height}
                            images_new.append(image)
                    except IOError as k:
                        print k
    return images_new


def find_biggest_image(images):
    """
    find the biggest in size from a pile of images
    """
    if not images:
        return None
    
    biggest = None
    for current, image in enumerate(images):
        size_max = 0, 0
        size_current = image['width'], image['height']
        if size_current > size_max:
            biggest = current
            size_max = size_current
    return biggest 


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
            raise Exception('ERROR: Method not well formed!')

        if thumbnail.is_valid_image(image):
            width, height = thumbnail.get_image_size(image)
            return {'url':image, 'width':widht, 'height':height}
        else:
            return None

    if isinstance(images, str):
        image = _check_image(images)
        return image
    elif isinstance(images, list):
        images_new = []
        for image in images:
            image_new = _check_image(image)
            if image_new:
                images_new.append(image_new)
        return images_new if images_new else None
