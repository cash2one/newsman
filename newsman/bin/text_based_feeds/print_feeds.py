#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

from config.settings import Collection, db
import feedparser


col = Collection(db, 'feeds')

output = {}
items = col.find()
for item in items:
    for country in item['countries']:
        country = str(country)
        if country not in output:
            output[country] = []
        ss = feedparser.parse(item['feed_link'])
        print item['feed_link']
        feed_title = ss['feed']['title'] if ss and 'title' in ss['feed'] else item['feed_link']
        print feed_title
        output[country].append('%s  %s' % (item['categories'][0], feed_title))
        print

f = open('test', 'w')
for k, v in output.iteritems():
    f.write(k + '\n')
    for i in v:
        f.write("    " + i + '\n')
    f.write('\n')
f.close()
