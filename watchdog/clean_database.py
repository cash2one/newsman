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

import calendar
from config import Collection, db
from datetime import datetime, timedelta
import time

# CONSTANTS
from config import FEED_REGISTRAR


def _find_document_names():
    """
    find all documents
    note. documents are represented by language
    """
    feeds = Collection(db, FEED_REGISTRAR)
    document_names = []
    # only get language and _id
    items = feeds.find({}, {'language':1})
    if items:
        document_names = [item['language'] for item in items]
    return list(set(document_names))


def _clean():
    """
    remove expired items from database
    """
    document_names = _find_document_names()
    for document_name in document_names:
        document = Collection(db, document_name)

        # compute a threshold
        current_utc_time_posix = calendar.timegm(time.gmtime())
        deadline_datetime = datetime.utcfromtimestamp(current_utc_time_posix) - timedelta(days=DATABASE_REMOVAL_DAYS)
        deadline_posix = calendar.timegm(deadline_datetime.timetuple())

        removal_candidates = document.find({'updated': {'$lt': deadline_posix}})
        for removal_candidate in removal_candidates:

    

if __name__ == "__main__":
    _clean()
