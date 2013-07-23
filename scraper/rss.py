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
from image_processor import thumbnail
from data_processor import transcoder
from data_processor import tts_provider

from administration.config import LANGUAGES
from administration.config import THUMBNAIL_LOCAL_DIR
from administration.config import THUMBNAIL_SIZE
from administration.config import THUMBNAIL_WEB_DIR


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
            relative_path = '%s_%s_%s_%i' % (entry['language'], entry['feed_id'], entry['updated'], rand)
            # high chances transcoder cannot work properly
            entry['transcoded'] = transcoder.transcode(entry['language'], entry['title'], entry['link'], relative_path) 

            # find big images
            entry['big_images'].extend(entry['transcoded'])
            entry['big_images'] = list(set(entry['big_images']))

            entries_new.append(entry)
        except Exception as k:
            if k.startswith('ERROR'):
                print k
            entry[
                'big_images'] = 'None' if not big_images else big_images
            if entry['image'] == 'None' and entry['big_images'] != 'None':
                entry['image'] = []
                bimage_max = 0, 0
                for bimage in entry['big_images']:
                    bimage_current = thumbnail.get_image_size(bimage)
                    if bimage_current > bimage_max:
                        thumbnail_relative_path = '%s.jpeg' % bimage
                        if len(thumbnail_relative_path) > 200:
                            thumbnail_relative_path = thumbnail_relative_path[
                                -200:]
                        try:
                            thumbnail_url = thumbnail.get(
                                bimage, thumbnail_relative_path)
                            entry['image'] = thumbnail_url
                            bimage_max = bimage_current
                        except IOError as e:
                            entry['big_images'].remove(bimage)
            elif entry['image'] and isinstance(entry['image'], list):
                entry['image'] = entry['image'][0]
            # Google TTS
            # only for English, at present
            if entry['language'] == 'en':
                try:
                    random_code = random.randint(0, 1000000000)
                    tts_web_path = '%s%s_%s_%i.mp3' % (
                        THUMBNAIL_WEB_DIR, entry['language'], entry['updated'], random_code)
                    tts_local_path = '%s%s_%s_%i.mp3' % (
                        THUMBNAIL_LOCAL_DIR, entry['language'], entry['updated'], random_code)
                    tts_provider.google(
                        entry['language'], entry['title'], tts_local_path)
                    entry['mp3'] = tts_web_path
                except Exception as e:
                    entry['mp3'] = "None"
    except Exception as e:
        print str(e)
    added_entries.append((entry, REDIS_ENTRY_EXPIRATION))
    added_entries.append((entry, MONGODB_ENTRY_EXPIRATION))
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
    entries = database.update(entries, language)
    # and some data, like feed_title, etag and modified to database
    database.update_feed()

    # store in both database and memory
    if entries_new:
        added_entries = database.update(entries, language)
        print 'Nothing updated' if not added_entries else '    2/3 .. updated %i database items' % len(added_entries)
        if added_entries:
            updated_entries = memory.update(
                added_entries, language, category, feed_id)
            print '' '    3/3 .. updated memory'
            return updated_entries
    return None
