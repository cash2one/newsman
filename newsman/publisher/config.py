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

from HTMLParser import HTMLParser
hparser = HTMLParser()


# CONSTANTS
#PUBLIC = 'http://mobile-global.baidu.com/news/%s'  # hk01-hao123-mob01/mob02
#PUBLIC = 'http://180.76.2.34/%s'                   # hk01-hao123-mob00
PUBLIC = 'http://54.251.107.116/%s'                # AWS singapore
#PUBLIC = 'http://54.232.81.44/%s'                  # AWS sao paolo
#PUBLIC = 'http://54.248.227.71/%s'                 # AWS tokyo
#LOCAL = '/home/work/%s'                            # official server prefix
#LOCAL = '/home/ubuntu/%s'                          # AWS server prefix
LOCAL = '/home/jinyuan/Downloads/%s'               # local server prefix


TRANSCODED_LOCAL_DIR = LOCAL % 'STATIC/news/ts/'
TRANSCODED_PUBLIC_DIR = PUBLIC % 'ts/'

IMAGES_LOCAL_DIR = LOCAL % 'STATIC/news/img/'
IMAGES_PUBLIC_DIR = PUBLIC % 'img/'

MEDIA_LOCAL_DIR = LOCAL % 'STATIC/news/mid/'
MEDIA_PUBLIC_DIR = PUBLIC % 'mid/'

MEDIA_TEMP_LOCAL_DIR = LOCAL % 'STATIC/news/tmp/'

NEWS_TEMPLATE = LOCAL % 'STATIC/news/templates/index.html'
NEWS_TEMPLATE_ARABIC = LOCAL % 'STATIC/news/templates/index_arabic.html'
UCK_TRANSCODING = 'http://gate.baidu.com/tc?m=8&from=bdpc_browser&src='
UCK_TRANSCODING_NEW = 'http://m.baidu.com/openapp?/webapp?debug=1&from=bd_international&onlyspdebug=1&structpage&siteType=7&nextpage=1&siteappid=1071361&src='
TRANSCODED_ENCODING = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'

CODE_BASE = LOCAL % 'newsman'
COMMAND_CLEAN_MEMORY = "python %s/newsman/watchdog/clean_memory.py"

TRANSCODING_BTN_EN = 'Original page'
TRANSCODING_BTN_PT = 'Página original'
TRANSCODING_BTN_JA = '元のページ'
TRANSCODING_BTN_IND = 'Laman Asli'
TRANSCODING_BTN_TH = 'หน้าเดิม'
TRANSCODING_BTN_AR = 'ﺎﻠﻤﺻﺩﺭ'
TRANSCODING_BTN_ZH_CN = '查看原始网页'
TRANSCODING_BTN_ZH_HK = '查看原始鏈接'

HOTNEWS_TITLE_EN = 'Hot News'
HOTNEWS_TITLE_PT = 'Notícias Quentes'
HOTNEWS_TITLE_JA = '人気ニュース'
HOTNEWS_TITLE_IND = 'Berita Terbaru'
HOTNEWS_TITLE_TH = 'ข่าวฮิต'
HOTNEWS_TITLE_AR = 'أخبار عاجلة'
HOTNEWS_TITLE_ZH_CN = '查看原始网页'
HOTNEWS_TITLE_ZH_HK = '查看原始鏈接'

DATABASE_REMOVAL_DAYS = 90
MEMORY_RESTORATION_DAYS = 20
MEMORY_EXPIRATION_DAYS = 20

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
