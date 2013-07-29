#!/usr/bin/python
# -*- coding: utf-8 -*-

# feed works to get feed meta info into database
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jan 1, 2013

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from administration.config import Collection
from administration.config import db
from administration.config import rclient
from BeautifulSoup import BeautifulStoneSoup
import entry
import feedparser
import task
import time

from administration.config import FEED_REGISTRAR
from administration.config import LANGUAGES


def create_language_collection(feed_info=None):
    ''''''
    if not feed_info:
        return None
    if feed_info['language'] not in db.collection_names():
        feed_id = db.create_collection(feed_info['language'])
        return feed_id
    return None

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

def _read_source(d=None, feed_link=None, language=None, categories=None, weight_categories=10, weight_source=10):
    feed_info = {}
    if 'feed' in d:
        if 'title' in d.feed:
            feed_info['feed_name'] = d.feed.title.strip()
        else:
            feed_info['feed_name'] = raw_input('Cannot find name for %s, input new:\n' % feed_link).strip()
        if 'subtitle' in d.feed:
            feed_info['subtitle'] = d.feed.subtitle.strip()
        if 'rights' in d.feed:
            feed_info['rights'] = d.feed.rights.strip()
        #if 'image' in d.feed:
        #    feed_info['image'] = d.feed.image.href
    else:
        feed_info['feed_name'] = raw_input('Invalid format of %s, input name:\n' % feed_link).strip()
    # read in passed values
    feed_info['feed_link'] = feed_link
    feed_info['categories'] = categories
    feed_info['language'] = language
    feed_info['weight_categories'] = weight_categories
    feed_info['weight_source'] = weight_source
    return feed_info


def add(feed_link=None, language=None, categories=None):
    """
    read rss/atom meta information from a given feed
    """
    if not feed_link or not language:
        return 1
    feed_link = feed_link.strip()
    language = language.strip()
    categories = categories.strip()

    d = feedparser.parse(feed_link)
    if d:
        # feed level
        feed_info = _read_source(d, feed_link, language, categories, weight_categories, weight_source)
        register_source(feed_info)
        feed_id = create_language_collection(feed_info)
        print '1/4 .. created entry in database'
        # ToDos
        # add feed_id checking procedure

        # add entries of this feed
        entry.add_entries(feed_id, feed_info['feed_link'], feed_info['language'], feed_info['categories']) 
        print '2/4 .. added all rss entries'

        # add weights to memory
        if not rclient.hexists('%s-weights' % feed_info['language'], feed_info['categories']):
            language_weights = {feed_info['categories']:feed_info['weight_categories']}
            rclient.hmset('%s-weights' % feed_info['language'], language_weights)
        if not rclient.hexists('%s-%s-weights' % (feed_info['language'], feed_info['categories']), feed_id):
            categories_weights = {feed_id:feed_info['weight_source']}
            rclient.hmset('%s-%s-weights' % (feed_info['language'], feed_info['categories']), categories_weights)
        print '3/4 .. updated memory structure'

        # add to update list
        task.add_task(feed_id, feed_info['feed_link'], feed_info['language'], feed_info['categories'])
        print '4/4 .. added to task list'
        return 0
    else:
        return 4
