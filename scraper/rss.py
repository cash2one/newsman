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
from administration.config import LANGUAGES


def screen_duplicated():
    """
    screen out items already in the database
    """
    if not entries:
        return None
    # collection was created by the feed
    added_entries = []
    col = Collection(db, language)
    for entry in entries:
        duplicated = col.find_one({'link': entry['link']})
        if duplicated:
            print 'Find a duplicate for %s' % entry['title']
            continue
        item = col.find_one({'title': entry['title']})
        if not item:
            # transcode the link
            try:


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
