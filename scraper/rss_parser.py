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
    entry['category'] = category
    entry['feed'] = feed_id
    entry['language'] = language

    try:
        # article original link
        entry['link'] = e.link.strip()
        # article title
        if e.title_detail.type != 'text/plain':
            entry['title'] = hparser.unescape(e.title.strip())
        else:
            entry['title'] = e.title.strip()
    except AttributeError as e:
        print e
        entry['error'] = e

    # article published time
    # first try parsed time info
    try:
        entry['updated'] = calendar.timegm(e.updated_parsed)
    except AttributeError as e:
        print e, "... will try attribute 'published_parsed'"
        try:
            entry['updated'] = calendar.timegm(e.published_parsed)
        except AttributeError as e:
            print e, "... will try attibutes 'update' and 'published'"
            entry['error'] = '%s\n%s' % (entry['error'], 'no parsed update or published')
            # then try unparsed time info
            try:
                updated = e.updated if 'updated' in e else e.published
                if updated:
                    # get time zone
                    offset = int(updated[-5:])
                    delta = timedelta(hours=offset / 100)
                    format = "%a , %d %b %Y %H:%M:%S"
                    if updated[-8:-5] != 'UTC':
                        updated = datetime.strptime(updated[:-6], format)
                    else:
                        updated = datetime.strptime(updated[:-9], format)
                    updated -= delta
                    entry['updated'] = time.mktime(updated.timetuple())
                else:
                    raise ValueError("attribute updated/published has no value")
            except ValueError as e:
                print e
                entry['error'] = '%s\n%s' % (entry['error'], e)
                raise Exception('----- ERROR: entry %s has no publication info!' % entry['title'])
            except AttributeError as e:
                print e
                entry['error'] = '%s\n%s' % (entry['error'], 'no update or published')
                raise Exception('----- ERROR: entry %s has no publication info!' % entry['title'])

    # article's thumbnail     
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
    # update parsing info to feed database

    def validate_time(entry):
        ''''''
        deadline = datetime.utcfromtimestamp(
            entry['updated']) + timedelta(days=MEMORY_RESTORATION_DAYS)
        return True if deadline > datetime.now() else False

    d = feedparser.parse(feed_link)
    if d:
        if 'entries' in d:
            language = language if not d.language else d.language
            entries = [read_entry(e, language, category, feed_id)
                       for e in d['entries']]
            return filter(validate_time, entries)
        else:
            return None
    else:
        return None


