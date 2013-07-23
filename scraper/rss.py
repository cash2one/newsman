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

import database
import random
import rss_parser
from iamge_processor import image_helper
from image_processor import thumbnail
from data_processor import transcoder
from data_processor import tts_provider

from administration.config import DATABASE_REMOVAL_DAYS
from administration.config import LANGUAGES
from administration.config import MEMORY_ENTRY_EXPIRATION
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
            transcoded_relative_path = '%s_%s_%s_%i' % (entry['language'], entry['feed_id'], entry['updated'], rand)
            # high chances transcoder cannot work properly
            entry['transcoded'] = transcoder.transcode(entry['language'], entry['title'], entry['link'], transcoded_relative_path) 

            # find big images
            big_images = image_helper.find_images(entry['transocded'])
            if big_images:
                entry['big_images'] = entry['big_images'] if entry.has_key('big_images') else []
                entry['big_images'].extend(entry['transcoded'])
                entry['big_images'] = list(set(entry['big_images']))

            # find biggest image
            if entry['big_images']:
                entry['image'] = image_helper.find_biggest_image(entry['big_images'])

            # tts only for English, at present
            if entry['language'] == 'en':
                try:
                    tts_relative_path = '%s_%s_%s_%i' % (entry['language'], entry['feed_id'], entry['updated'], rand)
                    entry['mp3'] = tts_provider.google(entry['language'], entry['title'], tts_relative_path)
                except Exception as k:
                    print k, '... cannot generate TTS for %s' % entry['link']
                    entry['mp3'] = "None"

            # expiration information
            entry['memory_expired'] = MEMORY_ENTRY_EXPIRATION
            entry['database_expired'] = DATABASE_REMOVAL_DAYS

            entries_new.append(entry)
        except Exception as k:
            if k.startswith('ERROR'):
                print k
    return entries_new


def update(feed_link=None, feed_id=None, feed_title=None, language=None, etag=None, modified=None):
    """
    update could be called
    1. from task procedure: all parameters included
    2. after an rss is added: all parameters included
    3. manually for testing purpose: feed_link, language
    """
    if not feed_link or not feed_link or not language:
        raise Exception(
            "ERROR: Method signature not well formed for %s!" % feed_link)
    if language not in LANGUAGES:
        raise Exception("ERROR: Language not supported for %s!" % feed_link)
    # parameters striped
    feed_link = feed_link.strip()
    language = language.strip()

    # parse rss reading from remote rss servers 
    try:
        entries, feed_title_new, etag_new, modified_new = rss_parser.parse(
            feed_link, feed_id, feed_title, language, etag, modified)
    except Exception as k:
        # deal with exceptions
        if k.startswith('WARNING'):
            print k
        else:
            print k
            raise k

    # filter out existing entries in database
    # there are some possible exceptions -- yet let it be
    entries = database.dedup(entries, language)
    # and do tts, big_images, image as well as transcode.
    entries = _value_added_process(entries, language)

    # update new entries to database
    # each entry is added with _id
    entries = database.update(entries, language)
    # and some data, like feed_title, etag and modified to database
    database.update_feed()

    # store in memory
    if entries:
        updated_entries = memory.update(entries, language, feed_id)
        return updated_entries
    return None
