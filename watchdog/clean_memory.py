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
sys.path.append('..')

from config import rclient


def _clean():
    """
    remove expired items from queues in memory
    """
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
    

if __name__ == "__main__":
    _clean()
