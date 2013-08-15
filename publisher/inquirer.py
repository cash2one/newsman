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
from config import Collection
from config import db
from config import rclient
import feedparser

# CONSTANTS
from config import LANGUAGES
from config import STRATEGY_WITHOUT_WEIGHTS
from config import STRATEGY_WITH_WEIGHTS


# TODO: need to refactor this method after sorting out feed.py
# TODO: added database inquire if language cannot be found in memory
def get_categories_by_language(language=None):
    """
    get a list of categories and hot news by language
    """
    if not language:
        return None
    search_limit = 50
    images_limit = 5

    category_images = {}
    # find category_images for each category
    key_wildcard = 'news::%s::*' % language
    categories_composite = rclient.keys(key_wildcard)
    if categories_composite:
        categories = [cc.replace('news::%s::' % language, "")
                      for cc in categories_composite]
        for category in categories:
            entries = get_latest_entries_by_category(
                language=language, category=category, limit=search_limit)
            # 'category A': [{'title':'xxx', 'image':'http://yyy.com/zzz.jpg'}]
            # image: category_image
            category_images[category] = []
            for entry in entries:
                if 'category_image' in entry and entry['category_image']:
                    item = {'title': entry['title'], 'image': entry['category_image'], 'updated': entry['updated']}
                    category_images[category].append(item)
                    # limit the number of category_image to
                    if len(category_images[category]) == images_limit:
                        break
    else:
        print "ERROR: %s not supported! Or database is corrupted!" % language

    # find hot_news_image from hot news
    # category_images['hot_news']
    entries = get_latest_entries_by_language(
        language=language, limit=search_limit)
    category_images['hot_news'] = []
    for entry in entries:
        if 'hot_news_image' in entry and entry['hot_news_image']:
            item = {'title': entry['title'], 'image': entry['hot_news_image'], 'updated': entry['updated']}
            category_images['hot_news'].append(item)
            if len(category_images['hot_news']) == images_limit:
                break

    # special formatting for android-end
    output = []
    for k, v in category_images.iteritems():
        output.append({'Category': k, 'Images': v})
    return {'Categories': output}


def get_latest_entries_by_language(language=None, limit=10, start_id=None, strategy=1):
    """
    find out latest news items by language
    """
    if not language:
        return None
    if not limit:
        return None
    if limit < 0 or limit > 100:
        return None
    language = language.strip()
    if language not in LANGUAGES:
        return None
    limit = int(limit)
    # get the latest entries
    entry_ids_total = rclient.zcard("news::%s" % language)
    entries = []
    if entry_ids_total:  # memory (partially) meets the limit
        if entry_ids_total >= limit:
            entry_ids = rclient.zrevrange("news::%s" % language, 0, limit - 1)
            for entry_id in entry_ids:
                if start_id and entry_id == start_id:
                    return entries
                entries.append(eval(rclient.get(entry_id)))
        else:
            entry_ids = rclient.zrevrange(
                "news::%s" % language, 0, entry_ids_total - 1)
            last_entry_in_memory = None
            for entry_id in entry_ids:
                if start_id and entry_id == start_id:
                    return entries
                last_entry_in_memory = eval(rclient.get(entry_id))
                entries.append(last_entry_in_memory)
            last_entry_in_memory_updated = last_entry_in_memory['updated']
            limit_in_database = limit - entry_ids_total
            # database
            col = Collection(db, language)
            items = col.find({'updated': {'$lt': last_entry_in_memory_updated}}).sort(
                'updated', -1).limit(limit_in_database)
            for item in items:
                if start_id and str(item['_id']) == start_id:
                    return entries
                # string-ify all the values: ObjectId
                for x, y in item.iteritems():
                    if x != 'updated':
                        item[x] = str(y)
                entries.append(item)
    else:  # query the database
        entries = []
        col = Collection(db, language)
        items = col.find().sort('updated', -1).limit(limit)
        for item in items:
            if start_id and str(item['_id']) == start_id:
                return entries
            # string-ify all the values: ObjectId
            for x, y in item.iteritems():
                if x != 'updated':
                    item[x] = str(y)
            entries.append(item)
    return entries


def get_previous_entries_by_language(language=None, limit=10, end_id=None, strategy=1):
    """
    strategy 1.query without considering weights 2.query with considering weights
    """
    if not language:
        return None
    if not limit:
        return None
    if limit < 0 or limit > 100:
        return None
    language = language.strip()
    if language not in LANGUAGES:
        return None
    limit = int(limit)
    # preprocess end_id
    entry_ids_total = 0
    end_id_index = 0
    END_ID_IN_MEMORY = False
    limit_in_memory = 0
    if not end_id:
        entry_ids_total = rclient.zcard("news::%s" % language)
        end_id_index = entry_ids_total
        if entry_ids_total:
            # end_id is assign the most recent one
            end_id = rclient.zrevrange("news::%s" % language, 0, 0)[0]
            END_ID_IN_MEMORY = True
            limit_in_memory = entry_ids_total
        else:
            end_id = None  # which is in most cases, pointless
            END_ID_IN_MEMORY = False
    else:
        end_id_index = rclient.zrank("news::%s" % language, end_id)
        END_ID_IN_MEMORY = True if end_id_index > 0 else False
        if END_ID_IN_MEMORY:
            limit_in_memory = rclient.zrank("news::%s" % language, end_id)
    # implement according to strategy
    if strategy == STRATEGY_WITHOUT_WEIGHTS:
        entries = []
        if END_ID_IN_MEMORY:  # see if data in memory suffice
            if limit_in_memory >= limit:  # purely get from memory
                entry_ids = rclient.zrevrange(
                    "news::%s" % language, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit - 1)
                for entry_id in entry_ids:
                    entries.append(eval(rclient.get(entry_id)))
            else:  # memory + database
                # memory
                entry_ids = rclient.zrevrange(
                    "news::%s" % language, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit_in_memory - 1)
                last_entry_in_memory = None
                for entry_id in entry_ids:
                    last_entry_in_memory = eval(rclient.get(entry_id))
                    entries.append(last_entry_in_memory)
                limit_in_database = limit - limit_in_memory
                last_entry_in_memory_updated = last_entry_in_memory['updated']
                # find the remaining items in database
                col = Collection(db, language)
                items = col.find({'updated': {'$lt': last_entry_in_memory_updated}}).sort(
                    'updated', -1).limit(limit_in_database)
                for item in items:
                    # string-ify all the values: ObjectId
                    for x, y in item.iteritems():
                        if x != 'updated':
                            item[x] = str(y)
                    entries.append(item)
            return entries
        else:  # no memory or data in memory are not enough, so query database
            entries = []
            col = Collection(db, language)
            if end_id:
                end_id_entry = col.find_one({'_id': ObjectId(end_id)})
                if end_id_entry:
                    end_id_updated = end_id_entry['updated']
                    items = col.find({'updated': {'$lt': end_id_updated}}).sort(
                        'updated', -1).limit(limit)
                else:
                    return None
            # get the most recent limit number of entries
            else:
                items = col.find().sort('updated', -1).limit(limit)
            for item in items:
                # string-ify all the values: ObjectId
                for x, y in item.iteritems():
                    if x != 'updated':
                        item[x] = str(y)
                entries.append(item)
            return entries
    elif strategy == STRATEGY_WITH_WEIGHTS:
        pass


def get_latest_entries_by_category(language=None, category=None, limit=10, start_id=None, strategy=1):
    """
    find out latest news items by category and language
    """
    if not language or not category:
        return None
    if not limit:
        return None
    if limit < 0 or limit > 100:
        return None
    language = language.strip()
    category = category.strip()
    if language not in LANGUAGES:
        return None
    limit = int(limit)
    collection_name = 'news::%s::%s' % (language, category)
    # get the latest entries
    entry_ids_total = rclient.zcard(collection_name)
    entries = []
    if entry_ids_total:  # memory (partially) meets the limit
        if entry_ids_total >= limit:
            entry_ids = rclient.zrevrange(collection_name, 0, limit - 1)
            for entry_id in entry_ids:
                if start_id and entry_id == start_id:
                    return entries
                entries.append(eval(rclient.get(entry_id)))
        else:
            entry_ids = rclient.zrevrange(
                collection_name, 0, entry_ids_total - 1)
            last_entry_in_memory = None
            for entry_id in entry_ids:
                if start_id and entry_id == start_id:
                    return entries
                last_entry_in_memory = eval(rclient.get(entry_id))
                entries.append(last_entry_in_memory)
            last_entry_in_memory_updated = last_entry_in_memory['updated']
            limit_in_database = limit - entry_ids_total
            # database
            col = Collection(db, language)
            # query categories array with only one of its values
            items = col.find({'updated': {'$lt': last_entry_in_memory_updated}, 'categories': category}).sort(
                'updated', -1).limit(limit_in_database)

            for item in items:
                if start_id and item['_id'] == start_id:
                    return entries
                # string-ify all the values: ObjectId
                for x, y in item.iteritems():
                    if x != 'updated':
                        item[x] = str(y)
                entries.append(item)
    else:  # query the database
        entries = []
        col = Collection(db, collection_name)
        items = col.find({'categories': category}).sort(
            'updated', -1).limit(limit)
        for item in items:
            if start_id and item['_id'] == start_id:
                return entries
            # string-ify all the values: ObjectId
            for x, y in item.iteritems():
                if x != 'updated':
                    item[x] = str(y)
            entries.append(item)
    return entries


def get_previous_entries_by_category(language=None, category=None, limit=10,
                                     end_id=None, strategy=1):
    """
    strategy 
        1.query without considering weights 
        2.query with considering weights
    """
    if not language or not category:
        return None
    if not limit:
        return None
    if limit < 0 or limit > 100:
        return None
    language = language.strip()
    category = category.strip()
    if language not in LANGUAGES:
        return None
    limit = int(limit)
    collection_name = 'news::%s::%s' % (language, category)
    # preprocess end_id
    entry_ids_total = 0
    end_id_index = 0
    END_ID_IN_MEMORY = False
    limit_in_memory = 0
    if not end_id:
        entry_ids_total = rclient.zcard(collection_name)
        end_id_index = entry_ids_total
        if entry_ids_total:
            # end_id is assign the most recent one
            end_id = rclient.zrevrange(collection_name, 0, 0)[0]
            END_ID_IN_MEMORY = True
            limit_in_memory = entry_ids_total
        else:
            end_id = None  # which is in most cases, pointless
            END_ID_IN_MEMORY = False
    else:
        end_id_index = rclient.zrank(collection_name, end_id)
        END_ID_IN_MEMORY = True if end_id_index > 0 else False
        if END_ID_IN_MEMORY:
            limit_in_memory = rclient.zrank(collection_name, end_id) + 1
    # implement according to strategy
    if strategy == STRATEGY_WITHOUT_WEIGHTS:
        entries = []
        if END_ID_IN_MEMORY:  # see if data in memory suffice
            if limit_in_memory >= limit:  # purely get from memory
                entry_ids = rclient.zrevrange(
                    collection_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit - 1)
                for entry_id in entry_ids:
                    entries.append(eval(rclient.get(entry_id)))
            else:  # memory + database
                # memory
                entry_ids = rclient.zrevrange(
                    collection_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit_in_memory - 1)
                last_entry_in_memory = None
                for entry_id in entry_ids:
                    last_entry_in_memory = eval(rclient.get(entry_id))
                    entries.append(last_entry_in_memory)
                limit_in_database = limit - limit_in_memory
                last_entry_in_memory_updated = last_entry_in_memory['updated']

                # find the remaining items in database
                col = Collection(db, language)
                items = col.find({'updated': {'$lt': last_entry_in_memory_updated}, 'categories': category}).sort(
                    'updated', -1).limit(limit_in_database)
                for item in items:
                    # string-ify all the values: ObjectId
                    for x, y in item.iteritems():
                        if x != 'updated':
                            item[x] = str(y)
                    entries.append(item)
            return entries
        else:  # no memory or data in memory are not enough, so query database
            entries = []
            col = Collection(db, language)
            if end_id:
                end_id_entry = col.find_one({'_id': ObjectId(end_id)})
                if end_id_entry:
                    end_id_updated = end_id_entry['updated']
                    items = col.find({'updated': {'$lt': end_id_updated}, 'categories': category}).sort(
                        'updated', -1).limit(limit)
                else:
                    return None
            # get the most recent limit number of entries
            else:
                items = col.find({'categories': category}).sort(
                    'updated', -1).limit(limit)
            for item in items:
                # string-ify all the values: ObjectId
                for x, y in item.iteritems():
                    if x != 'updated':
                        item[x] = str(y)
                entries.append(item)
            return entries
