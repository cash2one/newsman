#!/usr/bin/python
# -*- coding: utf-8 -*-

# transcoder is the main interface for several transcoders
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from decruft import Document
from administration.config import hparser
import Image
from administration.config import NEWS_TEMPLATE
from administration.config import NEWS_TEMPLATE_ARABIC
import os
import re
from cStringIO import StringIO
from image_processor import thumbnail
from administration.config import MIN_IMAGE_SIZE
from administration.config import TRANSCODING_BTN_EN
from administration.config import TRANSCODING_BTN_JA
from administration.config import TRANSCODING_BTN_TH
from administration.config import TRANSCODING_BTN_PT
from administration.config import TRANSCODING_BTN_IND
from administration.config import TRANSCODED_ENCODING   # lijun
from administration.config import TRANSCODED_LOCAL_DIR
from administration.config import TRANSCODED_PUBLIC_DIR
from administration.config import UCK_TRANSCODING
import urllib2
import urlparse


if not os.path.exists(TRANSCODED_LOCAL_DIR):
    os.mkdir(TRANSCODED_LOCAL_DIR)

transcoding_button_language = {
    'en': TRANSCODING_BTN_EN, 'ja': TRANSCODING_BTN_JA,
    'th': TRANSCODING_BTN_TH, 'pt': TRANSCODING_BTN_PT,
    'ind': TRANSCODING_BTN_IND, 'en-rIN': TRANSCODING_BTN_EN
}


def process_url(link):
    if link and link.count('http') > 1:
        p = link.rpartition('http')
        if p:
            return '%s%s' % (p[1], p[2])
        else:
            return None
    else:
        return link


def generate_path(content, relative_path):
    ''''''
    if not content or not relative_path:
        return None
    local_path = '%s%s.html' % (TRANSCODED_LOCAL_DIR, relative_path)
    web_path = '%s%s.html' % (TRANSCODED_PUBLIC_DIR, relative_path)
    f = open(local_path, 'w')
    f.write(hparser.unescape(content))
    f.close()
    return web_path, local_path


def transcode_by_readability(link):
    ''''''
    if not link:
        return None
    f = urllib2.urlopen(link)
    return Document(f.read()).summary()


def _organize_transcoders(transcoder="chengdujin"):
    """
    get data from different transcoders
    """
    transcoders = []
    if transcoder == 'chengdujin':
        transcoders.append("simplr")
        transcoders.append("uck")
    elif transcoder == 'burify':
        transcoders.append("readability")
        transcoders.append("uck")
    else:
        transcoders.append("uck")
    return transcoders


def _preprocess(link):
    """
    get the real address out
    """
    last_http_index = link.rfind('http')
    return link[last_http_index:].strip()


def convert(language="en", title=None, link=None, transcoder="chengdujin", relative_path=None):
    """
    select a transcoder
    send the link
    gather the data
    combine them with the template
    generate paths
    return news and images
    """
    if not language or not title or not link or not relative_path:
        raise Exception('ERROR: Method not well formed!')
    
    link = _preprocess(link)
    transcoders = _organize_transcoders(transcoder)

    '''
    #transcoded = transcode_by_readability(link)
    transcoded = TRANSCODED_ENCODING + transcode_by_readability(link)   # lijun
    
    import re

    # adding attribute for htmls : lijun
    jpgindex = transcoded.find('jpg')
    if jpgindex != -1:
        strinfo = re.compile('.jpg"')
        transcoded = strinfo.sub('.jpg" width=100% height="auto"', transcoded)

    pngindex = transcoded.find('png')
    if pngindex != -1:
        strinfo = re.compile('.png"')
        transcoded = strinfo.sub('.png" width=100% height="auto"', transcoded)
    '''
    results = transcode_by_uck(language, title, link)
    if results:
        transcoded, images = results
        # demo to return an exception
        if not transcoded:
            raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))
        # sanitizing work put here
        web_path, local_path = generate_path(transcoded, relative_path)
        if not web_path:
            raise Exception('ERROR: Cannot generate web path for %s properly!' % link)
        return web_path, local_path, images
    else:
        raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))
