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

import rss_parser

def add_entries(feed_id=None, feed_link=None, language=None, category=None):
    """
    add_entries could be called
    1. by automation/task procedures
    2. after a rss is called
    3. manually for testing purpose
    """
    if not feed_id or not feed_link or not language or not category:
        return None
    feed_link = feed_link.strip()
    language = language.strip()
    category = category.strip()
    if language not in LANGUAGES:
        return None
    if category.count(' '):
        return None

    entries = rss_parser.parse(feed_id, feed_link, language, category)
    print 'Nothing found from RSS' if not entries else '    1/3 .. retrieved %i entries' % len(entries)
    # store in both database and memory
    if entries:
        added_entries = database.update(entries, language)
        print 'Nothing updated' if not added_entries else '    2/3 .. updated %i database items' % len(added_entries)
        if added_entries:
            updated_entries = memory.update(
                added_entries, language, category, feed_id)
            print '' '    3/3 .. updated memory'
            return updated_entries
    return None
