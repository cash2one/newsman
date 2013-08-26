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
from config import Collection, db
from config import logging
import time

# CONSTANTS
from config import FEED_REGISTRAR


def get(feed_id=None, feed_link=None, language=None):
    """
    get all feed info in database:feeds
    """
    if not feed_id or not (feed_link and language):
        logging.error('Method malformed!')
        return None

    try:
        col = Collection(db, FEED_REGISTRAR)
        if feed_id:
            item = col.find_one({'_id': ObjectId(feed_id)})
        else:
            item = col.find_one({'feed_link': feed_link, 'language': language})
        return item
    except Exception as k:
        logging.exception(str(k))
        return None


def update(feed_id, **kwargs):
    """
    update feed info
    """
    if not feed_id:
        logging.error('Method malformed!')
        return None

    try:
        col = Collection(db, FEED_REGISTRAR)
        item = col.find_one({'_id': ObjectId(feed_id)})
        if item:
            # import new things into existing items
            if kwargs:
                item.update(kwargs)
            item['updated_times'] = int(item['updated_times']) + 1
            item['latest_update'] = time.asctime(time.gmtime())
            col.update({'_id': ObjectId(feed_id)}, item)
        else:
            logging.error("No such a _id %s in feeds" % feed_id)
    except Exception as k:
        logging.exception(str(k))
        return None


def save(feed_info=None):
    """
    add a new record of feed
    """
    if not feed_info:
        logging.exception("Method malformed!")
        return None

    try:
        # if the collection does not exist, it will be created
        col = Collection(db, FEED_REGISTRAR)
        # make a record in the feeds table
        item = col.find_one({'feed_link': feed_info['feed_link'], 'language': feed_info['language']})
        if not item:
            feed_info['updated_times'] = 0
            feed_info['latest_update'] = None
            return str(col.save(feed_info))
        else:
            return str(item['_id'])
    except Exception as k:
        logging.exception(str(k))
        return None
