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
from image_processor import thumbnail
import time
import urllib2

from administration.config import LANGUAGES


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


def parse(feed_id=None, feed_link=None, language=None, category=None):
    """read rss/atom data from a given feed"""
    # Todos
    # boundary checkers

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


