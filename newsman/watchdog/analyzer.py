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
import Queue
from spider import scraper
import threading

# CONSTANTS
from config.settings import FEED_REGISTRAR
queue = Queue.Queue()


class UpdateThread(threading.Thread):

    """
    Update news rss/twitter ...
    """

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                feed_id = self.queue.get()
                updated_feed = scraper.update(feed_id=feed_id)
                if updated_feed:
                    logger.error(
                        '--------------- %s got updated! ---------------' % updated_feed)
                self.queue.task_done()
            except Exception as k:
                logger.error(str(k))
                continue


def _update(feed_ids):
    """
    update links find in feeds
    """
    if not feed_ids:
        logger.error("No feed found!")
        return None

    for i in range(5):
        thread = UpdateThread(queue)
        thread.setDaemon(True)
        thread.start()

    # populate queue with feeds
    for feed_id in feed_ids:
        queue.put(feed_id)

    queue.join()


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
    logger.error('############### scraping ###############')
    _update(_read_feeds(language, country))
    logger.error(
        "############### Feeds of %s.%s all got updated! ###############" %
        (country, language))


if __name__ == "__main__":
    language = sys.argv[1]
    country = sys.argv[2]
    _scrape(language, country)
