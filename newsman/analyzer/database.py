#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database deals with saving, updating and deleting rss items to/from database
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Jul., 2013'

from newsman.config.settings import Collection, db
from newsman.config.settings import logger
import sys

# CONSTANTS
from newsman.config.settings import LANGUAGES

reload(sys)
sys.setdefaultencoding('UTF-8')

# Database is indexed by
# db.en.ensureIndex({'feed':1, 'title':1, 'link':1}, {background: true,
# unique: true, dropDups: true})
# to ensure unique insertion
# and db.en.ensureIndex({'feed':1, 'updated':-1}, {background: true})
# to ensure fast query
#


def dedup(entries=None, language=None):
    """
    return entries not found in database
    """
    if not entries:
        logger.error('Method malformed!')
        return None
    if not language or language not in LANGUAGES:
        logger.error("Language not found or not supported!")
        return None

    try:
        entries_new = []
        col = Collection(db, language)
        for entry in entries:
            # find duplicate in the form of the same link or title
            dup_link = col.find_one(
                {'link': entry['link'], 'feed': entry['feed']})
            if dup_link:
                logger.info('Find a duplicate for %s' % str(entry['title']))
                continue
            else:
                dup_title = col.find_one(
                    {'title': entry['title'], 'feed': entry['feed']})
                if dup_title:
                    logger.info(
                        'Find a duplicate for %s' % str(entry['title']))
                    continue
                else:
                    entries_new.append(entry)
        return entries_new if entries_new else None
    except Exception as k:
        logger.error(str(k))
        return None


def update(entry=None):
    """
    save an entry in database
    """
    if not entry:
        logger.error('Method malformed!')
        return None
    if entry['language'] not in LANGUAGES:
        logger.error("Language not found or not supported!")
        return None

    try:
        # collection was created by the feed
        col = Collection(db, entry['language'])
        # then save to database
        entry_id = col.save(entry)
        entry['_id'] = str(entry_id)
        return entry
    except Exception as k:
        logger.error(str(k))
        return None
