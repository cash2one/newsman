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

from config import rclient

# CONSTANTS
from config import MEMORY_EXPIRATION_DAYS


# TODO: add more comments
# TODO: be precautious with possible redis adding failure
def update(entry=None, language=None, categories=None):
    """
    add news and its attributes to memory
    """
    if not entry:
        return None
    if not language or not categories:
        raise Exception("ERROR: Method signature not well formed!")

    # add entry objects to memory
    for entry in entries:
        # add a piece of news into memory
        rclient.set(entry['_id'], entry)

        # expired in redis is counted in seconds
        expiration = MEMORY_EXPIRATION_DAYS * 24 * 60 * 60
        rclient.expire(entry['_id'], expiration)

        # add entry ids to the language list
        rclient.zadd("news::%s" % language, entry['updated'], entry['_id'])
        # print entry['_id'], 'is added to memory', rclient.zcard(language)

        # add entry ids to the category list
        for category in categories:
            rclient.zadd('news::%s::%s' % (language, category), entry['updated'], entry['_id'])
