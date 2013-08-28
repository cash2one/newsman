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
from config import logger
from datetime import datetime, timedelta
from data_processor import image_helper
from data_processor import summarizer
from data_processor import transcoder
from data_processor import tts_provider
import database as db_news
from feed_manager import database as db_feeds
import memory
import random
import rss_parser
import time

# CONSTANTS
from config import CATEGORY_IMAGE_SIZE
from config import DATABASE_REMOVAL_DAYS
from config import HOT_IMAGE_SIZE
from config import LANGUAGES
from config import MEMORY_EXPIRATION_DAYS
from config import THUMBNAIL_LANDSCAPE_SIZE_HIGH
from config import THUMBNAIL_LANDSCAPE_SIZE_NORMAL
from config import THUMBNAIL_LANDSCAPE_SIZE_LOW
from config import THUMBNAIL_PORTRAIT_SIZE_HIGH
from config import THUMBNAIL_PORTRAIT_SIZE_NORMAL
from config import THUMBNAIL_PORTRAIT_SIZE_LOW
from config import THUMBNAIL_STYLE


def _generate_images(image=None, entry=None, rand=None):
    """
    generate hot news, category and thumbnail images, and maybe more sizes
    """
    if not image or not entry:
        logger.error('Method malformedi!')
        return entry
    if not rand:
        # get a new rand
        rand = random.randint(0, 100000000)

    try:
        image_relative_path = '%s_%s_%s_%i' % (
            entry['language'], entry['feed_id'], entry['updated'], rand)

        # hot news image
        hot_web, hot_local = image_helper.scale_image(
            image=image, size_expected=HOT_IMAGE_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_hotnews' % image_relative_path)
        entry['hotnews_image'] = hot_web if hot_web else None
        entry['hotnews_image_local'] = hot_local if hot_local else None

        # category image
        category_web, category_local = image_helper.scale_image(
            image=image, size_expected=CATEGORY_IMAGE_SIZE, resize_by_width=True, crop_by_center=False, relative_path='%s_category' % image_relative_path)
        entry['category_image'] = category_web if category_web else None
        entry['category_image_local'] = category_local if category_local else None

        # thumbnail image
        # landscape
        if float(image['width']) / float(image['height']) >= THUMBNAIL_STYLE:
            # high resolution
            thumbnail_web, thumbnail_local = image_helper.scale_image(
                image=image, size_expected=THUMBNAIL_LANDSCAPE_SIZE_HIGH, resize_by_width=True, crop_by_center=False, relative_path='%s_thumbnail' % image_relative_path)
            if not thumbnail_web:
                # normal resolution
                thumbnail_web, thumbnail_local = image_helper.scale_image(
                    image=image, size_expected=THUMBNAIL_LANDSCAPE_SIZE_NORMAL, resize_by_width=True, crop_by_center=False, relative_path='%s_thumbnail' % image_relative_path)
                if not thumbnail_web:
                    # low resolution
                    thumbnail_web, thumbnail_local = image_helper.scale_image(
                        image=image, size_expected=THUMBNAIL_LANDSCAPE_SIZE_LOW, resize_by_width=True, crop_by_center=False, relative_path='%s_thumbnail' % image_relative_path)
        else:  # portrait
            # high resolution
            thumbnail_web, thumbnail_local = image_helper.scale_image(
                image=image, size_expected=THUMBNAIL_PORTRAIT_SIZE_HIGH, resize_by_width=True, crop_by_center=True, relative_path='%s_thumbnail' % image_relative_path)
            if not thumbnail_web:
                # normal resolution
                thumbnail_web, thumbnail_local = image_helper.scale_image(
                    image=image, size_expected=THUMBNAIL_PORTRAIT_SIZE_NORMAL, resize_by_width=True, crop_by_center=True, relative_path='%s_thumbnail' % image_relative_path)
                if not thumbnail_web:
                    # low resolution
                    thumbnail_web, thumbnail_local = image_helper.scale_image(
                        image=image, size_expected=THUMBNAIL_PORTRAIT_SIZE_LOW, resize_by_width=True, crop_by_center=True, relative_path='%s_thumbnail' % image_relative_path)
        entry['thumbnail_image'] = thumbnail_web if thumbnail_web else None
        entry['thumbnail_image_local'] = thumbnail_local if thumbnail_local else None
    except Exception as k:
        logger.error(str(k))
        pass
    return entry


# TODO: replace primitive exception recording with logger
def _get_tts(entry=None, rand=None):
    """
    get tts from the provider
    """
    if not entry:
        logger.error('Method malformed!')
        return entry
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
        logger.error(str(k))
        entry['error'].append(str(k) + '\n')
        entry['mp3'] = None
        entry['mp3_local'] = None
    return entry


def _value_added_process(entries=None, language=None, transcoder_type='chengdujin'):
    """
    add more value to an entry
    tts, transcode, images, redis_entry_expiration, database_entry_expiration
    """
    if not entries:
        logger.error('Method malformed!')
        return None
    if not language or language not in LANGUAGES:
        logger.error("Language not found or not supported!")
        return None

    updated_entries = []
    for i, entry in enumerate(entries):
        try:
            logger.info('... Working on %i of %d ...' % (i+1, len(entries)))
            logger.info(entry['title'])
            logger.info(entry['link'])

            # [MUST-HAVE] transcoding
            # get a random int from 100 million possibilities
            rand = random.randint(0, 100000000)
            transcoded_relative_path = '%s_%s_%s_%i' % (
                entry['language'], entry['feed_id'], entry['updated'], rand)

            # high chances transcoder cannot work properly
            entry['transcoded'], entry['transcoded_local'], raw_transcoded_content, images_from_transcoded = transcoder.convert(
                entry['language'], entry['title'], entry['link'], transcoder_type, transcoded_relative_path)

            if entry['transcoded']:
                # [OPTIONAL] summary
                summary_found = summarizer.extract(
                    entry['summary'], raw_transcoded_content, entry['language'])
                if summary_found:
                    entry['summary'] = summary_found

                # [OPTIONAL] images
                # process images found in the transcoded data
                if images_from_transcoded:
                    # images from transcoded are already normalized
                    entry['images'].extend(images_from_transcoded)
                    # remove duplicated images
                    images_deduped = image_helper.dedupe_images(
                        entry['images']) if entry.has_key('images') and entry['images'] else None
                    # be cautious dedupe_images might return None if network
                    # sucks
                    if images_deduped:
                        entry['images'] = images_deduped

                # make images none if nothing's there, instead of a []
                entry['images'] = entry['images'] if entry.has_key(
                    'images') and entry['images'] else None

                # [OPTIONAL] generate 3 types of images: thumbnail,
                # category image and hot news image
                if entry.has_key('images') and entry['images']:
                    biggest = image_helper.find_biggest_image(entry['images'])
                    if biggest:
                        entry = _generate_images(biggest, entry, rand)
                # for older version users
                entry['image'] = entry['thumbnail_image']['url'] if entry.has_key(
                    'thumbnail_image') and entry['thumbnail_image'] else None

                # [OPTIONAL] google tts not for indonesian
                if entry['language'] != 'ind':
                    # you dont get None in _get_tts
                    # at worst the original entry is returned
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

                # [OPTIONAL] if logger is used, this could be removed
                entry['error'] = entry['error'] if entry['error'] else None

                # [MUST-HAVE] update new entry to db_news
                # each entry is added with _id
                entry = db_news.update(entry)
                if entry:
                    # [MUST-HAVE] store in memory
                    result = memory.update(entry)
                    if result:
                        updated_entries.append(entry)
                    else:
                        logger.error('Error found in updating memory')
                        continue
                else:
                    logger.error('Error found in updating to news database')
                    continue
            else:
                logger.error('Error found in transcoding')
                continue
        except Exception as k:
            logger.error(str(k))
            continue
    # the FINAL return
    if updated_entries:
        return True
    else:
        logger.error('No entry got value added!')
        return False


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
        logger.error('Method malformed!')
        return None

    try:
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

            if entries:
                # filter out existing entries in db_news
                # there are some possible exceptions -- yet let it be
                entries = db_news.dedup(entries, language)

                if entries:
                    # and do tts, big_images, image as well as transcode.
                    result = _value_added_process(entries, language, transcoder_type)
                    if result:
                        # feed_title, etag and modified to db_feeds
                        # only feed_id is necessary, others are optional
                        # **kwargs
                        result = db_feeds.update(
                            feed_id=feed_id, status=status_new, feed_title=feed_title_new, etag=etag_new, modified=modified_new)
                        if result:
                            return result
                        else:
                            logger.error(
                                'Error found updating feeds database')
                            return None
                    else:
                        logger.error('Error found adding value to entries')
                        return None

                else:
                    logger.info('Nothing from RSS is found new!')
                    return None
            else:
                logger.info('Nothing from RSS is updated!')
                return None
        else:
            logger.warning('Register feed in database before updating!')
            return None
    except Exception as k:
        logger.error(str(k))
        return None
