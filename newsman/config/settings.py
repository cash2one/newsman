#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
config.py contains most CONSTANTS in the project
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Jan 17, 2013'

import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

# SERVICES
import logging

# mongodb client
from pymongo.connection import Connection
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid, ConnectionFailure

con = None
try:
    con = Connection('127.0.0.1:27017')
except ConnectionFailure:
    con = Connection('10.240.82.21:27017')
db = Database(con, 'news')

# redis rclient
import redis
from redis import ConnectionError

rclient = redis.StrictRedis(host='127.0.0.1', port=6379, socket_timeout=5,
                            charset='utf-8')
try:
    rclient.ping()
except ConnectionError:
    rclient = redis.StrictRedis(host='10.240.82.21', port=7777,
                                socket_timeout=5, charset='utf-8')
    # dump file: /var/log/dump.rdb

# htmlparser to do unescaping
from HTMLParser import HTMLParser

hparser = HTMLParser()


# CONSTANTS
PUBLIC = 'http://s.mobile-global.baidu.com/news/%s'  #
# hk01-hao123-mob01/mob02.hk01
#PUBLIC = 'http://180.76.2.34/news/%s'                # hk01-hao123-mob00.hk01
#PUBLIC = 'http://180.76.3.51/news/%s'                # hk01-hao123-mob07.hk01

LOCAL = '/home/work/%s'  # official server prefix
#LOCAL = '/home/jinyuan/Downloads/%s'               # local server prefix

# Obsolete
##PUBLIC = 'http://220.181.163.36:8080/news/%s'        # cq01-rdqa-dev067.cq01
##PUBLIC = 'http://54.251.107.116/%s'                  # AWS singapore
##PUBLIC = 'http://54.232.81.44/%s'                    # AWS sao paolo
##PUBLIC = 'http://54.248.227.71/%s'                   # AWS tokyo
##LOCAL = '/home/users/jinyuan/%s'                   # tests server in China
##LOCAL = '/home/ubuntu/%s'                          # AWS server prefix


LOGO_PUBLIC_PREFIX = 'http://s.mobile-global.baidu.com/logos/'
#LOGO_PUBLIC_PREFIX = 'http://220.181.163.36:8080/logos/'

# code base folder for updating
CODE_BASE = LOCAL % 'newsman'

# logging settings
LOG_FORMAT = "%(levelname)-8s %(asctime)-25s %(lineno)-3d:%(filename)-16s %(" \
             "message)s"
# critical, error, warning, info, debug, notset
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger('news-logger')
logger.setLevel(logging.WARNING)
# supress requests logging info
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

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
NEWS_TEMPLATE_1 = LOCAL % 'STATIC/news/templates/news1.html'  # no image,
# no font resizing
NEWS_TEMPLATE_2 = LOCAL % 'STATIC/news/templates/news2.html'  # with image,
# no font resizing
NEWS_TEMPLATE_3 = LOCAL % 'STATIC/news/templates/news3.html'  # no image,
# with font resizing
NEWS_TEMPLATE_4 = LOCAL % 'STATIC/news/templates/news4.html'  # with image,
# with font resizing
NEWS_TEMPLATE_ARABIC = LOCAL % 'STATIC/news/templates/index_arabic.html'

# Data paths
DATA_PATH = "%s/newsman/data/" % CODE_BASE

# Thai segmentation input and output file
THAI_WORDSEG = LOCAL % "wordseg_thai/wordseg_thai"
THAI_WORDSEG_DICT = LOCAL % "wordseg_thai/wordseg_thai_dict/thai_utf8"

# uck transcoding web service url
UCK_TRANSCODING = 'http://gate.baidu.com/tc?m=8&from=bdpc_browser&src='
UCK_TRANSCODING_NEW = 'http://m.baidu' \
                      '.com/openapp?/webapp?debug=1&from=bd_international' \
                      '&onlyspdebug=1&structpage&siteType=7&nextpage=1' \
                      '&siteappid=1071361&src='

# meta info for a new page
TRANSCODED_ENCODING = '<meta http-equiv="Content-Type" content="text/html; ' \
                      'charset=utf-8"/>\n'

# Font used to generate text-based image
FONT_PATH_EN = LOCAL % "fonts/ubuntu-font/Ubuntu-R.ttf"
FONT_PATH_IN = LOCAL % "fonts/ubuntu-font/Ubuntu-R.ttf"
FONT_PATH_JA = LOCAL % "fonts/ja_ipaexm/ipaexm.ttf"
FONT_PATH_PT = LOCAL % "fonts/ubuntu-font/Ubuntu-R.ttf"
FONT_PATH_TH = LOCAL % "fonts/th_tlwg/Loma.ttf"
FONT_PATH_ZH = LOCAL % "fonts/zh_yahei/msyh.ttf"
TEXT_WIDTH_EN = 24
TEXT_WIDTH_IN = 24
TEXT_WIDTH_JA = 11
TEXT_WIDTH_PT = 24
TEXT_WIDTH_TH = 22
TEXT_WIDTH_ZH = 12

# headers for url connecting
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, '
                  'like Gecko) Chrome/31.0.1650.63 Safari/537.36'}

# Twitter API
TWITTER_ACCESS_TOKEN_KEY = "24129666-M47Q6pDLZXLQy1UITxkijkTdKfkvTcBpleidNPjac"
TWITTER_ACCESS_TOKEN_SECRET = "0zHhqV5gmrmsnjiOEOBCvqxORwsjVC5ax4mM3dCDZ7RLk"
TWITTER_CONSUMER_KEY = "hySdhZgpj5gF12kRWMoVpQ"
TWITTER_CONSUMER_SECRET = "2AkrRg89SdJL0qHkHwuP933fiBaNTioChMpxRdoicUQ"

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

# Summarization
TOP_KEYWORDS_LIMIT = 10
SCORED_SENTENCE_LIMIT = 5

# expirations 
DATABASE_REMOVAL_DAYS = 90
FEED_UPDATE_DAYS = 2
MEMORY_EXPIRATION_DAYS = 30
FEED_UPDATE_TIMEOUT = 5400

# database names
FEED_REGISTRAR = 'feeds'
KEYWORD_REGISTRAR = 'keywords'

# settings used in summarizing
PARAGRAPH_CRITERIA_LATIN = 30
PARAGRAPH_CRITERIA_KANJI = 40
PARAGRAPH_CRITERIA_THAI = 18
SUMMARY_LENGTH_LIMIT = 500

# request connection timeouts
UCK_TIMEOUT = 60  # 14 seconds timeout
GOOGLE_TTS_TIMEOUT = 120  # 2 minutes timeout

# supported languages
LANGUAGES = ['ar', 'en', 'in', 'ja', 'th', 'pt', 'zh']
# supported countries, in code
COUNTRIES = ['AU', 'BR', 'CA', 'CN', 'EG', 'FR', 'GB', 'HK', 'ID', 'IN', 'JP',
             'KR', 'TH', 'TR', 'TW', 'US', 'VN']

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
