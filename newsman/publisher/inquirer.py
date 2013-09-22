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
from settings import Collection, db
from settings import logger
from settings import rclient, ConnectionError
import os

# CONSTANTS
from settings import CODE_BASE
from settings import COUNTRIES
from settings import HOTNEWS_TITLE_AR
from settings import HOTNEWS_TITLE_EN
from settings import HOTNEWS_TITLE_JA
from settings import HOTNEWS_TITLE_IND
from settings import HOTNEWS_TITLE_PT
from settings import HOTNEWS_TITLE_TH
from settings import HOTNEWS_TITLE_ZH_CN
from settings import HOTNEWS_TITLE_ZH_HK
from settings import LANGUAGES

HOTNEWS_TITLE = {'en': HOTNEWS_TITLE_EN, 'ja': HOTNEWS_TITLE_JA, 'th': HOTNEWS_TITLE_TH, 'pt': HOTNEWS_TITLE_PT, 'ind':
                  HOTNEWS_TITLE_IND, 'en-rIN': HOTNEWS_TITLE_EN, 'ar': HOTNEWS_TITLE_AR, 'zh-CN': HOTNEWS_TITLE_ZH_CN, 'zh-HK': HOTNEWS_TITLE_ZH_HK}


# TODO: need to refactor this method after sorting out feed.py
def get_categories_by_language(language=None):
    """
    get a list of categories and hot news by language
    """
    if not language:
        return None
    search_limit = 60
    images_limit = 5

    category_images = {}
    try:
        # check if redis is running
        rclient.ping()

        # find category_images for each category
        key_wildcard = 'news::%s::*' % language
        categories_composite = rclient.keys(key_wildcard)
        categories = [cc.replace('news::%s::' % language, "") for cc in categories_composite]
    except ConnectionError:
        logger.critical('Redis is down!')
        
        # query database for category names
        try:
            document_name = language
            document = Collection(db, document_name)
            categories = document.distinct('categories')
        except Exception as k:
            logger.critical(str(k))

    if categories:
        for category in categories:
            entries = get_latest_entries_by_category(language=language, category=category, limit=search_limit)
            # 'category A': [{'title':'xxx', 'image':'http://yyy.com/zzz.jpg'}]
            # image: category_image
            category_images[category] = []
            for entry in entries:
                if 'category_image' in entry and entry['category_image'] and entry['category_image'] != 'None' and entry['category_image'] != 'null':
                    item = {'title': entry['title'], 'image': entry['category_image'], 'updated': entry['updated']}
                    category_images[category].append(item)
                    # limit the number of category_image to
                    if len(category_images[category]) == images_limit:
                        break
    else:
        logger.error("%s not supported! Or database is corrupted!" % language)

    # find hotnews_image from hot news
    hotnews = HOTNEWS_TITLE[language]
    entries = get_latest_entries_by_language(language=language, limit=search_limit)
    category_images[hotnews] = []
    for entry in entries:
        if 'hotnews_image' in entry and entry['hotnews_image'] and entry['hotnews_image'] != 'None' and entry['hotnews_image'] != 'null':
            item = {'title': entry['title'], 'image': entry['hotnews_image'], 'updated': entry['updated']}
            category_images[hotnews].append(item)
            if len(category_images[hotnews]) == images_limit:
                break

    # special formatting for android-end
    output = []
    for k, v in category_images.iteritems():
        output.append({'Category': k, 'Images': v})
    return {'Categories': output}


def get_latest_entries_by_language(language=None, limit=10, start_id=None):
    """
    find out latest news items by language
    with a start_id, search entries newer than that 
    """

    if not language:
        return None
    if language not in LANGUAGES:
        return None
    if limit < 0:
        return None
    # limit the number of items
    if limit > 100:
        limit = 100

    # return list
    entries = []
    class_name = "news::%s" % language

    try:
        # check if redis is alive
        rclient.ping()

        # get the latest entries
        entry_ids_total = rclient.zcard(class_name)

        if entry_ids_total:  
            if entry_ids_total >= limit: # memory (partially) meets the limit
                entry_ids = rclient.zrevrange(class_name, 0, limit - 1)
            
                dirty_expired_ids = []
                for entry_id in entry_ids:
                    if start_id and entry_id == start_id:
                        return entries

                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        entries.append(eval(entry_id_in_memory))
                    else:
                        # call clean_memory afterwards
                        dirty_expired_ids.append(entry_id)
            else:
                entry_ids = rclient.zrevrange(class_name, 0, entry_ids_total - 1)

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

                # find out the boundary between memory and database
                last_entry_in_memory_updated = float(last_entry_in_memory['updated'])
                # get the REAL number of needs in database
                limit_in_database = limit - len(entries)

                # database
                col = Collection(db, language)
                items = col.find({'updated': {'$lt': last_entry_in_memory_updated}}).sort('updated', -1).limit(limit_in_database)
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

            # dirty expired ids found
            if dirty_expired_ids:
                sys.path.append(os.path.join(CODE_BASE, 'newsman'))
                from watchdog import clean_memory
                clean_memory.clean_by_items(class_name, dirty_expired_ids)
                logger.warning('Memory contains dirty expired items')

            return entries
        else:
            raise ConnectionError('Find nothing about %s in memory' % class_name)
    except ConnectionError:
        # query the database
        col = Collection(db, language)
        items = col.find().sort('updated', -1).limit(limit)
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


def get_previous_entries_by_language(language=None, limit=10, end_id=None):
    """
    get entries before end_id
    """

    if not language:
        return None
    if language not in LANGUAGES:
        return None
    if limit < 0:
        return None
    # limit the number of items
    if limit > 100:
        limit = 100

    # return list
    entries = []
    class_name = "news::%s" % language

    try:
        # check is redis is alive
        rclient.ping()

        # preprocess end_id
        entry_ids_total = rclient.zcard(class_name)
        end_id_index = 0
        END_ID_IN_MEMORY = False
        limit_in_memory = 0

        if not end_id:
            end_id_index = entry_ids_total
            if entry_ids_total:
                # end_id is assigned the most recent one
                end_id = rclient.zrevrange(class_name, 0, 0)[0]
                END_ID_IN_MEMORY = True
                limit_in_memory = entry_ids_total
            else:
                end_id = None  # which is in most cases, pointless
                END_ID_IN_MEMORY = False
        else:
            end_id_index = rclient.zrank(class_name, end_id)
            # not existing entry --> nil
            # first entry --> 0
            END_ID_IN_MEMORY = True if end_id_index > 0 else False
            if END_ID_IN_MEMORY:
                limit_in_memory = rclient.zrank(class_name, end_id)
            
        if END_ID_IN_MEMORY:  # see if data in memory suffice
            if limit_in_memory >= limit:  # purely get from memory
                entry_ids = rclient.zrevrange(class_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit - 1)

                dirty_expired_ids = []
                for entry_id in entry_ids:
                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        entries.append(eval(entry_id_in_memory))
                    else:
                        dirty_expired_ids.append(entry_id)
            else:  # memory + database
                # memory
                entry_ids = rclient.zrevrange(class_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit_in_memory - 1)

                last_entry_in_memory = None
                dirty_expired_ids = []
                for entry_id in entry_ids:
                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        last_entry_in_memory = eval(entry_id_in_memory)
                        entries.append(last_entry_in_memory)
                    else:
                        dirty_expired_ids.append(entry_id)

                last_entry_in_memory_updated = float(last_entry_in_memory['updated'])
                limit_in_database = limit - len(entries)

                # find the remaining items in database
                col = Collection(db, language)
                items = col.find({'updated': {'$lt': last_entry_in_memory_updated}}).sort('updated', -1).limit(limit_in_database)
                for item in items:
                    # string-ify all the values: ObjectId
                    new_item = {}
                    for x, y in item.iteritems():
                        if x != 'updated':
                            new_item[str(x)] = str(y)
                        new_item['updated'] = item['updated']
                    entries.append(new_item)

            # clean dirty memory
            if dirty_expired_ids:
                sys.path.append(os.path.join(CODE_BASE, 'newsman'))
                from watchdog import clean_memory
                clean_memory.clean_by_items(class_name, dirty_expired_ids)
                logger.warning('Memory contains dirty expired items')

            return entries
        else:
            raise ConnectionError('Find nothing about %s in memory' % class_name)
    except ConnectionError:
        # no memory or data in memory are not enough, so query database
        items = []
        col = Collection(db, language)
        if end_id:
            end_id_entry = col.find_one({'_id': ObjectId(end_id)})
            if end_id_entry:
                end_id_updated = float(end_id_entry['updated'])
                items = col.find({'updated': {'$lt': end_id_updated}}).sort('updated', -1).limit(limit)
            else:
                return None
        else: # get the most recent limit number of entries
            items = col.find().sort('updated', -1).limit(limit)

        # string-ify all the values: ObjectId
        for item in items:
            new_item = {}
            for x, y in item.iteritems():
                if x != 'updated':
                    new_item[str(x)] = str(y)
                new_item['updated'] = item['updated']
            entries.append(new_item)
        return entries


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
            class_name = 'news::%s::%s::%s::%s' % (language, country, category, feed)
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
                entry_ids = rclient.zrevrange(class_name, 0, entry_ids_total - 1)

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
                last_entry_in_memory_updated = float(last_entry_in_memory['updated'])
                limit_in_database = limit - len(entries)

                # database
                col = Collection(db, language)
                # query only one of its values
                if label_name:
                    items = col.find({'updated': {'$lt':last_entry_in_memory_updated}, 'countries':country, 'categories':category_name, 'labels':label_name}).sort('updated', -1).limit(limit_in_database)
                else:
                    items = col.find({'updated': {'$lt':last_entry_in_memory_updated}, 'countries':country, 'categories':category_name, 'feed':feed}).sort('updated', -1).limit(limit_in_database)

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
            raise ConnectionError('Find nothing about %s in memory' % class_name)
    except ConnectionError:  
        # query the database
        col = Collection(db, language)
        if label_name:
            items = col.find({'countries':country, 'categories':category_name, 'labels':label_name}).sort('updated', -1).limit(limit)
        else:
            items = col.find({'countries':country, 'categories': category, 'feed':feed}).sort('updated', -1).limit(limit)

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


def get_previous_entries_by_category(language=None, category=None, limit=10, end_id=None):
    """
    find entries before end_id
    """

    if not language or not category:
        return None
    if language not in LANGUAGES:
        return None
    if limit < 0:
        return None
    # limit the number of items
    if limit > 100:
        limit = 100

    # return list
    entries = []
    class_name = 'news::%s::%s' % (language, category)

    try:
        # check if redis is alive
        rclient.ping()

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
                entry_ids = rclient.zrevrange(class_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit - 1)

                dirty_expired_ids = []
                for entry_id in entry_ids:
                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        entries.append(eval(entry_id_in_memory))
                    else:
                        dirty_expired_ids.append(entry_id)
            else:  # memory + database
                # memory
                entry_ids = rclient.zrevrange(class_name, entry_ids_total - end_id_index, entry_ids_total - end_id_index + limit_in_memory - 1)

                last_entry_in_memory = None
                dirty_expired_ids = []
                for entry_id in entry_ids:
                    entry_id_in_memory = rclient.get(entry_id)
                    if entry_id_in_memory:
                        last_entry_in_memory = eval(entry_id_in_memory)
                        entries.append(last_entry_in_memory)
                    else:
                        dirty_expired_ids.append(entry_id)

                last_entry_in_memory_updated = float(last_entry_in_memory['updated'])
                limit_in_database = limit - len(entries)

                # find the remaining items in database
                col = Collection(db, language)
                items = col.find({'updated': {'$lt': last_entry_in_memory_updated}, 'categories': category}).sort('updated', -1).limit(limit_in_database)
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
            raise ConnectionError('Find nothing about %s in memory' % class_name)
    except ConnectionError:  
        # no memory or data in memory are not enough, so query database
        items = []
        col = Collection(db, language)
        if end_id:
            end_id_entry = col.find_one({'_id': ObjectId(end_id)})
            if end_id_entry:
                end_id_updated = float(end_id_entry['updated'])
                items = col.find({'updated': {'$lt': end_id_updated}, 'categories': category}).sort('updated', -1).limit(limit)
            else:
                return None
        else: # get the most recent limit number of entries
            items = col.find({'categories': category}).sort('updated', -1).limit(limit)

        for item in items:
            # string-ify all the values: ObjectId
            new_item = {}
            for x, y in item.iteritems():
                if x != 'updated':
                    new_item[str(x)] = str(y)
                new_item['updated'] = item['updated']
            entries.append(new_item)
        return entries
