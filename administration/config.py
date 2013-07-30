#!/usr/bin/python
# -*- coding: utf-8 -*-

# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jan 17, 2013

import sys 
reload(sys)
sys.setdefaultencoding('UTF-8')

# SERVICES
from pymongo.connection import Connection
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
con = Connection('127.0.0.1:27017')
db_news = Database(con, 'news')
db_feeds = Database(con, 'feeds')

import redis
rclient = redis.StrictRedis('127.0.0.1')

from HTMLParser import HTMLParser
hparser = HTMLParser()

# CONSTANTS
PUBLIC = 'http://180.76.4.17/%s'
LOCAL = '/home/jinyuan/Downloads/global-mobile-news/%s'

TRANSCODED_LOCAL_DIR = LOCAL % 'interface/transcoded/'
TRANSCODED_PUBLIC_DIR = PUBLIC % 'ts/'

IMAGES_LOCAL_DIR = LOCAL % 'interface/images/'
IMAGES_PUBLIC_DIR = PUBLIC % 'img/'

MEDIA_LOCAL_DIR = LOCAL % 'interface/media/'
MEDIA_PUBLIC_DIR = PUBLIC % 'mid/'

MAINTENANCE_DIR = LOCAL % 'alert_maintenance/maintenance/'
RSS_UPDATE_LOG = LOCAL % 'alert_maintenance/maintenance/rul.txt'
DATA_CLEAR_LOG = LOCAL % 'alert_maintenance/maintenance/dcl.txt'

NEWS_TEMPLATE = LOCAL % 'template/index.html'
UCK_TRANSCODING = 'http://gate.baidu.com/tc?m=8&from=bdpc_browser&src='
TRANSCODED_ENCODING = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'   # lijun

TRANSCODING_BTN_EN = 'Original page'
TRANSCODING_BTN_PT = 'Página original'
TRANSCODING_BTN_JA = '元のページ'
TRANSCODING_BTN_IND = 'Laman Asli'
TRANSCODING_BTN_TH = 'หน้าเดิม'

DATABASE_REMOVAL_DAYS = 90
MEMORY_RESTORATION_DAYS = 10
MEMORY_EXPIRATION_DAYS = 10

STRATEGY_WITHOUT_WEIGHTS = 1
STRATEGY_WITH_WEIGHTS = 2

FEED_REGISTRAR = 'feeds'

LANGUAGES = ['en', 'th', 'ind', 'ja', 'pt', 'en-rIN', 'ar']
MIN_IMAGE_SIZE = 150, 150
THUMBNAIL_IMAGE_SIZE = 118, 88
CATEGORY_IMAGE_SIZE = 189, 162
HOT_IMAGE_SIZE = 388, 162
