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

    # if the collection does not exist, it will be created
    col = Collection(db, FEED_REGISTRAR)
    # make a record in the feeds table
    item = col.find_one({'feed_link':feed_info['feed_link'], 'language':feed_info['language']})
    if not item:
        return col.save(feed_info)
    else:
        return None
