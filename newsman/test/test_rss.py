#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from spider import scraper

#entries = scraper.update(feed_link='http://news.yahoo.com/rss/world', feed_id='520b7da3680ccf3c10e93d55', language='en')
entries = scraper.update(feed_id='5296e329f5d7e61827936108', feed_link='http://men.kapook.com/technology/feed', language='th')
#entries = scraper.update(feed_link='http://www.mtv.com/rss/news/news_full.jhtml', feed_id='520b7da3680ccf3c10e93d6e', language='en')
#entries = scraper.update(feed_link='http://feeds.reuters.com/reuters/healthNews', feed_id='520b7da3680ccf3c10e93d4b', language='en')

#entries = scraper.update(feed_link='http://www.antaranews.com/rss/nasional-kesehatan', feed_id='008', language='ind', categories=categories)

#entries = scraper.update(feed_link='http://sankei.jp.msn.com/rss/news/politics.xml', feed_id='5203d468680ccf6430d7ab7a', language='ja')
#entries = scraper.update(feed_link='http://news.goo.ne.jp/rss/topstories/world/index.rdf', feed_id='5203d468680ccf6430d7ab7d', language='ja', categories=categories)
#entries = scraper.update(feed_link='http://community.travel.yahoo.co.jp/domestic/blog.html?m=rss', feed_id='5203d468680ccf6430d7ab75', language='ja')
