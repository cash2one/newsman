#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from scraper import rss

#entries = rss_parser.parse(feed_link='http://news.yahoo.com/rss/us', language='en')
#entries = rss_parser.parse(feed_link='http://www.engadget.com/rss.xml', language='en')
#entries = rss_parser.parse(feed_link='http://rss.cnn.com/rss/edition_sport.rss', language='en')
categories = ['Technology', 'Internet']
#entries = rss.update(feed_link='http://news.yahoo.com/rss/sports', feed_id='007', language='en', categories=categories)
#entries = rss.update(feed_link='http://www.engadget.com/rss.xml', feed_id='008', language='en', categories=categories)
#entries = rss.update(feed_link='http://feeds.bbci.co.uk/news/world/rss.xml', feed_id='008', language='en', categories=categories)
#entries = rss.update(feed_link='http://www.antaranews.com/rss/nasional-kesehatan', feed_id='008', language='ind', categories=categories)
entries = rss.update(feed_link='http://sankei.jp.msn.com/rss/news/politics.xml', feed_id='008', language='en', categories=categories)
print entries[0]
