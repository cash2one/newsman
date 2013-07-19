#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#
#@created Jan 2, 2013
#@updated Feb 8, 2013
#@updated Jul 14, 2013
#
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulStoneSoup
import calendar
from datetime import timedelta, datetime
import feedparser
from administration.config import hparser
import random
from administration.config import rclient
from image_processor import thumbnail
import time
import urllib2

from administration.config import LANGUAGES
from administration.config import MEMORY_RESTORATION_DAYS
from administration.config import REDIS_ENTRY_EXPIRATION


def update_memory(added_items=None, language=None, category=None, feed_id=None):
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


def read_entry(e=None, language=None, category=None, feed_id=None):
    ''''''
    if not e:
        return 1
    # Todos
    # add more boundary checks

    entry = {}
    entry['language'] = language
    entry['category'] = category
    entry['feed'] = feed_id
    entry['title'] = hparser.unescape(e.title.strip())
    entry['link'] = e.link.strip()
    if ('published_parsed' in e and e['published_parsed']) or ('updated_parsed' in e and e['updated_parsed']):
        entry['updated'] = calendar.timegm(
            e['published_parsed']) if 'published_parsed' in e else calendar.timegm(e['updated_parsed'])
    elif 'published' in e or 'updated' in e:
        published = e.published if 'published' in e else e.updated
        try:
            offset = int(published[-5:])
        except:
            return None
        delta = timedelta(hours=offset / 100)
        format = "%a , %d %b %Y %H:%M:%S"
        if published[-8:-5] != 'UTC':
            updated = datetime.strptime(published[:-6], format)
        else:
            updated = datetime.strptime(published[:-9], format)
        updated -= delta
        entry['updated'] = time.mktime(updated.timetuple())
    if 'media_thumbnail' in e or 'media_content' in e:
        thumbnails = e['media_content'] if 'media_content' in e else e[
            'media_thumbnail']
        # a list of thumbnails
        for thumbnail in thumbnails:
            if 'url' in thumbnail:
                image_web = thumbnail['url']
                if 'image' not in entry:
                    entry['image'] = []
                entry['image'].append(image_web)
    if 'thumbnail' in e:
        if 'image' not in entry:
            entry['image'] = []
        entry['image'].append(e['thumbnail'])
    if 'summary' in e:
        soup = BeautifulStoneSoup(e.summary)
        entry['image'] = []
        entry['summary'] = ''
        # thumbnail(s)

        # Todos
        # rename variable! bloody ugly
        # remove name length checking
        #
        if soup.img:
            img = soup.img['src']
            if isinstance(img, str):
                thumbnail_relative_path = '%s.jpeg' & img
                if len(thumbnail_relative_path) > 200:
                    thumbnail_relative_path = thumbnail_relative_path[-200:]
                thumbnail_url = thumbnail.get(
                    img, thumbnail_relative_path)
                entry['image'].append(thumbnail_url)
            elif isinstance(img, list):
                for im in img:
                    thumbnail_relative_path = '%s.jpeg' % im
                    if len(thumbnail_relative_path) > 200:
                        thumbnail_relative_path = thumbnail_relative_path[
                            -200:]
                    thumbnail_url = thumbnail.get(
                        im, thumbnail_relative_path)
                    entry['image'].append(thumbnail_url)
        # abstract
        if soup.text:
            entry['summary'] = hparser.unescape(soup.text)
    else:
        entry['summary'] = ''
        entry['image'] = []
    entry['image'] = 'None' if not entry['image'] else entry['image']
    entry['summary'] = 'None' if not entry['summary'] else entry['summary']
    return entry


def extract_entries(feed_id=None, feed_link=None, language=None, category=None):
    '''read rss/atom data from a given feed'''
    def validate_time(entry):
        ''''''
        deadline = datetime.utcfromtimestamp(
            entry['updated']) + timedelta(days=MEMORY_RESTORATION_DAYS)
        return True if deadline > datetime.now() else False

    d = feedparser.parse(feed_link)
    if d:
        if 'entries' in d:
            entries = [read_entry(e, language, category, feed_id)
                       for e in d['entries']]
            return filter(validate_time, entries)
        else:
            return None
    else:
        return None


def add_entries(feed_id=None, feed_link=None, language=None, category=None):
    ''''''
    if not feed_id or not feed_link or not language or not category:
        return None
    feed_link = feed_link.strip()
    language = language.strip()
    category = category.strip()
    if language not in LANGUAGES:
        return None
    if category.count(' '):
        return None

    entries = extract_entries(feed_id, feed_link, language, category)
    print 'Nothing found from RSS' if not entries else '    1/3 .. retrieved %i entries' % len(entries)
    # store in both database and memory
    if entries:
        added_entries = update_database(entries, language)
        print 'Nothing updated' if not added_entries else '    2/3 .. updated %i database items' % len(added_entries)
        if added_entries:
            updated_entries = update_memory(
                added_entries, language, category, feed_id)
            print '' '    3/3 .. updated memory'
            return updated_entries
    return None
