#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
cleaner is an interface file to clean database, memory and files on disk
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('/home/jinyuan/Downloads/bgm_news')

from bson.objectid import ObjectId
import calendar
from config import Collection, db
from config import rclient
from datetime import datetime, timedelta
import feedparser
import os
from scraper import memory
import time
from watchdog import clean_database, clean_memory, clean_disk

# CONSTANTS
from config import DATABASE_REMOVAL_DAYS
from config import IMAGES_LOCAL_DIR
from config import IMAGES_PUBLIC_DIR
from config import LANGUAGES
from config import MEMORY_RESTORATION_DAYS
from config import TRANSCODED_LOCAL_DIR
from config import TRANSCODED_PUBLIC_DIR


def restore():
    '''if memory failed, restore items from database'''
    def get_expiration(updated):
        ''''''
        deadline = datetime.utcfromtimestamp(
            updated) + timedelta(days=MEMORY_RESTORATION_DAYS)
        time_left = deadline - datetime.now()
        return time_left.days * 60 * 60 * 24 + time_left.seconds

    print '----------------------restoring-------------------------'
    language_files = read_task_directory()
    for language_file in language_files:
        print 'database to memory'
        l = open(language_file, 'r')
        lines = l.readlines()
        language = None
        col = None
        for line in lines:
            language, category, feed_id, feed_link = extract_task(line)
            col = Collection(db, language)
            current_utc_time_posix = calendar.timegm(time.gmtime())
            active_datetime = datetime.utcfromtimestamp(
                current_utc_time_posix) - timedelta(days=MEMORY_RESTORATION_DAYS)
            active_posix = calendar.timegm(active_datetime.timetuple())
            items = col.find(
                {'category': category, 'feed': feed_id, 'updated': {'$gte': active_posix}}).sort('updated', -1)
            if items:
                items_with_expiration = [(item, get_expiration(float(item['updated'])))
                                         for item in items]
                # for i in items_with_expiration:
                    #ent = i[0]
                    #exp = i[1]
                    # print '++', ent['_id'],
                    # datetime.utcfromtimestamp(ent['updated']), exp
                memory.update_memory(
                    items_with_expiration, language, category, feed_id)
            print language, category, feed_id, len(items_with_expiration)
        l.close()
        print 'memory to database for %s' % language
        language_in_memory_total = rclient.zcard(language)
        language_ids = rclient.zrange(language, 0, language_in_memory_total)
        if language_ids:
            for language_id in language_ids:
                if not rclient.get(language_id):
                    print language_id, 'is missing'
                    id_aloof = col.find_one({'_id': ObjectId(language_id)})
                    if id_aloof:
                        for key, value in id_aloof.iteritems():
                            id_aloof[key] = str(value)
                        rclient.set(id_aloof['_id'], id_aloof)
                        # print '--', id_aloof['_id'],
                        # datetime.utcfromtimestamp(id_aloof['updated']),
                        # get_expiration(float(id_aloof['updated']))
                        rclient.expire(
                            id_aloof['_id'], get_expiration(float(id_aloof['updated'])))
                        print 'restored', id_aloof['_id'], id_aloof['title'], datetime.utcfromtimestamp(float(id_aloof['updated']))
        print
    return 0


def is_overdue(time_stamp):
    """
    find out if the file is overdue
    """
    if not time_stamp:
        return False

    deadline_datetime = datetime.utcfromtimestamp(time_stamp) + timedelta(days=DATABASE_REMOVAL_DAYS)
    deadline_posix = calendar.timegm(deadline_datetime.timetuple())
    now_posix = time.mktime(time.gmtime())

    if deadline_posix < now_posix:  # deadline is earlier than now
        return True
    else:
        return False


def clean():
    """
    cleaner interface
    """
    print '----------------------cleaning-------------------------'
    # clean database
    clean_database.clean()
    # clean memory
    clean_memory.clean()
    # clean disk
    clean_disk.clean()


if __name__ == "__main__":
    clean()
