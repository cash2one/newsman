#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#@author Yuan JIN
#@contact jinyuan@baidu.com
#@created Jan 1, 2013
#
#@updated Jan 17, 2013
#
# TODO
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

from BeautifulSoup import BeautifulStoneSoup
from config import Collection
from config import db
import entry
import feedparser
from config import rclient
import task
import time

from config import FEED_REGISTRAR
from config import LANGUAGES


def create_language_collection(feed_info=None):
    ''''''
    if not feed_info:
        return 1
    if feed_info['language'] not in db.collection_names():
        col = db.create_collection(feed_info['language'])
    return 0

def register_source(feed_info=None):
    ''''''
    if not feed_info:
        return 1
    col = None
    if FEED_REGISTRAR not in db.collection_names():
        col = db.create_collection(FEED_REGISTRAR)
    else:
        col = Collection(db, FEED_REGISTRAR)
    # make a record in the feeds table
    item = col.find_one({'feed_link':feed_info['feed_link']})
    if not item:
        col.save(feed_info)
    return 0

def read_source(d=None, source_address=None, language=None, category=None, weight_category=10, weight_source=10):
    feed_info = {}
    if 'feed' in d:
        if 'title' in d.feed:
            feed_info['feed_name'] = d.feed.title.strip()
        else:
            feed_info['feed_name'] = raw_input('Cannot find name for %s, input new:\n' % source_address).strip()
        if 'subtitle' in d.feed:
            feed_info['subtitle'] = d.feed.subtitle.strip()
        if 'rights' in d.feed:
            feed_info['rights'] = d.feed.rights.strip()
        #if 'image' in d.feed:
        #    feed_info['image'] = d.feed.image.href
    else:
        feed_info['feed_name'] = raw_input('Invalid format of %s, input name:\n' % source_address).strip()
    # read in passed values
    feed_info['feed_link'] = source_address
    feed_info['category'] = category
    feed_info['language'] = language
    feed_info['weight_category'] = weight_category
    feed_info['weight_source'] = weight_source
    return feed_info

def add_feed(source_address=None, language=None, category=None, weight_category=10, weight_source=10):
    '''read rss/atom information from a given feed'''
    if not source_address or not language or not category:
        return 1
    source_address = source_address.strip()
    language = language.strip()
    category = category.strip()
    if language not in LANGUAGES:
        return 2
    if category.count(' '):
        return 3

    d = feedparser.parse(source_address)
    if d:
        # feed level
        feed_info = read_source(d, source_address, language, category, weight_category, weight_source)
        register_source(feed_info)
        create_language_collection(feed_info)
        print '1/4 .. created entry in database'

        # add entries of this feed
        entry.add_entries(feed_info['feed_name'], feed_info['feed_link'], feed_info['language'], feed_info['category']) 
        print '2/4 .. added all rss entries'

        # add weights to memory
        if not rclient.hexists('%s-weights' % feed_info['language'], feed_info['category']):
            language_weights = {feed_info['category']:feed_info['weight_category']}
            rclient.hmset('%s-weights' % feed_info['language'], language_weights)
        if not rclient.hexists('%s-%s-weights' % (feed_info['language'], feed_info['category']), feed_info['feed_name']):
            category_weights = {feed_info['feed_name']:feed_info['weight_source']}
            rclient.hmset('%s-%s-weights' % (feed_info['language'], feed_info['category']), category_weights)
        print '3/4 .. updated memory structure'

        # add to update list
        task.add_task(feed_info['feed_name'], feed_info['feed_link'], feed_info['language'], feed_info['category'])
        print '4/4 .. added to task list'
        return 0
    else:
        return 4

def remove_feed(collection_name=None, source_name=None):
    ''''''
    if not collection_name or not source_name:
        return 1
    else:
        task.remove_task(source_name)
        rclient.hdel(collection_name, source_name)
        entry.remove_entries(collection_name, source_name)
        col = Collection(db, FEED_REGISTRAR)
        col.remove({'source_name':source_name})
        return 0
