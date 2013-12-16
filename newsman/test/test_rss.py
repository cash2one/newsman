#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from spider import scraper

#entries = scraper.update(feed_id='5257d25509d1f72ff1aa8abc', feed_link='http://hilight.kapook.com/main/feed', language='th')
#entries = scraper.update(feed_id='5257d25509d1f72ff1aa8abe', feed_link='http://rssfeeds.sanook.com/rss/feeds/sanook/news.index.xml', language='th')
entries = scraper.update(feed_id='5257d25509d1f72ff1aa8ac3', feed_link='http://news.mthai.com/category/world-news/feed', language='th')
