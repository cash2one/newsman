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

def _register_source(feed_info=None):
    ''''''

def _read_source(d=None, feed_link=None, language=None, categories=None):
    if 'feed' in d:
        feed_info = {}
        # read in passed values
        feed_info['feed_link'] = feed_link
        feed_info['categories'] = categories
        feed_info['language'] = language

        if 'title' in d.feed:
            feed_info['feed_title'] = d.feed.title.strip()
        if 'rights' in d.feed:
            feed_info['rights'] = d.feed.rights.strip()
        if 'etag' in d.feed:
            feed_info['etag'] = d.feed.etag.strip()
        if 'modified' in d.feed:
            feed_info['modified'] = d.feed.modified.strip()
        return feed_info
    else:
        raise Exception('ERROR: Feed %s malformed!' % feed_link)


def _link_cleaner(link):
    """
    remove unnecessary parameters and the like
    """
    pass


def add(feed_link=None, language=None, categories=None):
    """
    read rss/atom meta information from a given feed
    """
    if not feed_link or not language:
        raise Exception("ERROR: Method not well formed!")
    
    d = feedparser.parse(feed_link)
    if d:
        # feed level
        feed_info = _read_source(d, feed_link, language, categories)
        _register_source(feed_info)
        feed_id = create_language_collection(feed_info)
        print '1/4 .. created entry in database'
        # ToDos
        # add feed_id checking procedure

        # add entries of this feed
        entry.add_entries(feed_id, feed_info['feed_link'], feed_info['language'], feed_info['categories']) 
        print '2/4 .. added all rss entries'

        # add to update list
        task.add_task(feed_id, feed_info['feed_link'], feed_info['language'], feed_info['categories'])
        print '4/4 .. added to task list'
        return 0
    else:
        return 4
