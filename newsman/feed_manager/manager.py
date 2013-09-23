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


def update_label(language=None, label=None):
    """
    Update memory and database on label change
    Note. label should be country::category::label-like
    """

    if not language or not label:
        return None

    label_name_in_memory = 'news::%s::%s' % (language, label)
    feeds = Collection(db, FEED_REGISTRAR) 
    items = feeds.find({'labels':label}, {'feed_title'})


if __name__ == '__main__':
    pass
