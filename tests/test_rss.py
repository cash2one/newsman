#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from scraper import rss

entries = rss.update(feed_link='http://news.yahoo.com/rss/us', feed_id='520a4340680ccf0b71e58944', language='en')
#entries = rss.update(feed_link='http://www.engadget.com/rss.xml', feed_id='520a4340680ccf0b71e58946', language='en')
#entries = rss.update(feed_link='http://news.yahoo.com/rss/sports', feed_id='52020d6c680ccf157f317902', language='en')
#categories = ['BBC', 'News']
#entries = rss.update(feed_link='http://feeds.bbci.co.uk/news/world/rss.xml', feed_id='008', language='en', categories=categories)

#entries = rss.update(feed_link='http://www.antaranews.com/rss/nasional-kesehatan', feed_id='008', language='ind', categories=categories)

#entries = rss.update(feed_link='http://sankei.jp.msn.com/rss/news/politics.xml', feed_id='5203d468680ccf6430d7ab7a', language='ja')
#entries = rss.update(feed_link='http://news.goo.ne.jp/rss/topstories/world/index.rdf', feed_id='5203d468680ccf6430d7ab7d', language='ja', categories=categories)
#entries = rss.update(feed_link='http://community.travel.yahoo.co.jp/domestic/blog.html?m=rss', feed_id='5203d468680ccf6430d7ab75', language='ja')
