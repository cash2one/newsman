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
        return None

    try:
        if status.text:
            entry = {}
            splits = [t.strip() for t in status.text.split() if t.strip() and not t.startswith('#') and 't.co' not in t]
            entry['title'] = ''.join(splits)
            entry['updated_human'] = status.created_at
            entry['updated'] = status.created_at_in_seconds
            for url in s.urls:
                req = urllib2.Request(url.url)
                resp = urllib2.urlopen(req)
                entry['link'] = resp.geturl()
            entry['tags'] = []
            for hashtag in s.hashtags:
                entry[tags].append(hashtag.text)

            # check link
            if not entry['link'] or not entry['updated']:
                return None
            else:
                return entry
        else:
            return None
    except Exception as k:
        logger.error(str(k))
        return None


def parse(screen_name, feed_id, feed_title, language, categories, etag):
    """
    Connect twitter and parses the timeline
    """
    # since_id is the latest stored tweet id
    # count limits the number of replies, maxium 200
    count = 200
    statuses = api.GetUserTimeline(screen_name, since_id=etag, count=count)
    entries = []
    etag_new = None
    for status in statuses:
        if not etag_new:
            etag_new = status.id
        entry = _read_entry(status)
        if entry:
            # supplement other information
            entry['feed_id'] = feed_id
            entry['feed'] = feed_title
            entry['language'] = language
            entry['categories'] = categories
            entries.append(entry)


if __name__ == "__main__":
    pass
