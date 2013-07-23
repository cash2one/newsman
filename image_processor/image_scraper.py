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


def find_big_images(content):
    ''''''
    if not content:
        return None
    soup = BeautifulSoup(content.decode('utf-8'))
    images = []
    for img in soup.findAll('img'):
        # filter out thumbnails
        try:
            image = img['src']
            if image.endswith('.jpg') or image.endswith('.JPG') or image.endswith('.jpeg') or image.endswith('.JPEG') or image.endswith('.png') or image.endswith('.PNG'):
                current_size = thumnail.get_image_size(image)
                if current_size > THUMBNAIL_SIZE:
                    images.append(image)
        except Exception as e:
            pass
    return images

