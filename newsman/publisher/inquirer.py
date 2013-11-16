#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
inquirer find news from memory and database
"""
#@author chengdujin
#@contact chengdujin@gmail.com
#@created Jan 12, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

from bson.objectid import ObjectId
import hashlib
import json
from settings import Collection, db
from settings import logger
from settings import rclient, ConnectionError
import os
import urllib2

# CONSTANTS
from settings import CODE_BASE
from settings import COUNTRIES
from settings import FEED_REGISTRAR
from settings import HOTNEWS_TITLE_AR
from settings import HOTNEWS_TITLE_EN
from settings import HOTNEWS_TITLE_JA
from settings import HOTNEWS_TITLE_IN
from settings import HOTNEWS_TITLE_PT
from settings import HOTNEWS_TITLE_TH
from settings import HOTNEWS_TITLE_ZH
from settings import LANGUAGES
from settings import LOGO_PUBLIC_PREFIX

HOTNEWS_TITLE = {'en': HOTNEWS_TITLE_EN, 'ja': HOTNEWS_TITLE_JA, 'th': HOTNEWS_TITLE_TH, 'pt': HOTNEWS_TITLE_PT, 'in':
                 HOTNEWS_TITLE_IN, 'ar': HOTNEWS_TITLE_AR, 'zh': HOTNEWS_TITLE_ZH}


def get_portal(language=None, country=None, categories=None):
    """
    get a list of text and images for feed/rss and labels
    """

    if not language or not language:
        return None
    if language not in LANGUAGES:
        return None
    if country not in COUNTRIES:
        return None

    search_limit = 70
    images_limit = 1
    portal_data = {}
    categories = urllib2.unquote(categories.strip()).split(',')

    for user_subscription in categories:
        user_subscription = user_subscription.replace('+', ' ')
        category, feed = user_subscription.split('*|*')
        entries = get_latest_entries(
            language=language, country=country, category=category, feed=feed, limit=search_limit)
        # 'category A': [{'title':'xxx', 'image':'http://yyy.com/zzz.jpg'}]
        # image: category_image
        portal_data[user_subscription] = []
        text_image_item = None
        for entry in entries:
            # only one text_image is necessary
            if 'text_image' in entry and entry['text_image'] and not text_image_item:
                if isinstance(entry['text_image'], str):
                    entry['text_image'] = eval(entry['text_image'])
                text_image = entry['text_image']
                text_image_item = {
                    'title': entry['title'], 'image': text_image, 'updated': entry['updated']}

            # search for category_image
            if 'category_image' in entry and entry['category_image'] and entry['category_image'] != 'None' and entry['category_image'] != 'null':
                if isinstance(entry['category_image'], str):
                    entry['category_image'] = eval(entry['category_image'])
                item = {'title': entry['title'], 'image': entry[
                    'category_image'], 'updated': entry['updated']}
                portal_data[user_subscription].append(item)
                # limit the number of category_image to
                if len(portal_data[user_subscription]) == images_limit:
                    break

        # can't find any category image, use text image instead, if available
        if len(portal_data[user_subscription]) < 1 and text_image_item:
            portal_data[user_subscription].append(text_image_item)

    # special formatting for android-end
    output = []
    for i, k, v in enumerate(portal_data.iteritems()):
        if k and v:
            category, feed = k.split('*|*')
            output.append(
                {'Category': category, 'Feed': feed, 'Images': v, 'order': i})
    return {'Categories': output}


def get_categories(language=None, country=None, version=None):
    """
    get categories and feeds and labels in those categories
    """

    if not language or not country:
        return None
    if language not in LANGUAGES:
        return None
    if country not in COUNTRIES:
        return None

    col = Collection(db, FEED_REGISTRAR)
    items = col.find({'countries': country})
    if items:
        categories = {}
        for item in items:
            # add rss to the category dictionary
            for category in item['categories']:
                if category.startswith(country):
                    category_name = category.replace('%s::' % country, '')
                    if category_name not in categories:
                        categories[category_name] = []

                    if 'feed_logo' in item and item['feed_logo']:
                        feed_format = {'order': len(categories[category_name]), 'text': item[
                            'feed_title'], 'image': item['feed_logo']}
                    else:
                        feed_format = {
                            'order': len(categories[category_name]), 'text': item['feed_title']}
                    if feed_format not in categories[category_name]:
                        categories[category_name].append(feed_format)

            if 'labels' in item and item['labels']:
                # add label to the category dictionary
                for label in item['labels']:
                    if label.startswith(country):
                        label_split = label.replace(
                            '%s::' % country, "").split('::')
                        category_name = label_split[0]
                        label_name = label_split[1]
                        if category_name not in categories:
                            categories[category_name] = []

                        label_name_shrinked = label_name.replace(' ', '')
                        label_image = {'url': '%s%s_%s/%s.png' % (
                            LOGO_PUBLIC_PREFIX, language, country, label_name_shrinked), 'width': 71, 'height': 60}
                        label_format = {
                            'order': len(categories[category_name]), 'text': label_name, 'image': label_image}

                        LABEL_ADDED = False
                        for label_format_added in categories[category_name]:
                            if label_format_added['text'] == label_name:
                                LABEL_ADDED = True
                                break
                        if not LABEL_ADDED:
                            categories[category_name].append(label_format)
        # reformat
        output = []
        for k, v in categories.iteritems():
            category_format = {'text': k}
            output.append({'Category': category_format, 'Feeds': v})
        version_latest = hashlib.md5(
            json.dumps(categories, sort_keys=True)).hexdigest()

        # compare versions
        if not version or version != version_latest:
            return {'Categories': output, 'Version': version_latest}
        else:
            return None
    else:
        return None


def get_latest_entries(language=None, country=None, category=None, feed=None, limit=10, start_id=None):
    """
    find out latest news items
    search entries newer than start_id
    """

    if not language or not country or not category or not feed:
        return None
    if language not in LANGUAGES:
        return None
    if country not in COUNTRIES:
        return None
    if limit < 0:
        return None
    # limit the number of items
    if limit > 100:
        limit = 100

    # return list
    entries = []
    category_name = '%s::%s' % (country, category)
    label_name = '%s::%s::%s' % (country, category, feed)

    try:
        # check if redis is alive
        rclient.ping()

        class_name = 'news::%s::%s' % (language, feed)
        if not rclient.exists(class_name):
            class_name = 'news::%s::%s' % (language, label_name)
        else:
            # reset label_name as the flag
            label_name = None

        # get the latest entries
        entry_ids_total = rclient.zcard(class_name)

        if entry_ids_total:  # memory (partially) meets the limit
            if entry_ids_total >= limit:
                entry_ids = rclient.zrevrange(class_name, 0, limit - 1)

                dirty_expired_ids = []
                for entry_id in entry_ids:
                    if start_id and entry_id == start_id:
                        return entries

                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        entries.append(eval(entry_id_in_memory))
                    else:
                        dirty_expired_ids.append(entry_id)
            else:  # memory + database
                entry_ids = rclient.zrevrange(
                    class_name, 0, entry_ids_total - 1)

                last_entry_in_memory = None
                dirty_expired_ids = []
                for entry_id in entry_ids:
                    if start_id and entry_id == start_id:
                        return entries

                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        last_entry_in_memory = eval(entry_id_in_memory)
                        entries.append(last_entry_in_memory)
                    else:
                        dirty_expired_ids.append(entry_id)

                # compute boundary variables
                tmp = last_entry_in_memory['updated']
                last_entry_in_memory_updated = float(tmp) if tmp else None
                limit_in_database = limit - len(entries)

                # database
                items = []
                col = Collection(db, language)
                # query only one of its values
                if label_name:
                    feeds = Collection(db, FEED_REGISTRAR)
                    feed_lists = feeds.find(
                        {'labels': label_name}, {'feed_title': 1})
                    feed_names = [feed_list['feed_title']
                                  for feed_list in feed_lists]
                    items = col.find({'updated': {'$lt': last_entry_in_memory_updated}, 'feed': {'$in': feed_names}}).sort(
                        'updated', -1).limit(limit_in_database)
                else:
                    items = col.find({'updated': {'$lt': last_entry_in_memory_updated}, 'feed': feed}).sort(
                        'updated', -1).limit(limit_in_database)

                for item in items:
                    if start_id and str(item['_id']) == start_id:
                        return entries

                    # string-ify all the values: ObjectId
                    new_item = {}
                    for x, y in item.iteritems():
                        if x != 'updated':
                            new_item[str(x)] = str(y)
                        new_item['updated'] = item['updated']
                    entries.append(new_item)

            # expired ids not cleaned found
            if dirty_expired_ids:
                sys.path.append(os.path.join(CODE_BASE, 'newsman'))
                from watchdog import clean_memory
                clean_memory.clean_by_items(class_name, dirty_expired_ids)
                logger.warning('Memory contains dirty expired items')

            return entries
        else:
            raise ConnectionError(
                'Find nothing about %s in memory' % class_name)
    except ConnectionError:
        # query the database
        items = []
        col = Collection(db, language)
        if label_name:
            feeds = Collection(db, FEED_REGISTRAR)
            feed_lists = feeds.find({'labels': label_name}, {'feed_title': 1})
            feed_names = [feed_list['feed_title'] for feed_list in feed_lists]
            items = col.find({'feed': {'$in': feed_names}}).sort(
                'updated', -1).limit(limit)
        else:
            items = col.find({'feed': feed}).sort('updated', -1).limit(limit)

        for item in items:
            if start_id and str(item['_id']) == start_id:
                return entries

            # string-ify all the values: ObjectId
            new_item = {}
            for x, y in item.iteritems():
                if x != 'updated':
                    new_item[str(x)] = str(y)
                new_item['updated'] = item['updated']
            entries.append(new_item)
        return entries


def get_previous_entries(language=None, country=None, category=None, feed=None, limit=10, end_id=None):
    """
    find entries before end_id
    """

    if not language or not country or not category or not feed:
        return None
    if language not in LANGUAGES:
        return None
    if country not in COUNTRIES:
        return None
    if limit < 0:
        return None
    # limit the number of items
    if limit > 100:
        limit = 100

    # return list
    entries = []
    category_name = '%s::%s' % (country, category)
    label_name = '%s::%s::%s' % (country, category, feed)

    try:
        # check if redis is alive
        rclient.ping()

        class_name = 'news::%s::%s' % (language, feed)
        if not rclient.exists(class_name):
            class_name = 'news::%s::%s' % (language, label_name)
        else:
            # reset label_name as the flag
            label_name = None

        # preprocess end_id
        entry_ids_total = rclient.zcard(class_name)
        end_id_index = 0
        END_ID_IN_MEMORY = False
        limit_in_memory = 0

        if not end_id:
            end_id_index = entry_ids_total
            if entry_ids_total:
                # end_id is assign the most recent one
                end_id = rclient.zrevrange(class_name, 0, 0)[0]
                END_ID_IN_MEMORY = True
                limit_in_memory = entry_ids_total
            else:
                end_id = None  # which is in most cases, pointless
                END_ID_IN_MEMORY = False
        else:
            end_id_index = rclient.zrank(class_name, end_id)
            END_ID_IN_MEMORY = True if end_id_index > 0 else False
            if END_ID_IN_MEMORY:
                limit_in_memory = rclient.zrank(class_name, end_id)

        if END_ID_IN_MEMORY:  # see if data in memory suffice
            if limit_in_memory >= limit:  # purely get from memory
                entry_ids = rclient.zrevrange(
                    class_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit - 1)

                dirty_expired_ids = []
                for entry_id in entry_ids:
                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        entries.append(eval(entry_id_in_memory))
                    else:
                        dirty_expired_ids.append(entry_id)
            else:  # memory + database
                # memory
                entry_ids = rclient.zrevrange(
                    class_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit_in_memory - 1)

                last_entry_in_memory = None
                dirty_expired_ids = []
                for entry_id in entry_ids:
                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        last_entry_in_memory = eval(entry_id_in_memory)
                        entries.append(last_entry_in_memory)
                    else:
                        dirty_expired_ids.append(entry_id)

                tmp = last_entry_in_memory['updated']
                last_entry_in_memory_updated = float(tmp) if tmp else None
                limit_in_database = limit - len(entries)

                # find the remaining items in database
                items = []
                col = Collection(db, language)
                # query only one of its values
                if label_name:
                    feeds = Collection(db, FEED_REGISTRAR)
                    feed_lists = feeds.find(
                        {'labels': label_name}, {'feed_title': 1})
                    feed_names = [feed_list['feed_title']
                                  for feed_list in feed_lists]
                    items = col.find({'updated': {'$lt': last_entry_in_memory_updated}, 'feed': {'$in': feed_names}}).sort(
                        'updated', -1).limit(limit_in_database)
                else:
                    items = col.find({'updated': {'$lt': last_entry_in_memory_updated}, 'feed': feed}).sort(
                        'updated', -1).limit(limit_in_database)

                for item in items:
                    # string-ify all the values: ObjectId
                    new_item = {}
                    for x, y in item.iteritems():
                        if x != 'updated':
                            new_item[str(x)] = str(y)
                        new_item['updated'] = item['updated']
                    entries.append(new_item)

            # expired ids not cleaned found
            if dirty_expired_ids:
                sys.path.append(os.path.join(CODE_BASE, 'newsman'))
                from watchdog import clean_memory
                clean_memory.clean_by_items(class_name, dirty_expired_ids)
                logger.warning('Memory contains dirty expired items')

            return entries
        else:
            raise ConnectionError(
                'Find nothing about %s in memory' % class_name)
    except ConnectionError:
        # no memory or data in memory are not enough, so query database
        items = []
        col = Collection(db, language)
        if end_id:
            end_id_entry = col.find_one({'_id': ObjectId(end_id)})

            if end_id_entry:
                end_id_updated = float(end_id_entry['updated'])

                if label_name:
                    feeds = Collection(db, FEED_REGISTRAR)
                    feed_lists = feeds.find(
                        {'labels': label_name}, {'feed_title': 1})
                    feed_names = [feed_list['feed_title']
                                  for feed_list in feed_lists]
                    items = col.find({'updated': {'$lt': end_id_updated}, 'feed': {'$in': feed_names}}).sort(
                        'updated', -1).limit(limit)
                else:
                    items = col.find({'updated': {'$lt': end_id_updated}, 'feed': feed}).sort(
                        'updated', -1).limit(limit)
            else:
                return None
        else:  # get the most recent limit number of entries
            if label_name:
                feeds = Collection(db, FEED_REGISTRAR)
                feed_lists = feeds.find(
                    {'labels': label_name}, {'feed_title': 1})
                feed_names = [feed_list['feed_title']
                              for feed_list in feed_lists]
                items = col.find({'feed': {'$in': feed_names}}).sort(
                    'updated', -1).limit(limit)
            else:
                items = col.find({'feed': feed}).sort(
                    'updated', -1).limit(limit)

        for item in items:
            # string-ify all the values: ObjectId
            new_item = {}
            for x, y in item.iteritems():
                if x != 'updated':
                    new_item[str(x)] = str(y)
                new_item['updated'] = item['updated']
            entries.append(new_item)
        return entries
