#!/usr/bin/python
# -*- coding: utf-8 -*-

# call burify's implementation of readability code to transcode a web page
# 
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Aug. 6, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import chardet
from readability import Document
import urllib2


def _prepare_link(url):
    """
    decode with the correct encoding
    """
    html = urllib2.urlopen(url).read()
    if html:
        detected = chardet.detect(html)
        if detected:
            data = html.decode(detected['encoding'])
        else:
            data = html.decode('utf-8')
    else:
        raise Exception("ERROR: Cannot read %s" % url)


def convert(link):
    """
    use burify's readability implementation to transcode a web page
    and return the transcoded page and images found in it
    """
    if not link:
        raise Exception('ERROR: Cannot transcode nothing!')
