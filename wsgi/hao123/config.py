#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#@author Yuan JIN
#@contact jinyuan@baidu.com
#@created Jan 17, 2013
#@updated Feb 8, 2013
#

import sys 
reload(sys)
sys.setdefaultencoding('UTF-8')

# SERVICES
from pymongo.connection import Connection
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
con = Connection('127.0.0.1:27017')
db = Database(con, 'hao123')

import redis
rclient = redis.StrictRedis('127.0.0.1')

from HTMLParser import HTMLParser
hparser = HTMLParser()

# CONSTANTS
TRANSCODED_LOCAL_DIR = '/home/ubuntu/hao123/transcoded/'
TRANSCODED_WEB_DIR = 'http://54.251.107.116/transcoded/'

MAINTENANCE_DIR = '/home/ubuntu/hao123/maintenance/'
RSS_UPDATE_LOG = '/home/ubuntu/hao123/maintenance/rul.txt'
DATA_CLEAR_LOG = '/home/ubuntu/hao123/maintenance/dcl.txt'

THUMBNAIL_LOCAL_DIR = '/home/ubuntu/hao123/thumbnails/'
THUMBNAIL_WEB_DIR = 'http://54.251.107.116/thumbnails/'

NEWS_TEMPLATE = '/home/ubuntu/hao123/templates/index.html'
UCK_TRANSCODING = 'http://gate.baidu.com/tc?m=8&from=bdpc_browser&src='
TRANSCODED_ENCODING = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'   # lijun

TRANSCODING_BTN_EN = 'Original page'
TRANSCODING_BTN_PT = 'Página original'
TRANSCODING_BTN_JA = '元のページ'
TRANSCODING_BTN_IND = 'Laman Asli'
TRANSCODING_BTN_TH = 'หน้าเดิม'

DATABASE_REMOVAL_DAYS = 10
MEMORY_RESTORATION_DAYS = 5
REDIS_ENTRY_EXPIRATION = 60 * 60 * 24 * 5

STRATEGY_WITHOUT_WEIGHTS = 1
STRATEGY_WITH_WEIGHTS = 2

FEED_REGISTRAR = 'feeds'

LANGUAGES = ['en', 'th', 'ind', 'ja', 'pt', 'en-rIN']
THUMBNAIL_SIZE = 150, 150   # banner filter for indonesia : lijun
