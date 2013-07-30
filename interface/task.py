#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#@created Jan 2, 2013
#@updated Feb 8, 2013

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import calendar
from datetime import datetime, timedelta
import feedparser
from scraper import memory
from bson.objectid import ObjectId
import os
from scraper import rss
import time

from administration.config import Collection
from administration.config import FEED_REGISTRAR
from administration.config import DATA_CLEAR_LOG
from administration.config import DATABASE_REMOVAL_DAYS
from administration.config import db
from administration.config import IMAGES_LOCAL_DIR
from administration.config import IMAGES_PUBLIC_DIR
from administration.config import LANGUAGES
from administration.config import MAINTENANCE_DIR
from administration.config import MEMORY_RESTORATION_DAYS
from administration.config import rclient
from administration.config import RSS_UPDATE_LOG
from administration.config import TRANSCODED_LOCAL_DIR
from administration.config import TRANSCODED_PUBLIC_DIR

if not os.path.exists(MAINTENANCE_DIR):
    os.mkdir(MAINTENANCE_DIR)
if not os.path.exists(RSS_UPDATE_LOG):
    f = open(RSS_UPDATE_LOG, 'w')
    f.write('')
    f.close()
if not os.path.exists(DATA_CLEAR_LOG):
    f = open(DATA_CLEAR_LOG, 'w')
    f.write('')
    f.close()


"""
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


def clear_short_dated(language, category, feed_id):
    if not language or not category or not feed_id:
        return None
    else:
        # remove entry ids in the language list that are already expired
        removed_language_ids = 0
        language_ids_total = rclient.zcard(language)
        if language_ids_total:
            entry_ids = rclient.zrange(language, 0, language_ids_total)
            for entry_id in entry_ids:
                if not rclient.exists(entry_id):
                    rclient.zrem(language, entry_id)
                    removed_language_ids = removed_language_ids + 1

        # remove entry ids in the category list that are already expired
        collection_name = '%s-%s' % (language, category)
        removed_collection_ids = 0
        collection_ids_total = rclient.zcard(collection_name)
        if collection_ids_total:
            entry_ids = rclient.zrange(
                collection_name, 0, collection_ids_total)
            for entry_id in entry_ids:
                if not rclient.exists(entry_id):
                    rclient.zrem(collection_name, entry_id)
                    removed_collection_ids = removed_collection_ids + 1

        # remove entry ids in the source list that are already expired
        removed_source_ids = 0
        source_name = '%s-%s-%s' % (language, category, feed_id)
        source_ids_total = rclient.zcard(source_name)
        if source_ids_total:
            entry_ids = rclient.zrange(source_name, 0, source_ids_total)
            for entry_id in entry_ids:
                if not rclient.exists(entry_id):
                    rclient.zrem(source_name, entry_id)
                    removed_source_ids = removed_source_ids + 1
        return removed_language_ids, removed_collection_ids, removed_source_ids


def clear_zombies(language):
    '''zombies are shits in memory but no more in database'''
    language_ids_total = rclient.zcard(language)
    col = Collection(db, language)
    zombies = []
    if language_ids_total:
        entry_ids = rclient.zrange(language, 0, language_ids_total)
        for entry_id in entry_ids:
            item = col.find_one({'_id': ObjectId(entry_id)})
            if not item:  # then its a zombie
                zombies.append(entry_id)
                if rclient.exists(entry_id):
                    print 'ZOMBIE!!: ', entry_id, eval(rclient.get(entry_id))['title']
                    rclient.delete(entry_id)
    else:
        print 'there is no such a language %s' % language
    return zombies


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
    f = open(DATA_CLEAR_LOG, 'a')
    language_files = read_task_directory()
    for language_file in language_files:
        language = language_file.replace(MAINTENANCE_DIR, '').split('_')[0]
        # remove item in database
        removed_long_ids = clear_long_dated(language)
        if removed_long_ids:
            print 'LONG', len(removed_long_ids)
            f.write('[LONG] %s: %s %i\n' %
                    (time.asctime(time.gmtime()), language, len(removed_long_ids)))
        # remove zombies
        removed_zombies = clear_zombies(language)
        if removed_zombies:
            print 'ZOMBIE', len(removed_zombies)
            f.write('[ZOMBIE] %s: %s %i\n' %
                    (time.asctime(time.gmtime()), language, len(removed_zombies)))
        # remove item in memory
        l = open(language_file, 'r')
        lines = l.readlines()
        for line in lines:
            language, category, feed_id, feed_link = extract_task(line)
            removed_short_ids = clear_short_dated(
                language, category, feed_id)
            if removed_short_ids:
                print 'SHORT', language, category, feed_id, removed_short_ids
                f.write(
                    '[SHORT] %s: %s %i %s %i %s %i\n' % (time.asctime(time.gmtime()), language, removed_short_ids[0], '%s-%s' %
                       (language, category), removed_short_ids[1], '%s-%s-%s' % (language, category, feed_id), removed_short_ids[2]))
        f.write('\n')
        l.close()
        print
    f.close()
    return 0


def add_task(feed_id, feed_link, language, category):
    if not feed_id or not feed_link or not language or not category:
        return 1
    feed_link = feed_link.strip()
    language = language.strip()
    category = category.strip()
    if language not in LANGUAGES:
        return 2
    if category.count(' '):
        return 3

    feeds_list_path = '%s%s_feeds_list.txt' % (MAINTENANCE_DIR, language)
    if os.path.exists(feeds_list_path):
        f = open(feeds_list_path, 'r')
        lines = f.readlines()
        for line in lines:
            splits = line.split('*|*')
            if feed_link == splits[3].strip():
                # hey we find one the same as the new one
                return 5

    f = open(feeds_list_path, 'a')
    line = '*|*'.join([language, category, feed_id, feed_link])
    f.write(line + '\n')
    f.close()
    return 0
"""


def _update(feed_ids):
    """
    update links find in feeds
    """
    if not feeds:
        raise Exception("ERROR: No feed found!")
    else:
        for feed_id in feed_ids:
            rss.update(feed_id=feed_id)


def _read_feeds(language='en'):
    """
    read feed information from database feeds
    """
    db_feeds = Collection(db, FEED_REGISTRAR)
    items = db_feeds.find({'language':language})
    if items:
        return [str(item['_id']) for item in items]
    else:
        raise Exception("ERROR: Cannot find any feeds of language %s!" % language)


def scrape(language):
    """
    update news from stored feeds
    """
    print '----------------------scraping-------------------------'
    _update(_read_feeds(language))


# TODO: put language in config file
if __name__ == "__main__":
    command = sys.argv[1]
    if len(sys.argv) > 2:
        language = '/home/work/global-mobile-news/alert_maintenance/maintenance/%s_feeds_list.txt' % sys.argv[2]
        eval(command)(language)
    else:
        eval(command)()
