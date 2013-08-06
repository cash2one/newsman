#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# first_paragraph  extracts summary or first paragraph from news
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# #created Jul. 29, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')


def extract():
    """
    get the first paragraph, only text
    """
    # if summary from rss provider is found
    #     use summary, but limit the number of words
    # else if summary could be generated
    #     use summary, limit the number of words
    # else find first paragraph from transcoded
    #     also limit the number of words

