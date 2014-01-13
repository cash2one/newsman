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
sys.path.append('/home/work/newsman/newsman')

from analyzer import scraper
from config.settings import Collection, db
from config.settings import logger
import Queue
import threading
import time

# CONSTANTS
from config.settings import FEED_REGISTRAR
from config.settings import FEED_UPDATE_TIMEOUT


class TimeoutQueue(Queue.Queue):

    """
    Synchronized Queue with timeout feature
    """

    def __init__(self):
        Queue.Queue.__init__(self)

    def join_with_timeout(self, timeout):
        self.all_tasks_done.acquire()
        try:
            endtime = time.time() + timeout
            while self.unfinished_tasks:
                remaining = endtime - time.time()
                if remaining <= 0.0:
                    raise Exception('[%s] unfinished items [%s]' %
                                    (str(self.unfinished_tasks), str(self.queue)))
                self.all_tasks_done.wait(remaining)
        finally:
            self.all_tasks_done.release()


class UpdateThread(threading.Thread):

    """
    Update news rss/twitter ...
    """

    def __init__(self, name):
        threading.Thread.__init__(self)
        self._name = name

    def run(self):
        while True:
            try:
                feed_id = queue.get()
                updated_feed = scraper.update(feed_id=feed_id)
                if updated_feed:
                    logger.warning(
                        '%s: %s [%s] is successfully updated!' % (self._name, feed_id, updated_feed))
                else:
                    logger.warning(
                        '%s: %s receives no update!' % (self._name, feed_id))
                queue.task_done()
            except Exception as k:
                logger.error(
                    '%s: [%s] receives no update but exception' % (self._name, str(k)))
                queue.task_done()


# synchronized queue that supports timeout
queue = TimeoutQueue()


def _update(feed_ids):
    """
    update links find in feeds
    """
    if not feed_ids:
        logger.error("No feed found!")
        return None

    # populate queue with feeds
    for feed_id in feed_ids:
        queue.put(feed_id)

    thread_limit = min(len(feed_ids) / 2, 10)
    for i in range(thread_limit):
        thread = UpdateThread('Thread-%i' % i)
        thread.setDaemon(True)
        thread.start()

    try:
        # updating timeout set to 1.5 hours
        queue.join_with_timeout(FEED_UPDATE_TIMEOUT)
    except Exception as k:
        logger.error(str(k))


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
    logger.warning('############### Scraping begins ###############')
    _update(_read_feeds(language, country))
    logger.warning(
        "############### Feeds of %s_%s all got updated! ###############" %
        (language, country))


if __name__ == "__main__":
    language = sys.argv[1]
    country = sys.argv[2]
    _scrape(language, country)
