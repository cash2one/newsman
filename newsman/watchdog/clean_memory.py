#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
daily work, clean expired items and its place in queues in memory
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 22, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from bson.objectid import ObjectId
from config import Collection, db
from config import rclient
import time
import cleaner


def clean_by_item(item_id):
    """
    remove item-related things in memory
    """
    if not item_id:
        return None
    if not rclient.exists(item_id):
        return None
    # it's possible item_id in queues be visited
    # success returns 1, else 0
    return rclient.delete(item_id)


def _is_zombie(item):
    """
    zombies are items in memory but not in database
    """
    if not item:
        return True

    document_name = item['language']
    document = Collection(db, document_name)
    item_id = ObjectId(item['_id']) 
    found = document.find_one({'_id': item_id})
    if not found:
        return True
    else:
        return False


def clean_by_collection():
    """
    removed a group of expired items in memory
    """
    pass


def clean():
    """
    remove expired items from queues in memory
    walk through all redis content
    """
    print '... cleaning memory ...'
    news_lists = rclient.keys('news::*')
    for news_list in news_lists:
        # get the total number of a news list
        news_list_count = rclient.zcard(news_list)
        # get all the ids in a news list
        if news_list_count:
            news_ids = rclient.zrange(news_list, 0, news_list_count)
            for news_id in news_ids:
                # make sure every item is touched
                if not rclient.exists(news_id):
                    rclient.zrem(news_list, news_id)
                else:
                    news_item_string = rclient.get(news_id)
                    if news_item_string:
                        news_item = eval(news_item_string)
                        news_updated = float(news_item['updated'])
                        
                        if cleaner.is_overdue(news_updated):  # WTF, remove it
                            rclient.zrem(news_list, news_id)
                            rclient.delete(news_id)
                        else:  # check if this is zombie
                            if _is_zombie(news_item):
                                rclient.zrem(news_list, news_id)
                                rclient.delete(news_id)
                    else:
                        rclient.zrem(news_list, news_id)
                        rclient.delete(news_id)
    

if __name__ == "__main__":
    clean()
