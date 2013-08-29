#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
memory provides an interface to store news in the memory/redis
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from config import logger
from config import rclient, ConnectionError

# CONSTANTS
from config import MEMORY_EXPIRATION_DAYS

# list of fields stored in memory
field_list = ['_id', 'categories', 'category_image', 'feed', 'hotnews_image', 'image', 'language', 'link', 'mp3', 'summary', 'thumbnail_image', 'title', 'transcoded', 'updated']


def update(entry=None):
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
        expiration = MEMORY_EXPIRATION_DAYS * 24 * 60 * 60
        rclient.expire(entry_reduced['_id'], expiration)

        # add entry ids to the language list
        rclient.zadd("news::%s" % entry_reduced['language'], entry_reduced['updated'], entry_reduced['_id'])

        # add entry ids to the category list
        for category in entry_reduced['categories']:
            rclient.zadd('news::%s::%s' % (entry_reduced['language'], category), entry_reduced['updated'], entry_reduced['_id'])
        # final return
        return True
    except ConnectionError:
        logger.critical('Redis is down!')
        return False
    except Exception as k:
        logger.error(str(k))
        return False
