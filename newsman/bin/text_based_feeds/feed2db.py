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
FILE_PREFIX = '/home/work/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/ubuntu/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds/feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    line = line.strip()
    if line:
        task = line.strip().split('*|*')
        # task[1] refers to categories
        if len(task) == 6:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[3].strip(), task[4].strip(), task[5].strip(), None
        elif len(task) == 7:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[3].strip(), task[4].strip(), task[5].strip(), task[6].strip()
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
    db_id_list = open('db_id_list', 'a')

    for line in lines:
        if line.strip():
            language, category, transcoder, feed_link, feed_title, feed_image, labels = _parse_task(line)
            if feed_link:
                category = '%s::%s' % (country, category)

                # break labels
                if labels:
                    labels = ['%s::%s' % (category, label.strip()) for label in labels.split(',')]

                print feed_link

                existing_item = db_feeds.find_one({'feed_link':feed_link})
                if not existing_item:
                    _id = db_feeds.save({'language': language, 'countries':[country], 'feed_link': feed_link, 'categories': [category], 'labels':labels, 'feed_title': feed_title, 'latest_update': None, 'updated_times': 0, 'transcoder': transcoder, 'image':feed_image})
                    db_id_list.write(str(_id) + '\n')
                else:
                    new_item = existing_item
                    new_item['language'] = language
                    
                    if 'categories' in existing_item and existing_item['categories'] and category:
                        existing_item['categories'].append(category)
                        new_item['categories'] = list(set(existing_item['categories']))
                    else:
                        new_item['categories'] = [category]

                    if 'labels' in existing_item and existing_item['labels'] and labels:
                        existing_item['labels'].extend(labels)
                        new_item['labels'] = list(set(existing_item['labels']))
                    else:
                        new_item['labels'] = labels

                    existing_item['countries'].extend([country])
                    new_item['countries'] = list(set(existing_item['countries']))

                    new_item['transcoder'] = transcoder
                    new_item['feed_title'] = feed_title
                    new_item['image'] = feed_image
                    db_feeds.update({'_id': existing_item['_id']}, new_item)
                    db_id_list.write(str(existing_item['_id']) + '\n')
            else:
                continue
        else:
            continue
    db_id_list.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _convert(sys.argv[1], sys.argv[2])
    else:
        print 'Please indicate a language and country'
