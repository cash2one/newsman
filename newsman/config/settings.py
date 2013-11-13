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
import logging

# mongodb client
from pymongo.connection import Connection
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
con = Connection('127.0.0.1:27017')
db = Database(con, 'news')

# redis rclient
import redis
from redis import ConnectionError
rclient = redis.StrictRedis(host='10.240.35.40', port=6379)
#rclient = redis.StrictRedis(host='127.0.0.1')

# htmlparser to do unescaping
from HTMLParser import HTMLParser
hparser = HTMLParser()


# CONSTANTS
PUBLIC = 'http://220.181.163.36:8080/news/%s'      # cq01-rdqa-dev067.cq01
#PUBLIC = 'http://mobile-global.baidu.com/news/%s'  # hk01-hao123-mob01/mob02
#PUBLIC = 'http://180.76.2.34/%s'                   # hk01-hao123-mob00
#PUBLIC = 'http://54.251.107.116/%s'                # AWS singapore
#PUBLIC = 'http://54.232.81.44/%s'                  # AWS sao paolo
#PUBLIC = 'http://54.248.227.71/%s'                 # AWS tokyo
LOCAL = '/home/users/jinyuan/%s'                            # official server prefix
#LOCAL = '/home/work/%s'                            # official server prefix
#LOCAL = '/home/ubuntu/%s'                          # AWS server prefix
#LOCAL = '/home/jinyuan/Downloads/%s'               # local server prefix

# Logo folder
LOGO_PUBLIC_PREFIX = 'http://220.181.163.36:8080/logos/'
#LOGO_PUBLIC_PREFIX = 'http://mobile-global.baidu.com/logos/'

# code base folder for updating
CODE_BASE = LOCAL % 'newsman'

# logging settings
LOG_FORMAT = "%(levelname)-8s %(asctime)-25s %(lineno)-3d:%(filename)-16s %(message)s"
# critical, error, warning, info, debug, notset
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger('news-logger')
logger.setLevel(logging.WARNING)

# paths for generating transcoded files, mp3 and images
TRANSCODED_LOCAL_DIR = LOCAL % 'STATIC/news/ts/'
TRANSCODED_PUBLIC_DIR = PUBLIC % 'ts/'

IMAGES_LOCAL_DIR = LOCAL % 'STATIC/news/img/'
IMAGES_PUBLIC_DIR = PUBLIC % 'img/'

MEDIA_LOCAL_DIR = LOCAL % 'STATIC/news/mid/'
MEDIA_PUBLIC_DIR = PUBLIC % 'mid/'

# path for generating temporary files (used in mp3 download)
MEDIA_TEMP_LOCAL_DIR = LOCAL % 'STATIC/news/tmp/'

# templates for new page
NEWS_TEMPLATE_1 = LOCAL % 'STATIC/news/templates/news1.html'
NEWS_TEMPLATE_2 = LOCAL % 'STATIC/news/templates/news2.html'
NEWS_TEMPLATE_3 = LOCAL % 'STATIC/news/templates/news3.html'
NEWS_TEMPLATE_ARABIC = LOCAL % 'STATIC/news/templates/index_arabic.html'

# Stop words
STOP_WORDS = "%s/newsman/data_processor/stopwords/" % CODE_BASE 

# uck transcoding web service url
UCK_TRANSCODING = 'http://gate.baidu.com/tc?m=8&from=bdpc_browser&src='
UCK_TRANSCODING_NEW = 'http://m.baidu.com/openapp?/webapp?debug=1&from=bd_international&onlyspdebug=1&structpage&siteType=7&nextpage=1&siteappid=1071361&src='

# meta info for a new page
TRANSCODED_ENCODING = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'

# words on 'opening origial page' button
TRANSCODING_BTN_EN = 'Original page'
TRANSCODING_BTN_PT = 'Página original'
TRANSCODING_BTN_JA = '元のページ'
TRANSCODING_BTN_IN = 'Laman Asli'
TRANSCODING_BTN_TH = 'หน้าเดิม'
TRANSCODING_BTN_AR = 'ﺎﻠﻤﺻﺩﺭ'
TRANSCODING_BTN_ZH = '查看原始网页'

# hot news title
HOTNEWS_TITLE_EN = 'Hot News'
HOTNEWS_TITLE_PT = 'Notícias Quentes'
HOTNEWS_TITLE_JA = '人気ニュース'
HOTNEWS_TITLE_IN = 'Berita Terbaru'
HOTNEWS_TITLE_TH = 'ข่าวฮิต'
HOTNEWS_TITLE_AR = 'أخبار عاجلة'
HOTNEWS_TITLE_ZH = '头条'

# expirations 
DATABASE_REMOVAL_DAYS = 365
FEED_UPDATE_DAYS = 2
MEMORY_EXPIRATION_DAYS = 20

# database names
FEED_REGISTRAR = 'feeds'
KEYWORD_REGISTRAR = 'keywords'

# settings used in summarizing
PARAGRAPH_CRITERIA = 40
SUMMARY_LENGTH_LIMIT = 500

# request connection timeouts
UCK_TIMEOUT = 40  # 14 seconds timeout
GOOGLE_TTS_TIMEOUT = 120  # 2 minutes timeout

# supported languages
LANGUAGES = ['en', 'th', 'in', 'ja', 'pt', 'ar', 'zh']
# supported countries, in code
COUNTRIES = ['AU', 'BR', 'CA', 'CN', 'EG', 'FR', 'GB', 'HK', 'ID', 'IN', 'JP', 'KR', 'TH', 'TR', 'TW', 'US', 'VN']

# sizes for generating images
MIN_IMAGE_SIZE = 150, 150
THUMBNAIL_STYLE = 1.4
THUMBNAIL_LANDSCAPE_SIZE_HIGH = 600, 226
THUMBNAIL_LANDSCAPE_SIZE_NORMAL = 450, 169
THUMBNAIL_LANDSCAPE_SIZE_LOW = 230, 85
THUMBNAIL_PORTRAIT_SIZE_HIGH = 310, 400
THUMBNAIL_PORTRAIT_SIZE_NORMAL = 175, 210
THUMBNAIL_PORTRAIT_SIZE_LOW = 90, 110
CATEGORY_IMAGE_SIZE = 300, 200
HOT_IMAGE_SIZE = 600, 226
