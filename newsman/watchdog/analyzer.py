#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
scrape is a task to scrape rss resources
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 14, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('/home/ubuntu/newsman/newsman')

from config import Collection, db
from config import logger
from scraper import rss

# CONSTANTS
from config import FEED_REGISTRAR


def _update(feed_ids):
    """
    update links find in feeds
    """
    if not feed_ids:
        logger.error("No feed found!")
        return None

    try:
        for feed_id in feed_ids:
            updated = rss.update(feed_id=feed_id)
            if not updated:
                logger.error('Nothing got updated from %s' % feed_id)
            else:
                logger.warning('%s got updated' % feed_id)
    except Exception as k:
        pass
        logger.error(str(k))
        return None


def _read_feeds(language='en'):
    """
    read feed information from database feeds
    """
    try:
        db_feeds = Collection(db, FEED_REGISTRAR)
        items = db_feeds.find({'language': language})
        if items:
            return [str(item['_id']) for item in items]
        else:
            logger.error("Cannot find any feeds for language %s!" % language)
            return None
    except Exception as k:
        pass
        logger.error(str(k))
        return None


def _scrape(language):
    """
    update news from stored feeds
    """
    logger.info('----------------------scraping-------------------------')
    _update(_read_feeds(language))


if __name__ == "__main__":
    language = sys.argv[1]
    _scrape(language)
