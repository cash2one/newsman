#!/usr/bin/env python
#-*- coding: utf-8 -*-

# rss is the interface to rss parsing,
# processing and storing.
#
# @author Jin Yuan
# @email jinyuan@baidu.com
# @created Jul. 20, 2013

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import calendar
import database
from datetime import datetime, timedelta
from data_processor import transcoder
from data_processor import tts_provider
from image_processor import image_helper
from image_processor import thumbnail
import memory
import random
import rss_parser
import time

from administration.config import DATABASE_REMOVAL_DAYS
from administration.config import LANGUAGES
from administration.config import MEMORY_EXPIRATION_DAYS
from administration.config import THUMBNAIL_SIZE


def _value_added_process(entries=None, language=None):
    """
    add more value to an entry
    tts, transcode, images, redis_entry_expiration, database_entry_expiration
    """
    if not entries:
        return None
    if not language or language not in LANGUAGES:
        raise Exception("ERROR: language not found or not supported!")

    entries_new = []
    for entry in entries:
        # get a random int from 100 million possibilities
        try:
            rand = random.randint(0, 100000000)
            transcoded_relative_path = '%s_%s_%s_%i' % (
                entry['language'], entry['feed_id'], entry['updated_parsed'], rand)
            # high chances transcoder cannot work properly
            entry['transcoded'], entry['transcoded_local'] = transcoder.transcode(
                entry['language'], entry['title'], entry['link'], transcoded_relative_path)

            # find big images
            big_images = image_helper.find_images(entry['transcoded_local'])
            if big_images:
                entry['big_images'] = entry[
                    'big_images'] if entry.has_key('big_images') else []
                entry['big_images'].extend(entry['transcoded'])
                entry['big_images'] = list(set(entry['big_images']))
            entry['big_images'] = None if not entry.has_key(
                'big_images') else entry['big_images']

            # find biggest image
            if entry.has_key('big_images'):
                entry['image'] = image_helper.find_biggest_image(
                    entry['big_images'])
            entry['image'] = None if not entry.has_key(
                'image') else entry['image']

            # tts only for English, at present
            if entry['language'] == 'en':
                try:
                    tts_relative_path = '%s_%s_%s_%i.mp3' % (
                        entry['language'], entry['feed_id'], entry['updated_parsed'], rand)
                    entry['mp3'], entry['mp3_local'] = tts_provider.google(
                        entry['language'], entry['title'], tts_relative_path)
                except Exception as k:
                    print k, '... cannot generate TTS for %s' % entry['link']
                    entry['mp3'] = None
                    entry['mp3_local'] = None

            # add expiration data
            def _expired(updated_parsed, days_to_deadline):
                """
                compute expiration information
                return time string and unix time
                """
                deadline = datetime.utcfromtimestamp(
                    updated_parsed) + timedelta(days=days_to_deadline)
                return time.asctime(time.gmtime(calendar.timegm(deadline.timetuple())))

            entry['memory_expired'] = _expired(
                entry['updated_parsed'], MEMORY_EXPIRATION_DAYS)
            entry['database_expired'] = _expired(
                entry['updated_parsed'], DATABASE_REMOVAL_DAYS)

            entries_new.append(entry)
        except Exception as k:
            print k
    return entries_new


# Todos
# code to remove added items if things suck at database/memory
def update(feed_link=None, feed_id=None, feed_title=None, language=None, categories=None, etag=None, modified=None):
    """
    update could be called
    1. from task procedure: all parameters included
    2. after an rss is added: all parameters included
    3. manually for testing purpose: feed_link, language
    Note. categories are ids of category item
    """
    if not feed_link or not feed_id or not language or not categories:
        raise Exception(
            "ERROR: Method signature not well formed for %s!" % feed_link)
    if language not in LANGUAGES:
        raise Exception("ERROR: Language not supported for %s!" % feed_link)
    # parameters striped
    feed_link = feed_link.strip()
    language = language.strip()

    # parse rss reading from remote rss servers
    entries, feed_title_new, etag_new, modified_new = rss_parser.parse(
        feed_link, feed_id, feed_title, language, categories, etag, modified)

    # filter out existing entries in database
    # there are some possible exceptions -- yet let it be
    entries = database.dedup(entries, language)
    # and do tts, big_images, image as well as transcode.
    entries = _value_added_process(entries, language)

    # update new entries to database
    # each entry is added with _id
    entries = database.update(entries, language)
    # and some data, like feed_title, etag and modified to database
    # database.update_feed()

    # store in memory
    memory.update(entries, language, categories)
    return entries
