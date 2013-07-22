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

from administration.config import Collection
from administration.config import db
import random
import rss_parser
from image_processor import thumbnail
from data_processor import transcoder
from data_processor import tts_provider

from administration.config import THUMBNAIL_LOCAL_DIR
from administration.config import THUMBNAIL_SIZE
from administration.config import THUMBNAIL_WEB_DIR
from administration.config import LANGUAGES


def _value_added_process(entries=None, language=None):
    """
    add more value to an entry
    tts, transcode, images
    """


def update(feed_link=None, feed_id=None, feed_title=None, language=None, etag=None, modified=None):
    """
    update could be called
    1. from task procedure
    2. after an rss is added
    3. manually for testing purpose
    """
    if not feed_link or not language:
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
    # and do tts, big_images, image as well as transcode.
    entries_new = screen_duplicates(entries)

    # update new entries and some data, like feed_title, etag and modified to database

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
