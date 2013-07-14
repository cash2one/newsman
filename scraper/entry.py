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
sys.path.append('../')

from BeautifulSoup import BeautifulStoneSoup
import calendar
from administration.config import Collection
from datetime import timedelta, datetime
from administration.config import db
import feedparser
from administration.config import hparser
import Image
import random
from administration.config import rclient
from cStringIO import StringIO
import time
from data_processor import transcoder
import urllib2

from administration.config import LANGUAGES
from administration.config import MEMORY_RESTORATION_DAYS
from administration.config import REDIS_ENTRY_EXPIRATION
from administration.config import THUMBNAIL_LOCAL_DIR
from administration.config import THUMBNAIL_SIZE
from administration.config import THUMBNAIL_WEB_DIR


def update_memory(added_items=None, language=None, category=None, feed_id=None):
    ''''''
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


def update_database(entries=None, language=None):
    ''''''
    print '>>> update_database'
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
                random_code = random.random()
                # create a proper name for url encoding
                safe_category = (entry['category']).strip().replace(" ", "-")
                transcoded_path, big_images = transcoder.transcode(entry['language'], entry['title'], entry[
                                                                   'link'], '%s_%s_%s_%f' % (entry['language'], safe_category, entry['updated'], random_code))
                if not transcoded_path:
                    raise Exception('cannot transcode %s' % entry['link'])
                else:
                    entry[
                        'transcoded'] = 'None' if not transcoded_path else transcoded_path
                    entry[
                        'big_images'] = 'None' if not big_images else big_images
                    if entry['image'] == 'None' and entry['big_images'] != 'None':
                        entry['image'] = []
                        bimage_max = 0, 0
                        for bimage in entry['big_images']:
                            bimage_current = transcoder.get_image_size(bimage)
                            if bimage_current > bimage_max:
                                thumbnail_relative_path = base64.urlsafe_b64encode(
                                    '%s.jpeg' % bimage)
                                if len(thumbnail_relative_path) > 200:
                                    thumbnail_relative_path = thumbnail_relative_path[
                                        -200:]
                                try:
                                    thumbnail_url = generate_thumbnail(
                                        bimage, thumbnail_relative_path)
                                    entry['image'] = thumbnail_url
                                    bimage_max = bimage_current
                                except IOError as e:
                                    entry['big_images'].remove(bimage)
                    elif entry['image'] and isinstance(entry['image'], list):
                        entry['image'] = entry['image'][0]
                    # then save to database
                    entry_id = col.save(entry)
                    entry['_id'] = str(entry_id)
                    added_entries.append((entry, REDIS_ENTRY_EXPIRATION))
                    print 'processed %s' % entry['title']
            except Exception as e:
                print str(e)
        else:
            print 'Find a duplicate for %s' % entry['title']
    return added_entries


def generate_thumbnail(image_url, relative_path):
    ''''''
    if not image_url or not relative_path:
        return None
    image_web = StringIO(urllib2.urlopen(image_url).read())
    image_pil = Image.open(image_web)
    # generate thumbnail
    if image_pil.size > THUMBNAIL_SIZE:
        image_thumbnail_local_path = '%s%s.jpeg' % (
            THUMBNAIL_LOCAL_DIR, relative_path)
        image_thumbnail_web_path = '%s%s.jpeg' % (
            THUMBNAIL_WEB_DIR, relative_path)
        image_pil.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        image_pil = image_pil.convert('RGB')
        image_pil.save(image_thumbnail_local_path, 'JPEG')
        return image_thumbnail_web_path
    else:
        return image_url


def read_entry(e=None, language=None, category=None, feed_id=None):
    ''''''
    if not e:
        return 1
    entry = {}
    entry['language'] = language
    entry['category'] = '%s' % category
    entry['feed'] = '%s' % feed_id
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
        if soup.img:
            img = soup.img['src']
            if isinstance(img, str):
                thumbnail_relative_path = base64.urlsafe_b64encode(
                    '%s.jpeg' & img)
                if len(thumbnail_relative_path) > 200:
                    thumbnail_relative_path = thumbnail_relative_path[-200:]
                thumbnail_url = generate_thumbnail(
                    img, thumbnail_relative_path)
                entry['image'].append(thumbnail_url)
            elif isinstance(img, list):
                for im in img:
                    thumbnail_relative_path = base64.urlsafe_b64encode(
                        '%s.jpeg' % im)
                    if len(thumbnail_relative_path) > 200:
                        thumbnail_relative_path = thumbnail_relative_path[
                            -200:]
                    thumbnail_url = generate_thumbnail(
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
