#!/usr/bin/env python 
#-*- coding: utf-8 -*- 


from newsman.config.settings import Collection, db
import feedparser
import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

col = Collection(db, 'feeds')

output = {}
items = col.find()
for item in items:
    for country in item['countries']:
        country = str(country)
        if country not in output:
            output[country] = []
        if not item['feed_title'] or item['feed_title'] == None:
            ss = feedparser.parse(item['feed_link'])
            feed_title = ss['feed']['title'] if ss and 'title' in ss[
                'feed'] else item['feed_link']
            print item['feed_link'], str(feed_title)
            output[country].append(
                '%s*|*%s' % (item['feed_link'], str(feed_title)))
        else:
            print ">>>", str(item['feed_title'])

f = open('tests', 'w')
for k, v in output.iteritems():
    f.write('>>>>> ' + k + '\n')
    for i in v:
        f.write(i + '\n')
    f.write('\n')
f.close()
