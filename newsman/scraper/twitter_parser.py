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

from config.settings import logger
from config.settings import TWITTER_ACCESS_TOKEN_KEY
from config.settings import TWITTER_ACCESS_TOKEN_SECRET
from config.settings import TWITTER_CONSUMER_KEY
from config.settings import TWITTER_CONSUMER_SECRET
import twitter
import urllib2

# twitter api interface
api = twitter.Api(consumer_key, consumer_secret, access_token_key, access_token_secret)


def _read_entry(status):
    """
    scrape information related to Twitter tweet
    """
    if not status:
        logger.error("Method malformed!")


def parse(screen_name, feed_id, feed_title, language, categories, etag):
    """
    Connect twitter and parses the timeline
    """
    count = 200
    # since_id is the latest stored tweet id
    # count limits the number of replies, maxium 200
    statuses = api.GetUserTimeline(screen_name, since_id=etag, count=count)
    entries = []
    for s in statuses:
        entry = _read_entry()
        if entry:
            entries.append(entry)


if __name__ == "__main__":
    pass
