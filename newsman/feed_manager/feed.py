#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
feed works to get feed meta info into database
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jan 1, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from config.settings import logger
import database as db_feeds
import feedparser
from scraper import spider
import socket
socket.setdefaulttimeout(10)  # 10 seconds


def _read_source(d=None, feed_link=None, language=None, categories=None):
    """
    parse the feed for meta information
    """
    if not d or not feed_link or not language or not categories:
        logger.error('Method malformed!')
        return None

    try:
        if 'feed' in d:
            feed = {}
            # read in passed values
            feed['feed_link'] = feed_link
            feed['categories'] = categories
            feed['language'] = language

            if 'title' in d.feed:
                feed['feed_title'] = d.feed.title.strip()
            if 'status' in d:
                feed['status'] = d.status
            if 'rights' in d.feed:
                feed['rights'] = d.feed.rights.strip()
            if 'etag' in d:
                feed['etag'] = d.feed.etag.strip()
            if 'modified' in d:
                feed['modified'] = d.feed.modified.strip()
            # the final return
            return feed
        else:
            logger.error('Feed %s is malformed!' % feed_link)
            return None
    except Exception as k:
        logger.error(str(k))
        return None


# TODO: implement _link_cleaner!
def add(feed_link=None, language=None, categories=None, transcoder_type="chengdujin"):
    """
    read rss/atom meta information from a given feed
    """
    if not feed_link or not language:
        logger.error("[feed.add] ERROR: Method not well formed!")
        return None

    try:
        d = feedparser.parse(feed_link)
        if d:
            # feed level
            feed = _read_source(d, feed_link, language, categories)
            if feed:
                feed_id = db_feeds.save(feed)
                if feed_id:
                    # add entries of this feed
                    # the FINAL return
                    return spider.update(feed_link=feed_link, feed_id=feed_id, language=language, categories=categories, transcoder_type=transcoder_type)
                else:
                    logger.error('Cannot save feed in database')
                    return None
            else:
                logger.error('Cannot read source!')
                return None
        else:
            logger.error(
                "RSS source %s cannot be interpreted!" % feed_link)
            return None
    except Exception as k:
        logger.error(str(k))
        return None
