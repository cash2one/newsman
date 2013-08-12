#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
feed2db works to turn text-based feed list into database
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 30, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from config import Collection
from config import db

# CONSTANTS
from config import FEED_REGISTRAR
from config import CATEGORY_REGISTRAR
#FILE_SUFFIX = '/home/work/bgm_news/tools/text_based_feeds/feed_lists/'
FILE_SUFFIX = '/home/jinyuan/Downloads/bgm_news/tools/\
        text_based_feeds/feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    if line:
        task = line.split('*|*')
        # task[1] refers to categories
        return task[0].strip(), task[1].split(','), \
            task[2].strip(), task[3].strip()
    else:
        return None


def _convert(language='en'):
    """
    turn text-based feed infor into database items
    """
    # read in file content
    feeds_list = open('%s%s_feeds_list.txt' % (FILE_SUFFIX, language), 'r')
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
                item = db_categories.find_one(
                    {'name': category, 'language': language})
                if item:
                    category_ids.append(str(item['_id']))
                else:
                    category_id = db_categories.save(
                        {'name': category, 'language': language})
                    category_ids.append(str(category_id))
            # save feed
            db_feeds.save({'language': language, 'feed_link': feed_link,
                           'categories': category_ids, 'feed_title': feed_title,
                           'latest_update': None, 'updated_times': 0,
                           'transcoder': 'chengdujin'})


if __name__ == "__main__":
    if len(sys.argv) > 0:
        _convert(sys.argv[1])
    else:
        print 'Please indicate a language'
