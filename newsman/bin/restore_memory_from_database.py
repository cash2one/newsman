#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
restore memory from database, if memory failed
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 23, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from bson.objectid import ObjectId
from config.settings import Collection, db
from config.settings import rclient
from datetime import datetime, timedelta
from scraper import memory

# CONSTANTS
from config.settings import MEMORY_RESTORATION_DAYS
from config.settings import LANGUAGES


def _get_expiration(updated):
    """
    Compute expiration time
    """
    if not updated:
        return 0

    deadline = datetime.utcfromtimestamp(updated) + timedelta(days=MEMORY_RESTORATION_DAYS)
    time_left = deadline - datetime.now()
    return time_left.days * 60 * 60 * 24 + time_left.seconds


def restore():
    """
    if memory failed, restore items from database
    """
    try:
        # check if redis is alive
        rclient.ping()
        # flushall existing data
        rclient.flushall()
    except ConnectionError:
        print 'Redis is down! Cannot recover memory data from database'
        return None

    print '=== RESTORE MEMORY FROM DATABASE ==='
    collections = db.collection_names()
    for collection in collections:
        if collection != 'system.indexes' and collection != 'feeds':
            language = collection
            col = Collection(db, language)

            # find valid time to filter out expired items
            current_utc_time_posix = calendar.timegm(time.gmtime())
            active_datetime = datetime.utcfromtimestamp(current_utc_time_posix) - timedelta(days=MEMORY_RESTORATION_DAYS)
            active_posix = calendar.timegm(active_datetime.timetuple())

            items = col.find({'updated': {'$gte': active_posix}}).sort('updated', -1)
            if items:
                for item in items:
                    expiration = _get_expiration(float(item['updated']))
                    memory.update(item, expiration)


if __name__ == "__main__":
    restore()
