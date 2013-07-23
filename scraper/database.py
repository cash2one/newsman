#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from administration.config import Collection
from administration.config import db
from administration.config import LANGUAGES


def dedup(entries=None, language=None):
    """
    return entries not found in database
    """
    if not entries:
        return None
    if not language or language not in LANGUAGES:
        raise Exception("ERROR: language not found or not supported!")

    entries_new = []
    col = Collection(db, language)
    for entry in entries:
        # find duplicate in the form of the same link or title
        dup_link = col.find_one({'link': entry['link']})
        dup_title = col.find_one({'title': entry['title']})
        if not dup_link or not dup_title:
            print 'Find a duplicate for %s' % entry['title']
            continue
        else:
            entries_new.append(entry)
    return entries_new if entries_new else None 


# Todos
# - break update_database into several shorter mthods
def update(entries=None, language=None):
    """
    save entries
    """
    if not entries:
        return None
    if not language or language not in LANGUAGES:
        raise Exception("ERROR: language not found or not supported!")

    # collection was created by the feed
    col = Collection(db, language)
    for entry in entries:
        # then save to database
        entry_id = col.save(entry)
        entry['_id'] = str(entry_id)
    return entries


def update_feed():
    """
    docs needed!
    """
    pass
