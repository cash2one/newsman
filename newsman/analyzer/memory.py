#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
memory provides an interface to store news in the memory/redis
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Jul. 2013'

from newsman.config.settings import Collection, db
from newsman.config.settings import logger
from newsman.config.settings import rclient, ConnectionError
import sys

# CONSTANTS
from newsman.config.settings import FEED_REGISTRAR
from newsman.config.settings import MEMORY_EXPIRATION_DAYS

reload(sys)
sys.setdefaultencoding('UTF-8')

# list of fields stored in memory
field_list = [
    '_id', 'category_image', 'feed', 'hotnews_image', 'image', 'labels',
    'language', 'link', 'mp3', 'summary', 'text_image', 'thumbnail_image',
    'title', 'transcoded', 'updated']


def update(entry=None, expiration=None):
    """
    add news and its attributes to memory
    """
    if not entry:
        logger.error('Method malformed!')
        return False

    try:
        # check if redis in alive
        rclient.ping()

        entry_reduced = {}
        # simplify fields in entry to ones in field_list
        for field in entry:
            if field in field_list:
                entry_reduced[field] = entry[field]

        # add an entry to memory
        # add a piece of news into memory
        rclient.set(entry_reduced['_id'], entry_reduced)

        # expired in redis is counted in seconds
        expiration = MEMORY_EXPIRATION_DAYS * 24 * \
                     60 * 60 if not expiration else expiration
        rclient.expire(entry_reduced['_id'], expiration)

        # add entry ids to the RSS list
        rclient.zadd("news::%s::%s" %
                     (entry_reduced['language'], entry_reduced['feed']),
                     entry_reduced['updated'], entry_reduced['_id'])

        # add entry ids to the label list
        col = Collection(db, FEED_REGISTRAR)
        item = col.find_one(
            {'feed_title': entry_reduced['feed']}, {'labels': 1})
        if item and 'labels' in item and item['labels']:
            for label in item['labels']:
                # a label is a combination of country, category and label
                rclient.zadd('news::%s::%s' %
                             (entry_reduced['language'], label),
                             entry_reduced['updated'], entry_reduced['_id'])
        # final return
        return True
    except ConnectionError:
        logger.critical('Redis is down!')
        return False
    except Exception as k:
        logger.error(str(k))
        return False
