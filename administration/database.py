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

from administration.config import FEED_REGISTRAR


def insert_feed(feed_info=None):
    """
    add a new record of feed
    """
    if not feed_info:
        raise Exception("ERROR: Nothing found in feed!")

    col = None
    if FEED_REGISTRAR not in db.collection_names():
        col = db.create_collection(FEED_REGISTRAR)
    else:
        col = Collection(db, FEED_REGISTRAR)
    # make a record in the feeds table
    item = col.find_one({'feed_link':feed_info['feed_link']})
    if not item:
        col.save(feed_info)
    return 0
