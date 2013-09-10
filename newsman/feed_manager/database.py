#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database works to manage interaction with the feed database
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 29, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from bson.objectid import ObjectId
from config.settings import Collection, db
from config.settings import logger
import time

# CONSTANTS
from config.settings import FEED_REGISTRAR


def get(feed_id=None, feed_link=None, language=None):
    """
    get all feed info in database:feeds
    """
    if not feed_id and not (feed_link and language):
        logger.error('Method malformed!')
        return None

    try:
        col = Collection(db, FEED_REGISTRAR)
        if feed_id:
            item = col.find_one({'_id': ObjectId(feed_id)})
        else:
            item = col.find_one({'feed_link': feed_link, 'language': language})
        # the final return
        return item
    except Exception as k:
        logger.error(str(k))
        return None


def update(feed_id, **kwargs):
    """
    update feed info
    """
    if not feed_id:
        logger.error('Method malformed!')
        return None

    try:
        col = Collection(db, FEED_REGISTRAR)
        item = col.find_one({'_id': ObjectId(feed_id)})
        if item:
            # import new things into existing items
            if kwargs:
                item.update(kwargs)

            # only update the following two if update happens
            if 'reason' in item and item['reason'] and item['reason'] == 'OK':
                item['updated_times'] = int(item['updated_times']) + 1
                item['latest_update'] = time.asctime(time.gmtime())

            # the final return
            # by default update returns null upon successful update
            # use find_and_modify if a return is needed
            col.update({'_id': ObjectId(feed_id)}, item)
            return True
        else:
            logger.error("No such a _id %s in feeds" % feed_id)
            return None
    except Exception as k:
        logger.error(str(k))
        return None


def save(feed_info=None):
    """
    add a new record of feed
    """
    if not feed_info:
        logger.error("Method malformed!")
        return None

    try:
        # if the collection does not exist, it will be created
        col = Collection(db, FEED_REGISTRAR)
        # make a record in the feeds table
        item = col.find_one(
            {'feed_link': feed_info['feed_link'], 'language': feed_info['language']})
        if not item:
            feed_info['updated_times'] = 0
            feed_info['latest_update'] = None
            # the final return
            return str(col.save(feed_info))
        else:
            # the final return
            return str(item['_id'])
    except Exception as k:
        logger.error(str(k))
        return None
