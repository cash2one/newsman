#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from scraper import rss_parser

entries = rss_parser.parse(feed_link='http://news.yahoo.com/rss/us', language='en')
print len(entries)
print entries[0]

