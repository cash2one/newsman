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

def find_images(content):
    """
    docs needed!
    """
    if not content:
        return None

    soup = BeautifulSoup(content.decode('utf-8'))
    images_new = []
    if soup.img:
        if soup.img.get('src'):
            image_paths = soup.img['src']
            if isinstance(image_paths, str):
                try:
                    if not thumbnail.is_thumbnail(image_paths):
                        width, height = thumbnail.get_image_size(image_paths)
                        images_new.append({'url': image_paths, 'width': width, 'height': height})
                except IOError as k:
                    print k
            elif isinstance(image_paths, list):
                for image_path in image_paths:
                    try:
                        if not thumbnail.is_thumbnail(image_path):
                            width, height = thumbnail.get_image_size(image_path)
                            image = {'url': image_path, 'width': width, 'height': height}
                            images_new.append(image)
                    except IOError as k:
                        print k
    return images_new
