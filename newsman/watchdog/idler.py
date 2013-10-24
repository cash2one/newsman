#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
idler finds out sources that do not update frequently
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Sept. 03, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append("/home/work/newsman/newsman")
#sys.path.append("/home/jinyuan/Downloads/newsman/newsman")

from config.settings import Collection, db
from config.settings import logger
from datetime import datetime, timedelta
import time

# CONSTANTS
from config.settings import FEED_REGISTRAR
from config.settings import FEED_UPDATE_DAYS


def _find_idler():
    """
    contact feeds database and apply the filter
    """
    try:
        document = Collection(db, FEED_REGISTRAR)
        feeds = document.find(
            {}, {'language': 1, 'latest_update': 1, 'feed_title': 1, 'feed_link': 1, 'reason': 1})
        if feeds:
            for feed in feeds:
                if 'latest_update' in feed and feed['latest_update']:
                    # read string value from database and convert it into unix
                    # time
                    latest_update_time = time.mktime(
                        time.strptime(str(feed['latest_update'])))
                    # change unix time into datetime struct
                    latest_update_datetime = datetime.utcfromtimestamp(
                        latest_update_time)
                    # convert feed_update_days into datetime struct
                    checkpoint_datetime = timedelta(days=FEED_UPDATE_DAYS)
                    # compute feed update deadline in datetime struct
                    feed_deadline_datetime = latest_update_datetime + \
                        checkpoint_datetime
                    # convert feed update deadline back to unix time
                    feed_deadline_time = time.mktime(
                        feed_deadline_datetime.utctimetuple())

                    # compute time now in unix
                    now_time = time.mktime(time.gmtime())

                    # compare feed_deadline with now
                    # feed was updated correctly
                    if feed_deadline_time > now_time:
                        pass
                    else:
                        if 'feed_title' in feed and feed['feed_title']:
                            if 'reason' in feed and feed['reason']:
                                logger.error('%s %s (%s) has no updates in %s days! Reason: %s' % (
                                    feed['language'], feed['feed_title'], feed['feed_link'], FEED_UPDATE_DAYS, feed['reason']))
                            else:
                                logger.error('%s %s (%s) has no updates in %s days!' % (
                                    feed['language'], feed['feed_title'], feed['feed_link'], FEED_UPDATE_DAYS))
                        else:
                            if 'reason' in feed and feed['reason']:
                                logger.error('%s %s has no updates in %s days! Reason: %s' % (
                                    feed['language'], feed['feed_link'], FEED_UPDATE_DAYS, feed['reason']))
                            else:
                                logger.error('%s %s has no updates in %s days!' % (
                                    feed['language'], feed['feed_link'], FEED_UPDATE_DAYS))
                else:  # nothing found in feed about latest_update
                    if 'feed_title' in feed and feed['feed_title']:
                        if 'reason' in feed and feed['reason']:
                            logger.error('%s %s (%s) has never been updated! Reason: %s' % (
                                feed['language'], feed['feed_title'], feed['feed_link'], feed['reason']))
                        else:
                            logger.error('%s %s (%s) has never been updated!' % (
                                feed['language'], feed['feed_title'], feed['feed_link']))
                    else:
                        if 'reason' in feed and feed['reason']:
                            logger.error(
                                '%s %s has never been updated! Reason: %s' %
                                (feed['language'], feed['feed_link'], feed['reason']))
                        else:
                            logger.error('%s %s has never been updated!' %
                                         (feed['language'], feed['feed_link']))
        else:
            logger.error('Cannot find any feed in %s' % FEED_REGISTRAR)
    except Exception as k:
        logger.error(str(k))


if __name__ == "__main__":
    _find_idler()
