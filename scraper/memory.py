#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from administration.config import rclient
from administration.config import MEMORY_EXPIRATION_DAYS


# TODO: add more comments
# TODO: be precautious with possible redis adding failure
def update(entries=None, language=None, categories=None):
    """
    add news and its attributes to memory
    categories are ids of category item
    """
    if not entries:
        return None
    if not language or not categories:
        raise Exception("ERROR: Method signature not well formed!")
    
    # add entry objects to memory
    for entry in entries:
        # add a piece of news into memory
        a = rclient.set(entry['_id'], entry)

        # expired in redis is counted in seconds
        expiration = MEMORY_EXPIRATION_DAYS * 24 * 60 * 60
        rclient.expire(entry['_id'], expiration)

        # add entry ids to the language list
        b = rclient.zadd(language, entry['updated'], entry['_id'])
        # print entry['_id'], 'is added to memory', rclient.zcard(language)

        # add entry ids to the category list
        for category in categories: 
            c = rclient.zadd('%s::%s' % (language, category), entry['updated'], entry['_id'])
