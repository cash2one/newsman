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
    images = []
    for img_tag in soup.findAll('img'):
        # filter out thumbnails
        try:
            image = img_tag['src']
            # when opening an image, Image will tell if it is a valid image.
            current_size = thumnail.get_image_size(image)
            if current_size > THUMBNAIL_SIZE:
                images.append(image)
        except IOError as e:
            pass
    return images
