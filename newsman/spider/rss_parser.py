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
from config.settings import hparser
from config.settings import logger
from processor import illustrator
from datetime import datetime, timedelta
import feedparser
import html2text
import re
import socket
socket.setdefaulttimeout(10)  # 10 seconds
import time
import urllib2

# CONSTANTS
from config.settings import LANGUAGES
from config.settings import DATABASE_REMOVAL_DAYS
# prefix should not end with a slash
HIDDEN_LINKS = {'http://news.goo.ne.jp':
                ('div', 'lead fs16 bold'), 'http://news.nifty.com': ('li', 'headnews')}
AD_LINKS = 'http://rss.rssad.jp/rss/ad/'


def _get_actual_link(prefix, link):
    """
    find the actual news link
    """
    if not prefix or not link:
        logger.error(
            'Method malformed! Prefix:[%s], Link:[%s]' % (prefix, link))

    try:
        raw_data = urllib2.urlopen(link)
        """
        data = raw_data.readlines()
        # str() is critical
        soup = BeautifulStoneSoup(str(data))
        html_tag, html_class = HIDDEN_LINKS[prefix]
        html_wrapper = soup.find(name=html_tag, attrs={'class': html_class})
        if html_wrapper:
            actual_suffix = html_wrapper.find('a')['href']
            actual_link = str('%s%s' % (prefix, actual_suffix))
            return actual_link
        else:
            return None
        """
        return raw_data.geturl()
    except Exception as k:
        logger.info('Cannot open %s' % k)
        return None


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
        logger.error('Method malformed!')
        return None
    if language not in LANGUAGES:
        logger.error("Language not supported for %s!" % feed_title)
        return None

    try:
        entry = {}
        entry['feed_id'] = feed_id
        entry['feed'] = feed_title.strip()
        entry['language'] = language.strip()
        entry['categories'] = categories

        # the easy part: the must-have
        entry['error'] = []

        # article original link
        if e.link:
            original_link = e.link.strip()
            if not original_link.startswith(AD_LINKS):
                """
                matched_prefix = [
                    link for link in HIDDEN_LINKS if original_link.startswith(link)]
                found_prefix = matched_prefix[0] if matched_prefix else None
                if found_prefix:
                    actual_link = _get_actual_link(found_prefix, original_link)
                    if actual_link:
                        entry['link'] = actual_link
                    else:
                        logger.info('No actual link found!')
                        return None
                else:
                    entry['link'] = original_link
                """
                original_link = urllib2.unquote(
                    hparser.unescape(original_link))
                f = urllib2.urlopen(original_link)
                entry['link'] = f.geturl()
            else:
                logger.info('Advertising link %s' % original_link)
                return None
        else:
            logger.info('Feed malformed! No link found!')
            return None

        # article title
        if e.title_detail.type != 'text/plain':
            entry['title'] = urllib2.unquote(hparser.unescape(e.title.strip()))
        elif 'title' in e:
            entry['title'] = e.title.strip()
        else:
            entry['title'] = None
        # remove possible htmlized title
        entry['title'] = re.sub("<.*?>", " ", entry[
                                'title']) if 'title' in entry and entry['title'] else None

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
                entry['error'] = ['%s\n%s' % (
                    entry['error'], "no 'updated_parsed' or 'published_parsed'")]
                # then try unparsed time info
                # this is rarely possible.
                try:
                    updated = e.updated if 'updated' in e else e.published
                    if updated:
                        # get time zone
                        offset = int(updated[-5:])
                        delta = timedelta(hours=int(offset) / 100)
                        format = "%a, %d %b %Y %H:%M:%S"
                        if updated[-8:-5] != 'UTC':
                            updated = datetime.strptime(updated[:-6], format)
                        else:
                            updated = datetime.strptime(updated[:-9], format)
                        updated -= delta
                        entry['updated'] = time.mktime(updated.timetuple())
                    else:
                        logger.info(
                            "Attribute updated/published has no value")
                        return None
                except ValueError as k:
                    logger.info(str(k))
                    entry['error'].append('%s\n%s' % (entry['error'], k))
                    return None
                except AttributeError as k:
                    logger.info(str(k))
                    entry['error'].append('no update or published\n')
                    return None

        # article's summary
        try:
            # its possible summary is html-based
            summary = urllib2.unquote(hparser.unescape(e.summary))
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
            images, media_content_new = illustrator.find_images(
                e.media_content, entry['link'])
            if images:
                entry['images'].extend(images)
        except AttributeError as k:
            pass
        try:
            images, media_content_new = illustrator.find_images(
                e.media_thumbnail, entry['link'])
            if images:
                entry['images'].extend(images)
        except AttributeError as k:
            pass
        for attribute in e:
            if 'thumbnail' in attribute:
                # currently set thumbnail to None if its a dictionary
                image = e[attribute] if isinstance(e[attribute], str) else None
                image = illustrator.find_image(image, entry['link'])
                if image:
                    entry['images'].append(image)
        try:
            links = e.links
            for link in links:
                if 'type' in link and 'image' in link.type:
                    if 'href' in link:
                        image = illustrator.find_image(
                            link.href, entry['link'])
                        if image:
                            entry['images'].append(image)
        except AttributeError as k:
            pass

        if entry.has_key('summary') and entry['summary']:
            images, entry['summary'] = illustrator.find_images(
                entry['summary'], entry['link'])
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

        # the FINAL return
        return entry
    except Exception as k:
        logger.error(str(k))
        return None


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
        logger.error("Method malformed!")
        return None, None, feed_title, etag, modified, "Method malformed!"
    if language not in LANGUAGES:
        logger.error("Language not supported for %s!" % feed_link)
        return None, None, feed_title, etag, modified, "Language not supported for %s!" % feed_link

    def _validate_time(entry):
        """
        see if the entry's updated time is earlier than needed
        """
        deadline = datetime.utcfromtimestamp(
            entry['updated']) + timedelta(days=DATABASE_REMOVAL_DAYS)
        return True if deadline > datetime.now() else False

    try:
        # variables d and e follow feedparser tradition
        d = feedparser.parse(feed_link, etag=etag, modified=modified)
        if d:
            # http://pythonhosted.org/feedparser/reference-status.html
            # http://pythonhosted.org/feedparser/http-etag.html#http-etag
            status = d.status if 'status' in d else None

            if status == 301:
                logger.critical(
                    '%s has been permantently moved to a %s!' % (feed_link, d.href))
                return None, status, feed_title, etag, modified, '%s has been permantently moved to a %s!' % (feed_link, d.href)
            elif status == 304:
                logger.info('%s server has not updated its feeds' % feed_link)
                return None, status, feed_title, etag, modified, '%s server has not updated its feeds' % feed_link
            elif status == 410:
                logger.critical(
                    '%s is gone! Admin should check the feed availability!' % feed_link)
                return None, status, feed_title, etag, modified, '%s is gone! Admin should check the feed availability!' % feed_link
            elif status == 200 or status == 302:
                # no need to worry.
                if status == 302:
                    logger.info(
                        '%s url has been temp moved to a new place' % feed_link)

                if not feed_title:
                    # if title were not found in feed, an AttributeError would
                    # be raised.
                    feed_title = urllib2.unquote(
                        hparser.unescape(d.feed.title)).strip()
                else:
                    feed_title = feed_title.strip()
                    if 'title' in d.feed:
                        feed_title_latest = urllib2.unquote(
                            hparser.unescape(d.feed.title)).strip()
                        if feed_title != feed_title_latest:
                            # change feed title
                            logger.info(
                                '%s title changed! Please update feed table/database' % feed_link)
                            logger.info('old title: %s' % feed_title)
                            logger.info('new title: %s' % feed_title_latest)
                            #feed_title = feed_title_latest
                    else:
                        logger.info(
                            '%s[%s] has no title in its latest RSS' % (feed_title, feed_link))

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
                    entries = []
                    for i, e in enumerate(d.entries):
                        if e:
                            entry = _read_entry(
                                e, feed_id, feed_title, language, categories)
                            if entry:
                                entries.append(entry)
                            else:
                                logger.info('Cannot parse %s' % e['link'])
                                continue
                        else:
                            logger.info(
                                'No infomation found for %s-th entry' % i)
                            continue

                    if entries:
                        # the FINAL return
                        # the last one indicates nothing wrong happended in
                        # parsing
                        return filter(_validate_time, entries), status, feed_title, etag, modified, 'OK'
                    else:
                        logger.info('Feed parsing goes wrong!')
                        return None, status, feed_title, etag, modified, 'Feed parsing goes wrong!'
                else:
                    logger.info("Feed %s has no items!" % feed_id)
                    return None, status, feed_title, etag, modified, 'Feed %s has no items!' % feed_id
            else:
                logger.info(
                    'HTTP Error Code [%s] for %s' % (status, feed_link))
                return None, status, feed_title, etag, modified, 'HTTP Error Code [%s] for %s' % (status, feed_link)
        else:
            logger.info("Cannot parse %s correctly!" % feed_id)
            return None, None, feed_title, etag, modified, "Cannot parse %s correctly!" % feed_id
    except Exception as k:
        logger.exception('%s for %s' % (str(k), feed_id))
        return None, None, feed_title, etag, modified, '%s for %s' % (str(k), feed_id)
