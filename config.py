#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
config.py contains most CONSTANTS in the project
"""
# @author chengdujin
# @contact chengdujin@gmail.com
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
db = Database(con, 'news')

import redis
#rclient = redis.StrictRedis(host='10.240.35.40', port=6379)
rclient = redis.StrictRedis(host='127.0.0.1')


# CONSTANTS
#PUBLIC = 'http://mobile-global.baidu.com/news/%s'
#PUBLIC = 'http://180.76.2.34/%s'
PUBLIC = 'http://54.251.107.116/%s'
#LOCAL = '/home/work/STATIC/%s'
#LOCAL = '/home/ubuntu/STATIC/%s'
LOCAL = '/home/jinyuan/Downloads/%s'

TRANSCODED_LOCAL_DIR = LOCAL % 'news/ts/'
TRANSCODED_PUBLIC_DIR = PUBLIC % 'ts/'

IMAGES_LOCAL_DIR = LOCAL % 'news/img/'
IMAGES_PUBLIC_DIR = PUBLIC % 'img/'

MEDIA_LOCAL_DIR = LOCAL % 'news/mid/'
MEDIA_PUBLIC_DIR = PUBLIC % 'mid/'

NEWS_TEMPLATE = LOCAL % 'news/templates/index.html'
NEWS_TEMPLATE_ARABIC = LOCAL % 'news/templates/index_arabic.html'
UCK_TRANSCODING = 'http://gate.baidu.com/tc?m=8&from=bdpc_browser&src='
TRANSCODED_ENCODING = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'

TRANSCODING_BTN_EN = 'Original page'
TRANSCODING_BTN_PT = 'Página original'
TRANSCODING_BTN_JA = '元のページ'
TRANSCODING_BTN_IND = 'Laman Asli'
TRANSCODING_BTN_TH = 'หน้าเดิม'
TRANSCODING_BTN_AR = 'ﺎﻠﻤﺻﺩﺭ'
TRANSCODING_BTN_ZH_CN = '查看原始网页'
TRANSCODING_BTN_ZH_HK = '查看原始鏈接'

DATABASE_REMOVAL_DAYS = 90
MEMORY_RESTORATION_DAYS = 20
MEMORY_EXPIRATION_DAYS = 20

STRATEGY_WITHOUT_WEIGHTS = 1
STRATEGY_WITH_WEIGHTS = 2

FEED_REGISTRAR = 'feeds'

PARAGRAPH_CRITERIA = 40
SUMMARY_LENGTH_LIMIT = 500
UCK_TIMEOUT = 15  # 15 seconds timeout
GOOGLE_TTS_TIMEOUT = 15

LANGUAGES = ['en', 'th', 'ind', 'ja', 'pt', 'en-rIN', 'ar', 'zh-CN', 'zh-HK']
MIN_IMAGE_SIZE = 150, 150
THUMBNAIL_STYLE = 1.4
THUMBNAIL_LANDSCAPE_SIZE_HIGH = 600, 226
THUMBNAIL_LANDSCAPE_SIZE_NORMAL = 450, 169
THUMBNAIL_LANDSCAPE_SIZE_LOW = 230, 85
THUMBNAIL_PORTRAIT_SIZE_HIGH = 310, 400
THUMBNAIL_PORTRAIT_SIZE_NORMAL = 175, 210
THUMBNAIL_PORTRAIT_SIZE_LOW = 90, 110
CATEGORY_IMAGE_SIZE = 310, 250
HOT_IMAGE_SIZE = 600, 250
