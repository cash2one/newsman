#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
restore memory from database, if memory failed
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Aug. 23, 2013'

from bson.objectid import ObjectId
import calendar
from datetime import datetime, timedelta
from newsman.analyzer import memory
from newsman.config.settings import Collection, db
from newsman.config.settings import rclient
import sys
import time

# CONSTANTS
from newsman.config.settings import MEMORY_EXPIRATION_DAYS
from newsman.config.settings import LANGUAGES

reload(sys)
sys.setdefaultencoding('UTF-8')


def _expired(updated):
    """
    Compute expiration time
    """
    if not updated:
        return 0

    deadline = datetime.utcfromtimestamp(
        updated) + timedelta(days=MEMORY_EXPIRATION_DAYS)
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
    try:
        collection_names = db.collection_names()
        for collection_name in collection_names:
            if collection_name != 'system.indexes' and collection_name != \
                    'feeds':
                col = Collection(db, collection_name)

                # find valid time to filter out expired items
                current_utc_time_posix = calendar.timegm(time.gmtime())
                active_datetime = datetime.utcfromtimestamp(
                    current_utc_time_posix) - timedelta(
                    days=MEMORY_EXPIRATION_DAYS)
                active_posix = calendar.timegm(active_datetime.timetuple())

                items = col.find(
                    {'updated': {'$gte': active_posix}}).sort('updated', -1)
                for item in items:
                    expiration = _expired(float(item['updated']))
                    memory.update(item, expiration)
        print '=== MEMORY SUCCESSFULLY RESTORED ==='
    except Exception as k:
        print 'Memory restoring blocked due to [%s]' % str(k)
        return None


if __name__ == "__main__":
    restore()
