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

from administration import database as db_feeds
from BeautifulSoup import BeautifulStoneSoup
import feedparser
from scraper import rss
import task
import time

from administration.config import FEED_REGISTRAR
from administration.config import LANGUAGES


def _read_source(d=None, feed_link=None, language=None, categories=None):
    """
    parse the feed for meta information
    """
    if 'feed' in d:
        feed_info = {}
        # read in passed values
        feed_info['feed_link'] = feed_link
        feed_info['categories'] = categories
        feed_info['language'] = language

        if 'title' in d.feed:
            feed_info['feed_title'] = d.feed.title.strip()
        if 'status' in d:
            feed_info['status'] = d.status
        if 'rights' in d.feed:
            feed_info['rights'] = d.feed.rights.strip()
        if 'etag' in d:
            feed_info['etag'] = d.feed.etag.strip()
        if 'modified' in d:
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
        feed_id = db_feeds.insert_feed(feed_info)
        # add entries of this feed
        rss.update(str(feed_id), feed_info['feed_link'], feed_info['language'], feed_info['categories']) 
    else:
        raise Exception("ERROR: RSS source %s cannot be interpreted!" % feed_link)
        
