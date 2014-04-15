#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Feed management supports operations like Insert, Modify and Remove on the 
level of an RSS feed, a label and a category
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Sept. 23, 2013'

from newsman.config.settings import Collection, db
from newsman.config.settings import rclient
from newsman.watchdog import clean_disk
from newsman.watchdog import clean_memory
import sys

# CONSTANTS
from newsman.config.settings import FEED_REGISTRAR

reload(sys)
sys.setdefaultencoding('UTF-8')


def modify_field(language):
    """
    change a key/field name in database and memory
    """
    # memory
    id_total = rclient.zcard("news::%s" % language)
    ids = rclient.zrange("news::%s" % language, 0, id_total)

    for id in ids:
        entry_string = rclient.get(id)
        entry_string_new = entry_string.replace(
            'hot_news_image', 'hotnews_image')
        rclient.setex(id, rclient.ttl(id), entry_string_new)

    # database
    col = Collection(db, language)
    col.update(
        {}, {"rename": {"hot_news_image": "hotnews_image"}}, False, True)
    col.update(
        {}, {"rename": {"hot_news_image_local": "hotnews_image_local"}}, False,
          True)


def modify_feed(language=None, feed_old=None, feed_new=None):
    """
    Call this once a feed's name is changed
    """
    if not language or not feed_old or not feed_new:
        return None

    # update old feed name in memory to new one
    feed_old_name_in_memory = 'news::%s::%s' % (language, feed_old)
    feed_new_name_in_memory = 'news::%s::%s' % (language, feed_new)

    ids_all = rclient.keys('*')
    for id_in_memory in ids_all:
        if 'news' not in id_in_memory and '::' not in id_in_memory:
            entry = eval(rclient.get(id_in_memory))
            if entry['feed'] == feed_old:
                entry['feed'] = feed_new
                rclient.set(
                    name=id_in_memory, value=entry,
                    ex=rclient.ttl(id_in_memory), xx=True)
        elif id_in_memory == feed_old_name_in_memory:
            rclient.rename(feed_old_name_in_memory, feed_new_name_in_memory)
        else:
            continue

    # update old feed name in database to new one
    # change the "meta" data of feed_old in database
    feeds = Collection(db, FEED_REGISTRAR)
    item = feeds.find_one({'feed_title': feed_old})
    if item:
        item['feed_title'] = feed_new
        feeds.update({'_id': item['_id']}, item)
    # change all the related news in database
    col = Collection(db, language)
    items = col.find({'feed': feed_old})
    if items:
        for item in items:
            item['feed'] = feed_new
            col.update({'_id': item['_id']}, item)

    return 'OK'


def remove_feed(language=None, feed=None):
    """
    Call this once a feed is removed
    """
    if not language or not feed:
        return None

    # remove every entry related to feed in memory
    feed_name_in_memory = 'news::%s::%s' % (language, feed)
    ids_all = rclient.keys('*')
    for id_in_memory in ids_all:
        if 'news' not in id_in_memory and '::' not in id_in_memory:
            rclient.delete(id_in_memory)
        elif id_in_memory == feed_name_in_memory:
            feed_total_in_memory = rclient.zcard(feed_name_in_memory)
            # remove sequence in feed_name_in_memory
            rclient.zremrangebyrank(
                feed_name_in_memory, 0, feed_total_in_memory)
            # remove the key
            rclient.delete(feed_name_in_memory)
    # clean memory holes
    clean_memory.clean()

    # remove feed "meta" data in feeds database
    feeds = Collection(db, FEED_REGISTRAR)
    feeds.remove({'feed_title': feed})
    # remove entries related to feed in database
    col = Collection(db, language)
    col.remove({'feed': feed})
    # clean disk
    clean_disk.clean()
    return 'OK'


def add_feed_to_label(language=None, feed=None, label=None, label_order=None):
    """
    Ad hoc add a feed to label. This mainly deals with history data
    """
    if not language or not feed or not label:
        return None

    # add label to the feed's labels
    feeds = Collection(db, FEED_REGISTRAR)
    item = feeds.find_one({'feed_title': feed})
    if item:
        if label not in item['labels']:
            item['labels'][label] = label_order
            feeds.update({'_id': item['_id']}.item)

            # add entries in memory of the feed
            label_name_in_memory = 'news::%s::%s' % (language, label)
            ids_all = rclient.keys('*')
            for id_in_memory in ids_all:
                if 'news' not in id_in_memory and '::' not in id_in_memory:
                    entry = eval(rclient.get(id_in_memory))
                    if entry['feed'] == feed:
                        rclient.zadd(
                            label_name_in_memory, entry['updated'],
                            entry['_id'])
            return 'OK'
        else:
            # label is already there
            return None
    else:
        return None


def add_label(language=None, label=None, *kwargs):
    """
    Ad hoc add a label. This mainly deals with history data
    """
    if not language or not label:
        return None

    label_name_in_memory = 'news::%s::%s' % (language, label)

    for item in kwargs:
        # add entries in memory of this feed to the label sequence
        add_feed_to_label(language=language, feed=item,
                          label=label_name_in_memory)


def remove_feed_from_label(language=None, feed=None, label=None):
    """
    Remove a feed from a label
    """
    if not language or not feed or not label:
        return None

    # remove member in label sequence in memory regarding the feed
    label_name_in_memory = 'news::%s::%s' % (language, label)
    if rclient.exists(label_name_in_memory):
        label_total_in_memory = rclient.zcard(label_name_in_memory)
        ids_with_label = rclient.zrevrange(
            label_name_in_memory, 0, label_total_in_memory)
        for id_with_label in ids_with_label:
            item = eval(rclient.get(id_with_label))
            if item['feed'] == feed:
                rclient.zrem(id_with_label)

    # remove label in feed
    feeds = Collection(db, FEED_REGISTRAR)
    item = feeds.find_one(
        {'feed_title': feed, '%s.%s' % ('labels', label): {'$exists': True}})
    if item:
        item['labels'].pop(label)
        feeds.update({'_id': item['_id']}, item)
        return 'OK'

    return None


def remove_label(language=None, label=None):
    """
    Remove a label from memory and database
    Note. label should be country::category::label-like
    """

    if not language or not label:
        return None

    label_name_in_memory = 'news::%s::%s' % (language, label)
    if rclient.exists(label_name_in_memory):
        label_total_in_memory = rclient.zcard(label_name_in_memory)
        # remove sequence in label_name_in_memory
        rclient.zremrangebyrank(label_name_in_memory, 0, label_total_in_memory)
        # remove the key
        rclient.delete(label_name_in_memory)

    # operate on database with or without memory
    feeds = Collection(db, FEED_REGISTRAR)
    items = feeds.find(
        {'language': language, '%s.%s' % ('labels', label): {'$exists': True}})
    if items:
        for item in items:
            _id = item['_id']
            item['labels'].pop(label)
            feeds.update({'_id': _id}, item)
        return 'OK'
    return None


def update_label(language=None, label=None):
    """
    If some feed in label change name, call this one
    """
    if not language or not label:
        return None

    feeds = Collection(db, FEED_REGISTRAR)
    # items = feeds.find({'language' = language, '%s.%s' % ('labels', label):
    #  {'$exists': True}})
    # This is incorrect!!!
    items = None
    if items:
        feeds_with_label = [item['feed_title'] for item in items]

        if feeds_with_label:
            label_name_in_memory = 'news::%s::%s' % (language, label)
            # remove all existing data regarding this label in memory
            if rclient.exsits(label_name_in_memory):
                label_total_in_memory = rclient.zcard(label_name_in_memory)
                # remove sequence in label_name_in_memory
                rclient.zremrangebyrank(label_name_in_memory, 0,
                                        label_total_in_memory)

                # reload entries of feeds to the sequence
                ids_all = rclient.keys('*')
                for id_in_memory in ids_all:
                    if 'news' not in id_in_memory and '::' not in id_in_memory:
                        item = eval(rclient.get(id_in_memory))
                        if item['feed'] in feeds_with_label:
                            rclient.zadd(label_name_in_memory, item['updated'],
                                         item['_id'])
                return 'OK'
    return None


def modify_label(language=None, label_old=None, label_new=None,
                 label_new_order=None):
    """
    Call this one if the name a label is changed
    """
    if not language or not label_old or not label_new:
        return None

    # update feeds with old label names to new ones
    feeds = Collection(db, FEED_REGISTRAR)

    items = feeds.find({'%s.%s' % ('labels', label_old): {'$exists': True}})
    items = feeds.find({'labels': label_old})
    if items:
        for item in items:
            if label_old in item['labels']:
                item['labels'].pop(label_old)
                item['labels'][label_new] = label_new_order
                feeds.update({'_id': item['_id']}, item)

    # rename old label to new one in memory
    label_old_in_memory = 'news::%s::%s' % (language, label_old)
    label_new_in_memory = 'news::%s::%s' % (language, label_new)
    rclient.rename(label_old_in_memory, label_new_in_memory)


if __name__ == '__main__':
    pass
