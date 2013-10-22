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

from config.settings import Collection
from config.settings import db

# CONSTANTS
from config.settings import FEED_REGISTRAR
#FILE_PREFIX = '/home/work/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/ubuntu/newsman/newsman/bin/text_based_feeds/feed_lists/'
FILE_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds/feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    line = line.strip()
    if line:
        task = line.strip().split('*|*')
        # task[1] refers to categories
        if len(task) == 5:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[3].strip(), task[4].strip(), None
        elif len(task) == 6:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[3].strip(), task[4].strip(), task[5].strip()
        else:
            return None
    else:
        return None


def _convert(language='en', country=None):
    """
    turn text-based feed infor into database items
    Note. 1. categories: [(), ()]
    """
    # read in file content
    feeds_list = open('%s%s_%s_feeds_list' % (FILE_PREFIX, language, country), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    # open datbase
    db_feeds = Collection(db, FEED_REGISTRAR)

    for line in lines:
        if line.strip():
            language, category, transcoder, feed_link, feed_title, labels = _parse_task(line)
            if feed_link:
                category = '%s::%s' % (country, category)

                # break labels
                if labels:
                    labels = ['%s::%s' % (category, label.strip()) for label in labels.split(',')]

                print feed_title, labels

                existing_item = db_feeds.find_one({'link':feed_link})
                if not existing_item:
                    db_feeds.save({'language': language, 'countries':[country], 'feed_link': feed_link, 'categories': [category], 'labels':labels, 'feed_title': feed_title, 'latest_update': None, 'updated_times': 0, 'transcoder': transcoder})
                else:
                    new_item = existing_item
                    new_item['language'] = language
                    new_item['categories'] = list(set(new_item['categories'].extend([category])))
                    new_item['labels'] = list(set(new_item['labels'].extend(labels)))
                    new_item['countries'] = list(set(new_item['countries'].append(country)))
                    new_item['transcoder'] = transcoder
                    new_item['feed_title'] = feed_title
                    db_feeds.update({'_id': item['_id']}, new_item)
            else:
                continue
        else:
            continue


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _convert(sys.argv[1], sys.argv[2])
    else:
        print 'Please indicate a language and country'
