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
#FILE_PREFIX = '/home/users/jinyuan/newsman/newsman/bin/text_based_feeds
# /feed_lists/'
#FILE_PREFIX = '/home/ubuntu/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds
# /feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    line = line.strip()
    if line:
        task = line.strip().split('*|*')
        # task[1] refers to categories
        if len(task) == 6:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[
                3].strip(), task[4].strip(), task[5].strip(), None
        elif len(task) == 7:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[
                3].strip(), task[4].strip(), task[5].strip(), task[6].strip()
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
    feeds_list = open('%s%s_%s_feeds_list' %
                      (FILE_PREFIX, language, country), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    # open datbase
    db_feeds = Collection(db, FEED_REGISTRAR)
    db_id_list = open('db_id_list', 'a')

    for line in lines:
        if line.strip():
            parser, category_and_order, transcoder, feed_link, feed_title, \
            feed_logo, labels_and_orders = _parse_task(
                line)
            if feed_link:
                category_and_order_splits = category_and_order.split('-->')
                category = category_order = None
                if len(category_and_order_splits) > 1:
                    category = u'%s::%s' % (
                        country, category_and_order_splits[0].strip())
                    category_order = category_and_order_splits[1].strip()
                else:
                    category = u'%s::%s' % (
                        country, category_and_order_splits[0])

                # break labels
                labels = {}
                if labels_and_orders:
                    labels_and_orders_splits = labels_and_orders.split(',')
                    for label_and_order in labels_and_orders_splits:
                        label_and_order_splits = label_and_order.strip().split(
                            '-->')
                        # every label has a label and its order, unlike
                        # category
                        label = u'%s::%s' % (
                            category, label_and_order_splits[0].strip())
                        label_order = label_and_order_splits[1].strip()
                        labels[label] = label_order

                existing_item = db_feeds.find_one({'feed_link': feed_link})
                if not existing_item:
                    feed_logo = {'url': feed_logo, 'width': 71, 'height': 60}
                    _id = db_feeds.save(
                        {'language': language, 'countries': [country],
                         'feed_link': feed_link, 'categories': {
                            category: category_order}, 'labels': labels,
                         'feed_title': feed_title, 'latest_update': None,
                         'updated_times': 0, 'transcoder': transcoder,
                         'feed_logo': feed_logo, 'parser': parser})
                    db_id_list.write(str(_id) + '\n')
                else:
                    existing_item['language'] = language
                    existing_item['parser'] = parser

                    # categories --> {category:order, category:order}
                    if isinstance(existing_item['categories'], list):
                        existing_item['categories'] = {}
                    existing_item['categories'][category] = category_order

                    # labels --> {label:order, label:order}
                    if isinstance(existing_item['labels'], list):
                        existing_item['labels'] = {}
                    if existing_item['labels']:
                        existing_item['labels'] = dict(
                            existing_item['labels'].items() + labels.items())
                    else:
                        existing_item['labels'] = labels

                    existing_item['countries'].extend([country])
                    existing_item['countries'] = list(
                        set(existing_item['countries']))

                    existing_item['transcoder'] = transcoder
                    existing_item['feed_title'] = feed_title
                    existing_item['feed_logo'] = {
                        'url': feed_logo, 'width': 71, 'height': 60}
                    db_feeds.update(
                        {'_id': existing_item['_id']}, existing_item)
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
