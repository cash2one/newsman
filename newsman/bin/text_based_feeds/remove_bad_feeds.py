#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

from config.settings import Collection, db
import feedparser


col = Collection(db, 'feeds')

"""
f = open('db_id_list', 'r')
feed_ids = f.readlines()
feed_ids = [feed_id.strip() for feed_id in feed_ids]
f.close()


counter = 0
items = col.find({'language':{'$in':['in', 'en', 'zh']}})
for item in items:
    if str(item['_id']) in feed_ids:
        pass
    else:
        counter = counter + 1
        print item['feed_link']
        col.remove({'_id':item['_id']})
print counter
"""

items = col.find({'language': {'$in': ['en']}})
for item in items:
    # if 'status' in item and item['status'] and (item['status'] == 200 or item['status'] == 302 or item['status'] == 304):
        # pass
        # print item['status'], item['feed_title'], "[%s]" %
        # item['latest_update'] if 'latest_update' in item and
        # item['latest_update'] else '-', '[%s]' % item['reason'] if 'reason'
        # in item and reason['reason'] else '-'
    if not item['updated_times']:
        print item['language'], str(item['feed_title']), "[%s]" % item['latest_update'] if 'latest_update' in item and item['latest_update'] else '-', '[%s]' % item['reason'] if 'reason' in item and item['reason'] else '-', '[%s]' % item['status'] if 'status' in item and item['status'] else '-'
        col.remove({'_id': item['_id']})
