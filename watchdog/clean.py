#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#@created Jan 2, 2013
#@updated Feb 8, 2013

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('/home/jinyuan/Downloads/bgm_news')

from bson.objectid import ObjectId
import calendar
from datetime import datetime, timedelta
import feedparser
import os
from scraper import memory
import time

# CONSTANTS
from config import Collection
from config import DATABASE_REMOVAL_DAYS
from config import db
from config import IMAGES_LOCAL_DIR
from config import IMAGES_PUBLIC_DIR
from config import LANGUAGES
from config import MEMORY_RESTORATION_DAYS
from config import rclient
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


def clear_thumbnail(removal_candidate):
    '''convert web path to local path'''
    if isinstance(removal_candidate['image'], str):
        thumbnail_web_path = removal_candidate['image']
        thumbnail_local_path = thumbnail_web_path.replace(
            IMAGES_PUBLIC_DIR, IMAGES_LOCAL_DIR)
        if os.path.exists(thumbnail_local_path):
            os.remove(thumbnail_local_path)
    elif isinstance(removal_candidate['image'], list):
        for thumbnail_web_path in removal_candidate['image']:
            thumbnail_local_path = thumbnail_web_path.replace(
                IMAGES_PUBLIC_DIR, IMAGES_LOCAL_DIR)
            if os.path.exists(thumbnail_local_path):
                os.remove(thumbnail_local_path)


def clear_transcoded(removal_candidate):
    '''convert web path to local path'''
    transcoded_web_path = removal_candidate['transcoded']
    transcoded_local_path = transcoded_web_path.replace(
        TRANSCODED_PUBLIC_DIR, TRANSCODED_LOCAL_DIR)
    if os.path.exists(transcoded_local_path):
        os.remove(transcoded_local_path)


def clear_zombies(language):
    '''zombies are shits in memory but no more in database'''
    language_ids_total = rclient.zcard("news::%s" % language)
    col = Collection(db, language)
    if language_ids_total:
        entry_ids = rclient.zrange("news::%s" % language, 0, language_ids_total)
        for entry_id in entry_ids:
            item = col.find_one({'_id': ObjectId(entry_id)})
            if not item:  # then its a zombie
                if rclient.exists(entry_id):
                    print 'ZOMBIE!!: ', entry_id, eval(rclient.get(entry_id))['title']
                    rclient.delete(entry_id)
    else:
        print 'there is no such a language %s' % language


def clear_long_dated(language):
    if not language:
        return None
    else:
        col = Collection(db, language)
        # data more than DATABASE_REMOVAL_DAYS days are removed
        current_utc_time_posix = calendar.timegm(time.gmtime())
        deadline_datetime = datetime.utcfromtimestamp(
            current_utc_time_posix) - timedelta(days=DATABASE_REMOVAL_DAYS)
        deadline_posix = calendar.timegm(deadline_datetime.timetuple())

        removal_candidates = col.find({'updated': {'$lt': deadline_posix}})
        removed_ids = []
        for removal_candidate in removal_candidates:
            clear_transcoded(removal_candidate)
            clear_thumbnail(removal_candidate)
            removed_ids.append(str(removal_candidate['_id']))
            # remove memory items
            rclient.delete(str(removal_candidate['_id']))
            # remove database items
            col.remove({'_id': removal_candidate['_id']})
        return removed_ids


def clear():
    print '----------------------clearing-------------------------'
    # clear memory
    language_files = read_task_directory()
    for language_file in language_files:
        language = language_file.replace(MAINTENANCE_DIR, '').split('_')[0]
        # remove item in database
        removed_long_ids = clear_long_dated(language)
        # remove zombies
        removed_zombies = clear_zombies(language)
        # remove item in memory
        l = open(language_file, 'r')
        lines = l.readlines()
        for line in lines:
            language, category, feed_id, feed_link = extract_task(line)
            removed_short_ids = clear_short_dated(
                language, category, feed_id)
        l.close()
        print


# TODO: put language in config file
if __name__ == "__main__":
    command = sys.argv[1]
    if len(sys.argv) > 2:
        eval(command)(sys.argv[2])
    else:
        eval(command)()
