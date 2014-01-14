#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from analyzer import rss_parser

#entries = rss_parser.parse(feed_link='http://news.yahoo.com/rss/us', language='en')
#entries = rss_parser.parse(feed_link='http://www.engadget.com/rss.xml', language='en')
#entries = rss_parser.parse(feed_link='http://rss.cnn.com/rss/edition_sport.rss', language='en')
#entries = rss_parser.parse(feed_link='http://news.yahoo.com/rss/sports', language='en')
entries = rss_parser.parse(feed_link='http://rss.detik.com/index.php/sport', feed_id="5264f7cb0ff6cb1898609028", language='in', categories={"ID::Olahraga" : "1"})
print len(entries)
print entries[0]
