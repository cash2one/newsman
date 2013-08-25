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
sys.path.append('../..')

from config import Collection
from config import db

# CONSTANTS
from config import FEED_REGISTRAR
#FILE_SUFFIX = '/home/work/newsman/newsman/tools/text_based_feeds/feed_lists/'
#FILE_SUFFIX = '/home/ubuntu/newsman/newsman/tools/text_based_feeds/feed_lists/'
FILE_SUFFIX = '/home/jinyuan/Downloads/newsman/newsman/tools/text_based_feeds/feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    if line:
        task = line.split('*|*')
        # task[1] refers to categories
        return task[0].strip(), task[1].split(','), task[2].strip(), task[3].strip()
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

    for line in lines:
        if line.strip():
            language, categories, feed_x, feed_link = _parse_task(line)
            # save feed
            if feed_x in ['chengdujin', 'readability', 'uck']:
                transcoder_mode = feed_x
                feed_title = ""
            else:
                transcoder_mode = "readability"
                feed_title = feed_x
            print feed_link, transcoder_mode
            db_feeds.save({'language': language, 'feed_link': feed_link,
                           'categories': categories, 'feed_title': feed_title,
                           'latest_update': None, 'updated_times': 0,
                           'transcoder': transcoder_mode})


if __name__ == "__main__":
    if len(sys.argv) > 0:
        _convert(sys.argv[1])
    else:
        print 'Please indicate a language'
