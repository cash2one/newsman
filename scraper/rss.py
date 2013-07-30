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

from administration import database as db_feeds
import calendar
import database as db_news
from datetime import datetime, timedelta
from data_processor import transcoder
from data_processor import tts_provider
import Image
from image_processor import image_helper
from image_processor import thumbnail
import memory
import random
import rss_parser
from cStringIO import StringIO
import time
import urllib2

from administration.config import CATEGORY_IMAGE_SIZE
from administration.config import db_news_REMOVAL_DAYS
from administration.config import HOT_IMAGE_SIZE
from administration.config import LANGUAGES
from administration.config import MEMORY_EXPIRATION_DAYS
from administration.config import MIN_IMAGE_SIZE
from administration.config import THUMBNAIL_IMAGE_SIZE


def _value_added_process(entries=None, language=None):
    """
    add more value to an entry
    tts, transcode, images, redis_entry_expiration, db_news_entry_expiration
    """
    if not entries:
        return None
    if not language or language not in LANGUAGES:
        raise Exception("ERROR: language not found or not supported!")

    entries_new = []
    for entry in entries:
        # get a random int from 100 million possibilities
        try:
            # [MUST-HAVE] transcoding
            rand = random.randint(0, 100000000)
            transcoded_relative_path = '%s_%s_%s_%i' % (entry['language'], entry['feed_id'], entry['updated_parsed'], rand)
            # high chances transcoder cannot work properly
            entry['transcoded'], entry['transcoded_local'], images_from_transcoded = transcoder.transcode(entry['language'], entry['title'], entry['link'], transcoded_relative_path)

            # [OPTIONAL] find images
            # process images found in the image_list tag of transcoded page
            images = image_helper.normalize(images_from_transcoded)
            if images:
                entry['images'].extend(images)
            # or find the image directly from the content of transcoded page
            # images = image_helper.find_images(entry['transcoded_local'])

            #if images:
            #    entry['images'] = entry['images'] if entry.has_key('images') and entry['images'] else []
            #    entry['images'].extend(images)
            entry['images'] = image_helper.dedupe_images(entry['images']) if entry.has_key('images') and entry['images'] else None

            # [OPTIONAL] generate 3 types of images: thumbnail, category image and hot news image
            if entry.has_key('images') and entry['images']:
                biggest = image_helper.find_biggest_image(entry['images'])
                if biggest:
                    try:
                        rand = random.randint(0, 100000000)
                        image_relative_path = '%s_%s_%s_%i' % (entry['language'], entry['feed_id'], entry['updated_parsed'], rand)
                        image_downloaded = StringIO(urllib2.urlopen(biggest['url']).read())
                        image_data = Image.open(image_downloaded)
                        image_data_category = image_data
                        image_data_thumbnail = image_data

                        # hot news image
                        hot_web, hot_local = image_helper.scale_image(image=biggest, image_data=image_data, size_expected=HOT_IMAGE_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_hotnews' % image_relative_path)
                        entry['hot_news_image'] = hot_web if hot_web else None
                        entry['hot_news_image_local'] = hot_local if hot_local else None
                        # category image
                            
                        category_web, category_local = image_helper.scale_image(image=biggest, image_data=image_data_category, size_expected=CATEGORY_IMAGE_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_category' % image_relative_path)
                        entry['category_image'] = category_web if category_web else None
                        entry['category_image_local'] = category_local if category_local else None
                        # new item thumbnail image
                        thumbnail_web, thumbnail_local = image_helper.scale_image(image=biggest, image_data=image_data_thumbnail, size_expected=THUMBNAIL_IMAGE_SIZE, resize_by_width=True, crop_by_center=True, relative_path='%s_thumbnail' % image_relative_path)
                        entry['thumbnail_image'] = thumbnail_web if thumbnail_web else None
                        entry['thumbnail_image_local'] = thumbnail_local if thumbnail_local else None 
                    except IOError as k:
                        entry['error'].append(str(k) + '\n')

            # [OPTIONAL] google tts not for indonesian
            if entry['language'] != 'ind':
                try:
                    tts_relative_path = '%s_%s_%s_%i.mp3' % (
                        entry['language'], entry['feed_id'], entry['updated_parsed'], rand)
                    entry['mp3'], entry['mp3_local'] = tts_provider.google(
                        entry['language'], entry['title'], tts_relative_path)
                except Exception as k:
                    print k, '... cannot generate TTS for %s' % entry['link']
                    entry['error'].append(k + '\n')
                    entry['mp3'] = None
                    entry['mp3_local'] = None

            # [MUST-HAVE] add expiration data
            def _expired(updated_parsed, days_to_deadline):
                """
                compute expiration information
                return time string and unix time
                """
                deadline = datetime.utcfromtimestamp(
                    updated_parsed) + timedelta(days=days_to_deadline)
                return time.asctime(time.gmtime(calendar.timegm(deadline.timetuple())))

            entry['memory_expired'] = _expired(
                entry['updated_parsed'], MEMORY_EXPIRATION_DAYS)
            entry['db_news_expired'] = _expired(
                entry['updated_parsed'], db_news_REMOVAL_DAYS)

            entry['error'] = entry['error'] if entry['error'] else None
            entries_new.append(entry)
            print
            print
        except Exception as k:
            print k
    return entries_new


# TODO: code to remove added items if things suck at db_news/memory
def update(feed_link=None, feed_id=None, language=None, categories=None):
    """
    update could be called
    1. from task procedure: feed_id
    2. after an rss is added: feed_id
    3. manually for testing purpose: feed_link, language
    Note. categories are ids of category item
    Notel categories are kept for manual testing
    """
    if not feed_id or not (feed_link and language) :
        raise Exception(
            "ERROR: Method signature not well formed!")

    if feed_id:
        feed = db_feeds.get(feed_id=feed_id)
    else 
        feed = db_feeds.get(feed_link=feed_link, language=language)

    feed_id = str(feed['_id']) if feed else feed_id
    feed_link = feed['feed_link'] if feed else feed_link
    language = feed['language'] if feed else language
    categories = feed['categories'] if feed else categories
    feed_title = feed['feed_title'] if feed and 'feed_title' in feed else None
    etag = feed['etag'] if feed and 'etag' in feed else None
    modified = feed['modified'] if feed and 'modified' in feed else None

    # parse rss reading from remote rss servers
    entries, status_new, feed_title_new, etag_new, modified_new = rss_parser.parse(
        feed_link, feed_id, feed_title, language, categories, etag, modified)

    # filter out existing entries in db_news
    # there are some possible exceptions -- yet let it be
    entries = db_news.dedup(entries, language)
    # and do tts, big_images, image as well as transcode.
    entries = _value_added_process(entries, language)

    # update new entries to db_news
    # each entry is added with _id
    entries = db_news.update(entries, language)
    # and some data, like feed_title, etag and modified to db_feeds
    # only feed_id is necessary, others are optional **kwargs
    db_feeds.update(feed_id=feed_id, status=status_new, feed_title=feed_title_new, etag=etag_new, modified=modified_new)

    # store in memory
    memory.update(entries, language, categories)
    return entries
