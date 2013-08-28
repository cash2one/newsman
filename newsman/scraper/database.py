#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
database deals with saving, updating and deleting rss items to/from database
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul., 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from config import Collection, db
from config import logger

# CONSTANTS
from config import LANGUAGES


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
            dup_link = col.find_one({'link': entry['link']})
            dup_title = col.find_one({'title': entry['title']})

            if dup_link or dup_title:
                logger.info(
                    'Find a duplicate for %s' % str(entry['title']))
                continue
            else:
                entries_new.append(entry)
        return entries_new if entries_new else None
    except Exception as k:
        pass
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
        logger.debug(entry['_id'] + ' is inserted into database')
        return entry
    except Exception as k:
        pass
        logger.error(str(k))
        return None
