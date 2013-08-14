#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
rss is the interface to rss parsing, processing and storing.
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 20, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import calendar
from datetime import datetime, timedelta
from data_processor import summarizer
from data_processor import transcoder
from data_processor import tts_provider
from data_processor import image_helper
from feed_manager import database as db_feeds
import random
from scraper import database as db_news
from scraper import memory
from scraper import rss_parser
import time

# CONSTANTS
from config import CATEGORY_IMAGE_SIZE
from config import DATABASE_REMOVAL_DAYS
from config import HOT_IMAGE_SIZE
from config import LANGUAGES
from config import MEMORY_EXPIRATION_DAYS
from config import THUMBNAIL_LANDSCAPE_SIZE
from config import THUMBNAIL_PORTRAIT_SIZE
from config import THUMBNAIL_STYLE


def _generate_images(image=None, entry=None, rand=None):
    """
    generate hot news, category and thumbnail images, and maybe more sizes
    """
    if not image or not entry:
        raise Exception('[rss._generate_images] ERROR: Cannot generate images from void content!')
    if not rand:
        # get a new rand
        rand = random.randint(0, 100000000)

    image_relative_path = '%s_%s_%s_%i' % (
        entry['language'], entry['feed_id'], entry['updated'], rand)

    # hot news image
    hot_web, hot_local = image_helper.scale_image(
        image=image, size_expected=HOT_IMAGE_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_hotnews' % image_relative_path)
    entry['hot_news_image'] = hot_web if hot_web else None
    entry['hot_news_image_local'] = hot_local if hot_local else None

    # category image
    category_web, category_local = image_helper.scale_image(
        image=image, size_expected=CATEGORY_IMAGE_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_category' % image_relative_path)
    entry['category_image'] = category_web if category_web else None
    entry['category_image_local'] = category_local if category_local else None

    # thumbnail image
    # landscape
    if float(image['width']) / float(image['height']) >= THUMBNAIL_STYLE:
        thumbnail_web, thumbnail_local = image_helper.scale_image(
            image=image, size_expected=THUMBNAIL_LANDSCAPE_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_thumbnail' % image_relative_path)
    else:  # portrait
        thumbnail_web, thumbnail_local = image_helper.scale_image(
            image=image, size_expected=THUMBNAIL_PORTRAIT_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_thumbnail' % image_relative_path)
    entry['thumbnail_image'] = thumbnail_web if thumbnail_web else None
    entry['thumbnail_image_local'] = thumbnail_local if thumbnail_local else None

    return entry


# TODO: replace primitive exception recording with logging
def _get_tts(entry=None, rand=None):
    """
    get tts from the provider
    """
    if not entry:
        raise Exception('[rss._get_tts] ERROR: Cannot generate tts from void content!')
    if not rand:
        # get a new rand
        rand = random.randint(0, 100000000)

    try:
        tts_relative_path = '%s_%s_%s_%i.mp3' % (
            entry['language'], entry['feed_id'], entry['updated'], rand)
        read_content = '%s. %s' % (entry['title'], entry[
                                   'summary'] if entry.has_key('summary') and entry['summary'] else "")
        entry['mp3'], entry['mp3_local'] = tts_provider.google(
            entry['language'], read_content, tts_relative_path)
    except Exception as k:
        print '[rss._get_tts]', k, ':%s' % entry['link']
        entry['error'].append(k + '\n')
        entry['mp3'] = None
        entry['mp3_local'] = None
    return entry


def _value_added_process(entries=None, language=None, transcoder_type='chengdujin'):
    """
    add more value to an entry
    tts, transcode, images, redis_entry_expiration, database_entry_expiration
    """
    if not entries:
        return None
    if not language or language not in LANGUAGES:
        raise Exception("[rss._value_added_process] ERROR: language not found or not supported!")

    for entry in entries:
        try:
            print entry['title']
            print entry['link']
            # [MUST-HAVE] transcoding
            # get a random int from 100 million possibilities
            rand = random.randint(0, 100000000)
            transcoded_relative_path = '%s_%s_%s_%i' % (
                entry['language'], entry['feed_id'], entry['updated'], rand)

            # high chances transcoder cannot work properly
            entry['transcoded'], entry['transcoded_local'], raw_transcoded_content, images_from_transcoded = transcoder.convert(
                entry['language'], entry['title'], entry['link'], transcoder_type, transcoded_relative_path)

            # [MUST-HAVE] summary
            entry['summary'] = summarizer.extract(
                entry['summary'], raw_transcoded_content, entry['language'])

            # process images found in the transcoded data
            if images_from_transcoded:
                # images from transcoded are already normalized
                entry['images'].extend(images_from_transcoded)
                # remove duplicated images
                entry['images'] = image_helper.dedupe_images(
                    entry['images']) if entry.has_key('images') and entry['images'] else None

            # make images none if nothing's there, instead of a []
            entry['images'] = entry['images'] if entry.has_key(
                'images') and entry['images'] else None

            # [OPTIONAL] generate 3 types of images: thumbnail,
            # category image and hot news image
            if entry.has_key('images') and entry['images']:
                biggest = image_helper.find_biggest_image(entry['images'])
                if biggest:
                    try:
                        entry = _generate_images(biggest, entry, rand)
                        # for older version users
                        entry['image'] = entry['thumbnail_image']['url'] if entry.has_key(
                            'thumbnail_image') and entry['thumbnail_image'] else None
                    except IOError as k:
                        entry['error'].append(str(k) + '\n')

            # [OPTIONAL] google tts not for indonesian
            if entry['language'] != 'ind':
                entry = _get_tts(entry, rand)

            # [MUST-HAVE] add expiration data
            def _expired(updated, days_to_deadline):
                """
                compute expiration information
                return time string and unix time
                """
                deadline = datetime.utcfromtimestamp(
                    updated) + timedelta(days=days_to_deadline)
                return time.asctime(time.gmtime(calendar.timegm(deadline.timetuple())))

            entry['memory_expired'] = _expired(
                entry['updated'], MEMORY_EXPIRATION_DAYS)
            entry['database_expired'] = _expired(
                entry['updated'], DATABASE_REMOVAL_DAYS)

            # [OPTIONAL] if logging is used, this could be removed
            entry['error'] = entry['error'] if entry['error'] else None

            # [MUST-HAVE] update new entry to db_news
            # each entry is added with _id
            entry = db_news.update(entry)

            # [MUST-HAVE] store in memory
            memory.update(entry)

            print
            print
        except Exception as k:
            print '[rss._value_added_process:191L]', k
            print
            print


# TODO: code to remove added items if things suck at database/memory
def update(feed_link=None, feed_id=None, language=None, categories=None, transcoder_type='chengdujin'):
    """
    update could be called
    1. from task procedure: feed_id
    2. after an rss is added: feed_id
    3. manually for testing purpose: feed_link, language
    Note categories are kept for manual testing
    """
    if not feed_id and not (feed_link and language):
        raise Exception(
            "[rss.update] ERROR: Method signature not well formed!")

    # try to find the feed in database
    if feed_id:
        feed = db_feeds.get(feed_id=feed_id)
    else:
        feed = db_feeds.get(feed_link=feed_link, language=language)

    if feed:
        # read latest feed info from database
        feed_id = str(feed['_id'])
        feed_link = feed['feed_link']
        language = feed['language']
        categories = feed['categories']
        transcoder_type = feed['transcoder']
        feed_title = feed['feed_title'] if 'feed_title' in feed else None
        etag = feed['etag'] if 'etag' in feed else None
        modified = feed['modified'] if 'modified' in feed else None

        # parse rss reading from remote rss servers
        entries, status_new, feed_title_new, etag_new, modified_new = rss_parser.parse(
            feed_link, feed_id, feed_title, language, categories, etag, modified)

        # filter out existing entries in db_news
        # there are some possible exceptions -- yet let it be
        entries = db_news.dedup(entries, language)

        # and do tts, big_images, image as well as transcode.
        _value_added_process(entries, language, transcoder_type)

        # feed_title, etag and modified to db_feeds
        # only feed_id is necessary, others are optional **kwargs
        db_feeds.update(feed_id=feed_id, status=status_new,
                        feed_title=feed_title_new, etag=etag_new, modified=modified_new)
    else:
        raise Exception('[rss.update] ERROR: Register feed in database before updating!')
