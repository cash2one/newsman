#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
daily, clean saved expired files, temporary files and unrecorded files on disk
"""
# @author chengudjin
# @contact chengdujin@gmail.com
# @created Aug. 22, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

import os


def clean_by_item(candidate):
    """
    remove related files on disk of an item
    mp3_local, transcoded_local, hot_news_image_local, category_image_local, thumbnail_image_local
    """
    # mp3
    if candidate.has_key('mp3_local') and candidate['mp3_local']:
        if os.path.exists(candidate['mp3_local']):
            os.remove(candidate['mp3_local'])
    # transcoded
    if candidate.has_key('transcoded_local') and candidate['transcoded_local']:
        if os.path.exists(candidate['transcoded_local']):
            os.remove(candidate['transcoded_local'])
    # hot_news_image
    if candidate.has_key('hot_news_image_local') and candidate['hot_news_image_local']:
        if os.path.exists(candidate['hot_news_image_local']['url']):
            os.remove(candidate['hot_news_image_local']['url'])
    # category_image
    if candidate.has_key('category_image_local') and candidate['category_image_local']:
        if os.path.exists(candidate['category_image_local']['url']):
            os.remove(candidate['category_image_local']['url'])
    # thumbnail_image
    if candidate.has_key('thumbnail_image_local') and candidate['thumbnail_image_local']:
        if os.path.exists(candidate['thumbnail_image_local']['url']):
            os.remove(candidate['thumbnail_image_local']['url'])


def clean():
    """
    """
    pass


if __name__ == "__main__":
    clean()

