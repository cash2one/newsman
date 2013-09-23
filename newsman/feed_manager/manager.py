#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
Feed management supports operations like Insert, Modify and Remove on the 
level of an RSS feed, a label and a category
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Sept. 23, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from config.settings import Collection, db
from config.settings import rclient

# CONSTANTS
from config.settings import FEED_REGISTRAR


def add_feed_to_label(language=None, feed=None, label=None):
    """
    Ad hoc add a feed to label. This mainly deals with history data
    """
    pass


def add_label(language=None, label=None):
    """
    Ad hoc add a label. This mainly deals with history data
    """
    pass


def remove_feed_from_label(language=None, feed=None, label=None):
    """
    Remove a feed from a label
    """
    if not language or not feed or not label:
        return None

    # remove member in label sequence in memory regarding the feed
    label_name_in_memory = 'news::%s::%s' % (language, label)
    if rclient.exists(label_name_in_memory):
        label_total_in_memory = rclient.zcard(label_name_in_memory)
        ids_with_label = rclient.zrevrange(label_name_in_memory, 0, label_total_in_memory) 
        for id_with_label in ids_with_label:
            item = eval(rclient.get(id_with_label))
            if item['feed'] == feed:
                rclient.zrem(id_with_label)

    # remove label in feed
    feeds = Collection(db, FEED_REGISTRAR)
    item = feeds.find_one({'feed_title':feed, 'labels':label})
    if item:
        item['labels'].remove(label)
        feeds.update({'_id':item['_id']}, item)
        return 'OK'

    return None


def remove_label(language=None, label=None):
    """
    Remove a label from memory and database
    Note. label should be country::category::label-like
    """

    if not language or not label:
        return None

    label_name_in_memory = 'news::%s::%s' % (language, label)
    if rclient.exists(label_name_in_memory):
        label_total_in_memory = rclient.zcard(label_name_in_memory)
        # remove sequence in label_name_in_memory
        rclient.zremrangebyrank(label_name_in_memory, 0, label_total_in_memory)
        # remove the key
        rclient.delete(label_name_in_memory)

    # operate on database with or without memory
    feeds = Collection(db, FEED_REGISTRAR) 
    items = feeds.find({'labels':label})
    if items:
        for item in items:
            new_item = item
            _id = item['_id']
            labels = item['labels']
            labels.remove(label)
            new_item['labels'] = labels
            feeds.update({'_id':_id}, new_item)
        return 'OK'
    return None


def update_label(language=None, label=None):
    """
    If some feed in lable change name, call this one
    """
    if not language or not label:
        return None

    label_name_in_memory = 'news::%s::%s' % (language, label)


if __name__ == '__main__':
    pass
