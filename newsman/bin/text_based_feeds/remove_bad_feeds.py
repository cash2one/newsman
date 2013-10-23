#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

from config.settings import Collection, db
import feedparser


col = Collection(db, 'feeds')
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
