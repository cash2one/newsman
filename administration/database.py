#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# database works to manage interaction with the feed database
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jul. 29, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from administration.config import Collection
from administration.config import db
from bson.objectid import ObjectId
import time

from administration.config import FEED_REGISTRAR


def get(feed_id=None, feed_link=None, language=None):
    """
    get all feed info in database:feeds
    """
    col = Collection(db, FEED_REGISTRAR)
    if feed_id:
        item = col.find_one({'_id':ObjectId(feed_id)})
    else:
        item = col.find_one({'feed_link':feed_link, 'language':language})
    return item


def update(feed_id, **kwargs):
    """
    update feed info
    """
    col = Collection(db, FEED_REGISTRAR)
    item = col.find_one({'_id': ObjectId(feed_id)})
    if item:
        # import new things into existing items
        if kwargs:
            item.update(kwargs)
        item['updated_times'] = int(item['updated_times']) + 1
        item['latest_update'] = time.asctime(time.gmtime())
        col.update({'_id':ObjectId(feed_id)}, item)
    else:
        raise Exception("ERROR: No such a _id %s in feeds" % feed_id)


def save(feed_info=None):
    """
    add a new record of feed
    """
    if not feed_info:
        raise Exception("ERROR: Nothing found in feed!")

    # if the collection does not exist, it will be created
    col = Collection(db, FEED_REGISTRAR)
    # make a record in the feeds table
    item = col.find_one({'feed_link':feed_info['feed_link'], 'language':feed_info['language']})
    if not item:
        feed_info['updated_times'] = 0
        feed_info['latest_update'] = None
        return str(col.save(feed_info))
    else:
        return None
