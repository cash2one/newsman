#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
idler finds out sources that do not update frequently
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Sept. 03, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("../..")

from config import Collection, db
from config import logger

# CONSTANTS
from config import FEED_REGISTRAR


def _find_idler():
    """
    contact feeds database and apply the filter
    """
    try:
        document = Collection(db, FEED_REGISTRAR) 
        feeds = document.find({}, {'latest_update':1, 'feed_title':1, 'feed_link':1})
        if feeds:
            for feed in feeds:
                pass
        else:
            logger.error('Cannot find any feed in %s' % FEED_REGISTRAR)
    except Exception as k:
        logger.error(str(k))


if __name__ == "__main__":
    _find_idler()

