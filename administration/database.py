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

from administration.config import FEED_REGISTRAR


def get(feed_id):
    """
    get all feed info in database:feeds
    """
    col = Collection(db, FEED_REGISTRAR)
    item = col.find_one({'_id':ObjectId(feed_id)})
    return item


def update(feed_id, **kwargs):
    """
    update feed info
    """
    col = Collection(db, FEED_REGISTRAR)
    item = col.find_one({'_id': ObjectId(feed_id)})
    if item:
        col.update({'_id':ObjectId(feed_id)}, kwargs)
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
        return col.save(feed_info)
    else:
        return None
