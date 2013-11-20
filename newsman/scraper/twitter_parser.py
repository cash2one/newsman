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
import twitter
import urllib2

# CONSTANTS
from config.settings import LANGUAGES
from config.settings import TWITTER_ACCESS_TOKEN_KEY
from config.settings import TWITTER_ACCESS_TOKEN_SECRET
from config.settings import TWITTER_CONSUMER_KEY
from config.settings import TWITTER_CONSUMER_SECRET

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


def parse(screen_name=None, feed_id=None, feed_title=None, language=None, categories=None, etag=None):
    """
    Connect twitter and parses the timeline
    """
    if not screen_name:
        logger.error('No screen name found!')
        return None, None, None, None, None, None
    if not feed_id:
        logger.error('Feed not registered!')
        return None, None, None, None, None, None
    if not feed_title:
        logger.error('Feed does not have a name!')
        return None, None, None, None, None, None
    if not language or language not in LANGUAGES:
        logger.error('Language %s not supported!' % language)
        return None, None, None, None, None, None 
    if not categories:
        logger.error('No category is found!')
        return None, None, None, None, None, None 
        
    try:
        # since_id is the latest stored tweet id
        # count limits the number of replies, maxium 200
        statuses = api.GetUserTimeline(screen_name, since_id=etag)
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
        return entries, 200, feed_title, etag_new if etag_new else etag, None, 'Ok' 
    except Exception as k:
        logger.error(str(k))
        return None, None, None, None, None, str(k) 


if __name__ == "__main__":
    parse('2chnews_j', 'xxxx', '2ch matome', 'ja', ['JP::News'], None)
