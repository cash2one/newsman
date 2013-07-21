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
from administration.config import MEMORY_RESTORATION_DAYS


# Todos
# - add more boundary checks
# - [register unsupported date format](http://pythonhosted.org/feedparser/date-parsing.html#advanced-date)
# - add tags
def read_entry(e=None, language=None, category=None, feed_id=None):
    """
    docs needed!
    """
    entry = {}
    entry['category'] = category
    entry['feed'] = feed_id
    entry['language'] = language

    # the easy part: the must have
    try:
        # article original link
        entry['link'] = e.link.strip()
        # article title
        if e.title_detail.type != 'text/plain':
            entry['title'] = hparser.unescape(e.title.strip())
        else:
            entry['title'] = e.title.strip()
    except AttributeError as k:
        print k
        entry['error'] = k

    # article published time
    # first try parsed time info
    try:
        entry['updated'] = calendar.timegm(e.updated_parsed)
    except AttributeError as k:
        print k, "... will try attribute 'published_parsed'"
        try:
            entry['updated'] = calendar.timegm(e.published_parsed)
        except AttributeError as k:
            print k, "... will try attibutes 'update' and 'published'"
            entry['error'] = '%s\n%s' % (
                entry['error'], 'no parsed update or published')
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
                    raise ValueError(
                        "attribute updated/published has no value")
            except ValueError as k:
                print k
                entry['error'] = '%s\n%s' % (entry['error'], k)
                raise Exception(
                    '----- ERROR: entry %s has no publication info!' % entry['title'])
            except AttributeError as k:
                print k
                entry['error'] = '%s\n%s' % (
                    entry['error'], 'no update or published')
                raise Exception(
                    '----- ERROR: entry %s has no publication info!' % entry['title'])

    # article's summary
    try:
        entry['summary'] = hparser.unescape(e.summary)
    except AttributeError as k:
        print k, '... probably this has no summary'

    def store_thumbnail(stored_at, image):
        """
        docs needed!
        """
        if thumbnail.is_thumbnail(image):
            width, height = thumbnail.get_image_size(image)
            stored_at.append({'url': image, 'width': width, 'height': height})
        else:
            rand = random.randint(0, 1000000)
            thumbnail_name = 'thumbnail_%s_%s_%i' % (
                entry['language'], entry['updated'], rand)
            image_shrinked = thumbnail.generate_thumbnail(
                image, thumbnail_name)
            width, height = thumbnail.get_image_size(image_shrinked)
            stored_at.append(
                {'url': image_shrinked, 'width': width, 'height': height})
    entry['summary'] = None if not entry['summary'] else entry['summary']

    # article's thumbnail
    # e.g. [{'url':
    # u'http://l.yimg.com/bt/api/res/1.2/SC7vBu0RS0PXeIctqYqbnw--/YXBwaWQ9eW5ld3M7Zmk9ZmlsbDtoPTg2O3E9ODU7dz0xMzA-/http://media.zenfs.com/pt_BR/News/AFP/photo_1374358063998-1-HD.jpg',
    # 'width': u'130', 'type': u'image/jpeg', 'height': u'86'}]
    try:
        entry['thumbnails'] = e.media_content
    except AttributeError as k:
        print k, '... will try media_thumbnail'
        try:
            entry['thumbnails'] = e.media_thumbnail
        except AttributeError as k:
            print k, '... will try thumbnail'
            try:
                for attribute in e:
                    if 'thumbnail' in attribute:
                        # currently set thumbnail to None if its a dictionary
                        thumbnail_embedded = e.attribute if isinstance(
                            e.attribute, str) else None
                        if thumbnail_embedded:
                            width, height = thumbnail.get_image_size(
                                thumbnail_embedded)
                            entry['thumbnails'] = [
                                {'url': thumbnail_embedded, 'width': width, 'height': height}]
                            break
                if 'thumbnails' not in entry:
                    raise AttributeError(
                        "cannot find 'thumbnail'-like attribute")
            except AttributeError as k:
                print k, '... will try summary, if available'
                entry['thumbnails'] = []
                if 'summary' in entry:
                    soup = BeautifulStoneSoup(entry['summary'])
                    if soup.img:
                        if soup.img.get('src'):
                            images = soup.img['src']
                            if isinstance(images, str):
                                store_thumbnail(entry['thumbnails'], images)
                            elif isinstance(images, list):
                                for image in images:
                                    store_thumbnail(entry['thumbnails'], image)
                if 'thumbnails' not in entry:
                    print 'cannot find thumbnails in summary ... will try links!'
                    try:
                        links = e.links
                        for link in links:
                            if 'type' in link and 'image' in link.type:
                                if 'href' in link:
                                    store_thumbnail(
                                        entry['thumbnails'], link.href)
                        if 'thumbnails' not in entry:
                            raise AttributeError("no image found in 'links'")
                    except AttributeError as k:
                        print k, '... Oooops! cannot find thumbnails!'
    entry['thumbnails'] = None if not entry[
        'thumbnails'] else entry['thumbnails']

    # article's big images
    entry['big_images'] = []
    if 'summary' in entry:
        soup = BeautifulStoneSoup(entry['summary'])
        if soup.img:
            if soup.img.get('src'):
                images = soup.img['src']
                if isinstance(images, str):
                    if not thumbnail.is_thumbnail(images):
                        width, height = thumbnail.get_image_size(images)
                        entry['big_images'].append(
                            {'url': images, 'width': width, 'height': height})
                elif isinstance(images, list):
                    for image in images:
                        if not thumbnail.is_thumbnail(image):
                            width, height = thumbnail.get_image_size(image)
                            big_image = {
                                'url': image, 'width': width, 'height': height}
                            if big_image not in entry['big_images']:
                                entry['big_images'].append(big_image)
    try:
        links = e.links
        for link in links:
            if 'type' in link and 'image' in link.type:
                if 'href' in link:
                    width, height = thumbnail.get_image_size(link.href)
                    big_image = {
                        'url': link.href, 'width': width, 'height': height}
                    if big_image not in entry['big_images']:
                        entry['big_images'].append(big_image)
        if 'big_images' not in entry:
            raise AttributeError("no image found in 'links'")
    except AttributeError as k:
        if 'big_images' not in entry:
            print k, '... probably this has no big images!'
    entry['big_images'] = None if not entry[
        'big_images'] else entry['big_images']

    # article's author
    # e.g. Yuan Jin
    try:
        # i guess this could be a string or a list
        entry['author'] = e.author
    except AttributeError as k:
        print k, '... probably this has no author'

    # article's source
    # e.g. {'href': u'http://www.reuters.com/', 'title': u'Reuters'}
    try:
        entry['source'] = e.source
    except AttributeError as k:
        print k, '... probably this has no source'

    # article's tags
    # e.g. [{'term': u'Campus Party Recife 2013', 'scheme': None, 'label': None}]
    # term is usually combined with scheme to form a url; label is the name of
    # term
    try:
        entry['tags'] = e.tag
    except AttributeError as k:
        print k, '... probably this has no tags'

    return entry


def parse(feed_id=None, feed_link=None, language=None, category=None):
    """
    read rss/atom data from a given feed
    """
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
            language = language if 'language' not in d else d.language
            entries = [read_entry(e, language, category, feed_id)
                       for e in d['entries']]
            return filter(validate_time, entries)
        else:
            return None
    else:
        return None
