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


def convert(link):
    """
    use burify's readability implementation to transcode a web page
    and return the transcoded page and images found in it
    """
    if not link:
        raise Exception('ERROR: Cannot transcode nothing!')
