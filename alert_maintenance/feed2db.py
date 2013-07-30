#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# feed2db works to turn text-based feed list into database
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jul. 30, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from administration.config import Collection
from administration.config import db
from administration.config import FEED_REGISTRAR
from administration.config import CATEGORY_REGISTRAR

file_suffix = '/home/jinyuan/Downloads/global-mobile-news/alert_maintenance/maintenance/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    if line:
        task = line.split('*|*')
        # task[1] refers to categories
        return task[0], task[1].split(','), task[2], task[3]
    else:
        return None


def _convert(language='en'):
    """
    turn text-based feed infor into database items
    """
    # read in file content
    feeds_list = open('%s%s_feeds_list.txt' % (file_suffix, language), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    # open datbase
    db_feeds = Collection(db, FEED_REGISTRAR)
    db_categories = Collection(db, CATEGORY_REGISTRAR)

    for line in lines:
        if line.strip():
            language, categories, feed_title, feed_link = _parse_task(line)
            # save categories
            category_ids = []
            for category in categories:
                item = db_categories.find_one({'name':category, 'language':language})
                if item:
                    category_ids.append(str(item['_id']))
                else:
                    category_id = db_categories.save({'name':category, 'language':language})
                    category_ids.append(category_id)
            # save feed
            db_feeds.save({'language':language, 'feed_link':feed_link, 'categories':category_ids, 'feed_title':feed_title})
