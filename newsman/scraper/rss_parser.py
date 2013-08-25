#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
rss_parser finds all information in an rss item
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from BeautifulSoup import BeautifulStoneSoup
import calendar
import chardet
from config import hparser
from data_processor import image_helper
from datetime import datetime, timedelta
import feedparser
import html2text
import re
import time
import urllib2

# CONSTANTS
from config import LANGUAGES
from config import MEMORY_RESTORATION_DAYS


# TODO: add more boundary checks
# TODO: [register unsupported date format](http://pythonhosted.org/feedparser/date-parsing.html#advanced-date)
# TODO: add tags
# TODO: add thumbnail limit(downward)
def _read_entry(e=None, feed_id=None, feed_title=None, language=None, categories=None):
    """
    read a specific entry item from a feed 
    Note. categories are ids of category item
    """
    if not e or not feed_title or not language or not categories:
        raise Exception(
                "[rss_parser._read_entry:44L] ERROR: Method signature not well formed for %s!" % feed_title)
    if language not in LANGUAGES:
        raise Exception("[rss_parser._read_entry:46L] ERROR: Language not supported for %s!" % feed_title)

    entry = {}
    entry['feed_id'] = feed_id
    entry['feed'] = feed_title.strip()
    entry['language'] = language.strip()
    entry['categories'] = categories

    # the easy part: the must-have
    try:
        # article original link
        entry['error'] = []
        entry['link'] = e.link.strip()
        # article title
        if e.title_detail.type != 'text/plain':
            entry['title'] = urllib2.unquote(hparser.unescap(e.title.strip()))
        else:
            entry['title'] = e.title.strip()
        # remove possible htmlized title
        entry['title'] = re.sub("<.*?>", " ", entry['title'])
    except AttributeError as k:
        print '[rss_parser._read_entry:65L]', str(k)
        entry['error'].append(k + '\n')
        raise Exception(
            '[rss_parser._read_entry] ERROR: No title or link found for %s!' % entry['feed_id'])

    # article published time
    # first try parsed time info
    try:
        entry['updated'] = calendar.timegm(e.updated_parsed)
        entry['updated_human'] = e.updated
    except AttributeError as k:
        try:
            entry['updated'] = calendar.timegm(e.published_parsed)
            entry['updated_human'] = e.published
        except AttributeError as k:
            entry['error'] = '%s\n%s' % (
                entry['error'], "no 'updated_parsed' or 'published_parsed'")
            # then try unparsed time info
            # this is rarely possible.
            try:
                updated = e.updated if 'updated' in e else e.published
                if updated:
                    # get time zone
                    offset = int(updated[-5:])
                    delta = timedelta(hours=offset / 100)
                    format = "%a , %d %b %Y %H:%M:%S"
                    if updated[-8:-5] != 'UTC':
                        updated = datetime.strptime(updated[:-6], format)
                    else:
                        updated = datetime.strptime(updated[:-9], format)
                    updated -= delta
                    entry['updated'] = time.mktime(updated.timetuple())
                else:
                    raise ValueError(
                        "[rss_parser._read_entry] attribute updated/published has no value")
            except ValueError as k:
                print '[rss_parser._read_entry:101L]', str(k)
                entry['error'] = '%s\n%s' % (entry['error'], k)
                raise Exception(
                    '[rss_parser._read_entry] ERROR: entry %s has no publication info!' % entry['title'])
            except AttributeError as k:
                print '[rss_parser._read_entry:106L]', str(k)
                entry['error'].append('no update or published\n')
                raise Exception(
                    '[rss_parser._read_entry] ERROR: entry %s has no publication info!' % entry['title'])

    # article's summary
    try:
        # its possible summary is html-based
        summary = urllib2.unquote(hparser.unescap(e.summary))
        if isinstance(summary, str):
            summary_encoding = chardet.detect(summary)['encoding']
            summary = summary.decode(summary_encoding, 'ignore')
        # a <div, for example, and a </div
        is_html = True if len(
            re.findall(u'</?a|</?p|</?strong|</?img|</?html|</?div', summary)) > 1 else False
        if is_html:
            h = html2text.HTML2Text()
            h.ignore_images = True
            h.ignore_links = True
            h.ignore_emphasis = True
            paragraphs = (h.handle(summary)).strip('#').split('\n\n')
            paragraphs_above_limit = []
            # remove paragraphs that contain less than x number of words
            for paragraph in paragraphs:
                if entry['language'].startswith('zh') or entry['language'] == 'ja':
                    if len(paragraph) > 18:
                        paragraphs_above_limit.append(paragraph)
                else:
                    words = paragraph.split()
                    if len(words) > 12:
                        paragraphs_above_limit.append(paragraph)
            entry['summary'] = '\n\n'.join(paragraphs_above_limit)
        else:
            entry['summary'] = summary
    except AttributeError as k:
        entry['summary'] = None
    entry['summary'] = None if not entry['summary'] else entry['summary']

    # article's images
    # e.g. [{'url':'http://image.com/test.jpg, 'width': u'130', 'height':
    # u'86'}]
    entry['images'] = []
    try:
        images = image_helper.normalize(e.media_content)
        if images:
            entry['images'].extend(images)
    except AttributeError as k:
        pass
    try:
        images = image_helper.normalize(e.media_thumbnail)
        if images:
            entry['images'].extend(images)
    except AttributeError as k:
        pass
    for attribute in e:
        if 'thumbnail' in attribute:
            # currently set thumbnail to None if its a dictionary
            image = e[attribute] if isinstance(e[attribute], str) else None
            image = image_helper.normalize(image)
            if image:
                entry['images'].extend(image)
    try:
        links = e.links
        for link in links:
            if 'type' in link and 'image' in link.type:
                if 'href' in link:
                    image = image_helper.normalize(link.href)
                    if image:
                        entry['images'].extend(image)
    except AttributeError as k:
        pass
    if entry.has_key('summary') and entry['summary']:
        soup = BeautifulStoneSoup(entry['summary'])
        if soup.img:
            if soup.img.get('src'):
                images = image_helper.normalize(soup.img['src'])
                if images:
                    entry['images'].extend(images)
    # dedup images is processed at rss.py

    # article's author
    # e.g. Yuan Jin
    try:
        # i guess this could be a string or a list
        entry['author'] = e.author
    except AttributeError as k:
        entry['author'] = None

    # article's source
    # e.g. {'href': u'http://www.reuters.com/', 'title': u'Reuters'}
    try:
        entry['source'] = e.source
    except AttributeError as k:
        entry['source'] = None

    # article's tags
    # e.g. [{'term': u'Campus Party', 'scheme': None, 'label': None}]
    # term is usually combined with scheme to form a url; label is
    # the name of term
    try:
        entry['tags'] = e.tag
    except AttributeError as k:
        entry['tags'] = None

    return entry


# TODO: boundary checkers
# TODO: update parsing info to feed database
def parse(feed_link=None, feed_id=None, feed_title=None, language=None, categories=None, etag=None, modified=None):
    """
    read rss/atom data from a given feed
    feed_id is the feed ObjectId in MongoDB
    Etag and Modified are used to save rss http server's bandwidth
    Note: category should be added to feed table/database
    """
    if not feed_link or not feed_id or not language or not categories:
        raise Exception(
            "[rss_parser.parse] ERROR: Method signature not well formed for %s!" % feed_link)
    if language not in LANGUAGES:
        raise Exception("[rss_parser.parse] ERROR: Language not supported for %s!" % feed_link)

    def _validate_time(entry):
        """
        see if the entry's updated time is earlier than needed
        """
        deadline = datetime.utcfromtimestamp(
            entry['updated']) + timedelta(days=MEMORY_RESTORATION_DAYS)
        return True if deadline > datetime.now() else False

    # variables d and e follow feedparser tradition
    d = feedparser.parse(feed_link, etag=etag, modified=modified)
    if d:
        # http://pythonhosted.org/feedparser/reference-status.html
        # http://pythonhosted.org/feedparser/http-etag.html#http-etag
        status = d.status
        if status == 301:
            raise Exception(
                '[rss_parser.parse] ERROR: %s has been permantently moved to a %s!' % (feed_link, d.href))
        elif status == 304:
            print '[rss_parser.parse] WARNING: %s server has not updated its feeds' % feed_link
        elif status == 410:
            raise Exception(
                '[rss_parser.parse] ERROR: %s is gone! Admin should check the feed availability!' % feed_link)
        elif status == 200 or status == 302:
            # no need to worry.
            if status == 302:
                print '[rss_parser.parse] WARNING: %s url has been temp moved to a new place' % feed_link

            if not feed_title:
                # if title were not found in feed, an AttributeError would be
                # raised.
                feed_title = urllib2.unquote(hparser.unescape(d.feed.title)).strip()
            else:
                feed_title = feed_title.strip()
                feed_title_latest = urllib2.unquote(hparser.unescape(d.feed.title)).strip()
                if feed_title != feed_title_latest:
                    # change feed title
                    print '[rss_parser.parse] WARNING: %s title changed! Please update feed table/database' % feed_link
                    print '    old title:', feed_title
                    print '    new title:', feed_title_latest

            # update etag/modified
            etag = None
            modified = None
            try:
                etag = d.etag
            except AttributeError:
                try:
                    modified = d.modified
                except AttributeError:
                    pass

            if 'entries' in d:
                language = language if 'language' not in d else d.language
                # an Exception might be raised from _read_entry
                entries = [_read_entry(e, feed_id, feed_title, language, categories)
                           for e in d.entries]
                return filter(_validate_time, entries), status, feed_title, etag, modified
            else:
                raise Exception("[rss_parser.parse] ERROR: Feed %s has no items!" % feed_id)
        else:
            raise Exception(
                '[rss_parser.parse] ERROR: HTTP ERROR CODE %i for %s' % (status, feed_link))
    else:
        raise Exception("[rss_parser.parse] ERROR: Cannot parse %s correctly!" % feed_id)