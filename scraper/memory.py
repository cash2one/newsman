#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')


from datetime import datetime
from administration.config import rclient
from administration.config import MEMORY_RESTORATION_DAYS
from administration.config import MEMORY_EXPIRATION_DAYS


def update(added_items=None, language=None, category=None, feed_id=None):
    ''''''
    # Todos
    # add more comments
    if not added_items:
        return None
    # add entry objects to memory
    for item in added_items:
        entry = item[0]
        expiration = item[1]
        entry['_id'] = str(entry['_id'])
        a = rclient.set(entry['_id'], entry)
        # set expire time to 3 days later
        rclient.expire(entry['_id'], expiration)

        # add entry ids to the language list
        b = rclient.zadd(language, entry['updated'], entry['_id'])
        # print entry['_id'], 'is added to memory', rclient.zcard(language)

        # add entry ids to the category list
        c = rclient.zadd('%s-%s' %
                         (language, category), entry['updated'], entry['_id'])

        # add entry ids to the feed list
        d = rclient.zadd('%s-%s-%s' %
                         (language, category, feed_id), entry['updated'], entry['_id'])
        print datetime.utcfromtimestamp(entry['updated']), entry['title'], a, b, c, d
    return len(added_items)
