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
# sys.path.append('/home/work/newsman/newsman')
# sys.path.append('/home/users/jinyuan/newsman/newsman')
# sys.path.append('/home/ubuntu/newsman/newsman')
# sys.path.append('/home/jinyuan/Downloads/newsman/newsman')

from config.settings import Collection, db
from config.settings import logger
from spider import scraper

# CONSTANTS
from config.settings import FEED_REGISTRAR


def _update(feed_ids):
    """
    update links find in feeds
    """
    if not feed_ids:
        logger.error("No feed found!")
        return None

    try:
        for index, feed_id in enumerate(feed_ids):
            updated = scraper.update(feed_id=feed_id)
            logger.info('=============== %s of %s updated ===============' %
                        (str(index + 1), str(len(feed_ids))))
            if not updated:
                logger.info('Nothing got updated from %s' % feed_id)
            else:
                logger.info('%s got updated' % feed_id)
    except Exception as k:
        logger.error(str(k))
        return None


def _read_feeds(language='en', country='US'):
    """
    read feed information from database feeds
    """
    try:
        db_feeds = Collection(db, FEED_REGISTRAR)
        items = db_feeds.find({'language': language, 'countries': country})
        if items:
            return [str(item['_id']) for item in items]
        else:
            logger.error("Cannot find any feeds for language %s!" % language)
            return None
    except Exception as k:
        logger.error(str(k))
        return None


def _scrape(language='en', country='US'):
    """
    update news from stored feeds
    """
    logger.info('############### scraping ###############')
    _update(_read_feeds(language, country))


if __name__ == "__main__":
    language = sys.argv[1]
    country = sys.argv[2]
    _scrape(language, country)
