#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
Twitter parser parses specific twitter account in real time
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Nov. 19, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')

from config.settings import ACCESS_TOKEN_KEY
from config.settings import ACCESS_TOKEN_SECRET
from config.settings import consumer_key
from config.settings import consumer_secret
import twitter
import urllib2


api = twitter.Api(consumer_key, consumer_secret, access_token_key, access_token_secret)

def parse(screen_name, feed_id, feed_title, language, categories):
    """
    Connect twitter and parses the timeline
    """
    pass


if __name__ == "__main__":
    pass
