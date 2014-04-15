#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
transcoder is the main interface for several transcoders
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Jan 2, 2013'

import baidu_uck
import baidu_uck_new
import burify
import chardet
from newsman.config.settings import hparser
from newsman.config.settings import logger
import illustrator
import os
import requests
import simplr
from slimmer import html_slimmer
import sys
import threading
import time
import urllib2

# CONSTANTS
#from newsman.config.settings import NEWS_TEMPLATE_1
#from newsman.config.settings import NEWS_TEMPLATE_2
from newsman.config.settings import NEWS_TEMPLATE_3
from newsman.config.settings import NEWS_TEMPLATE_4
from newsman.config.settings import NEWS_TEMPLATE_ARABIC
from newsman.config.settings import TRANSCODED_LOCAL_DIR
from newsman.config.settings import TRANSCODED_PUBLIC_DIR
from newsman.config.settings import TRANSCODING_BTN_AR
from newsman.config.settings import TRANSCODING_BTN_EN
from newsman.config.settings import TRANSCODING_BTN_IN
from newsman.config.settings import TRANSCODING_BTN_JA
from newsman.config.settings import TRANSCODING_BTN_PT
from newsman.config.settings import TRANSCODING_BTN_TH
from newsman.config.settings import TRANSCODING_BTN_ZH
from newsman.config.settings import UCK_TIMEOUT

TRANSCODE_BUTTON = {'en': TRANSCODING_BTN_EN, 'ja': TRANSCODING_BTN_JA,
                    'th': TRANSCODING_BTN_TH, 'pt': TRANSCODING_BTN_PT,
                    'in': TRANSCODING_BTN_IN, 'ar': TRANSCODING_BTN_AR,
                    'zh': TRANSCODING_BTN_ZH}

reload(sys)
sys.setdefaultencoding('UTF-8')


# create a local dir for transcoded content if dir does not exist
if not os.path.exists(TRANSCODED_LOCAL_DIR):
    os.mkdir(TRANSCODED_LOCAL_DIR)


class TranscoderAPI(threading.Thread):
    """
    call a transcoder
    """

    def __init__(self, url="no_url", transcoder="simplr", language=None):
        threading.Thread.__init__(self)
        self.transcoder = transcoder
        self.url = url
        self.language = language
        self.result = None

    def run(self):
        if self.transcoder == 'simplr':
            self.result = eval(self.transcoder).convert(
                self.url, self.language)
        else:
            try:
                self.result = eval(self.transcoder).convert(self.url)
            except Exception as k:
                logger.error(str(k))
                self.result = None, None, None


def _save(data, path):
    """
    save the file on local disk and return web and local path
    """
    if not data or not path:
        logger.error('Method malformed!')
        return None, None

    try:
        local_path = '%s%s.html' % (TRANSCODED_LOCAL_DIR, path)
        web_path = '%s%s.html' % (TRANSCODED_PUBLIC_DIR, path)

        f = open(local_path, 'w')
        f.write(urllib2.unquote(hparser.unescape(data)).replace(u'\xa0', ' '))
        f.close()
        return web_path, local_path
    except Exception as k:
        logger.error(str(k))
        return None, None


def _compose(language=None, title=None, updated=None, feed=None, content=None,
             images=None):
    """
    combine content with a template
    """
    if not content or not language or not title:
        logger.error("Method malformed!")
        return None

    try:
        # sub-info
        updated_sub_info = time.strftime(
            "%m %d, %Y",
            time.strptime(time.ctime(updated))) if updated else None
        sub_info = '%s | %s' % (feed, updated_sub_info)

        # select appropriate template
        news_template = NEWS_TEMPLATE_4 if images and len(
            images) > 0 else NEWS_TEMPLATE_3
        f = open(news_template, 'r')

        # a template is found
        if f:
            template = str(f.read())
            f.close()
            return template % (
                title, title, sub_info, content, TRANSCODE_BUTTON[language])
        else:
            logger.error("Template %s contains no data!" % news_template)
            return None
    except Exception as k:
        logger.error(str(k))
        return None


def _sanitize(content):
    """
    sanitize the content
    """
    if not content:
        return content

    content = content.replace("<noscript>", "")
    content = content.replace("</noscript>", "")
    return content


def _combine(content, images):
    """
    combine results from transcoders
    """
    if not content or not images:
        return content, images

    try:
        # for now, if there are more than one image, take only one of them
        biggest = illustrator.find_biggest_image(images)
        if biggest:
            image_tag = '<img src="%s" width="%s" height="%s">'
            image = image_tag % (
                biggest['url'], str(biggest['width']), str(biggest['height']))
            return "%s %s" % (image, content), images
        else:
            logger.info('Cannot find biggest image')
            return content, biggest
    except Exception as k:
        logger.error(str(k))
        return content, images


# TODO: add http string checkers
def _transcode(url, transcoders, language=None):
    """
    organize different transcoders
    """
    if not url or not transcoders:
        logger.error("Method malformed!")
        return None, None, None

    try:
        threads = {}
        for transcoder in transcoders:
            if transcoder == 'simplr':
                transcoding_request = TranscoderAPI(url, transcoder, language)
            else:
                transcoding_request = TranscoderAPI(url, transcoder)
            # thread could be found via transcoder name
            threads[transcoder] = transcoding_request
            transcoding_request.start()
            # UCK_TIMEOUT seconds to wait UCK server
            #transcoding_request.join(UCK_TIMEOUT + 5)
            transcoding_request.join()

        # after a while ... put data in the proper variables
        uck_content = uck_new_content = simplr_content = burify_content = None
        uck_images = uck_new_images = simplr_images = burify_images = None
        uck_title = uck_new_title = simplr_title = burify_title = None

        if 'baidu_uck' in transcoders and 'baidu_uck' in threads:
            if threads['baidu_uck'].result:
                uck_title, uck_content, uck_images = threads[
                    'baidu_uck'].result
        if 'baidu_uck_new' in transcoders and 'baidu_uck_new' in threads:
            if threads['baidu_uck_new'].result:
                uck_new_title, uck_new_content, uck_new_images = threads[
                    'baidu_uck_new'].result
        if 'simplr' in transcoders and 'simplr' in threads:
            if threads['simplr'].result:
                simplr_title, simplr_content, simplr_images = threads[
                    'simplr'].result
        if 'burify' in transcoders and 'burify' in threads:
            if threads['burify'].result:
                burify_title, burify_content, burify_images = threads[
                    'burify'].result

        # use different combinations to create a news page with pictures
        if 'simplr' in transcoders or 'burify' in transcoders:
            if 'simplr' in transcoders and simplr_content:
                # handle cases title cannot be retrieved
                simplr_title = simplr_title if simplr_title else uck_title

                # if simplr found any image
                if simplr_images:
                    return simplr_title, simplr_content, simplr_images
                elif uck_images:  # add images from uck
                    new_content, new_images = _combine(
                        simplr_content, uck_images)
                    return simplr_title, new_content, new_images
                else:  # no image at all
                    return simplr_title, simplr_content, simplr_images
            elif 'burify' in transcoders and burify_content:
                # handle cases title cannot be retrieved
                burify_title = burify_title if burify_title else uck_title

                # if burify found any image
                if burify_images:
                    return burify_title, burify_content, burify_images
                elif uck_images:  # add images from uck
                    new_content, new_images = _combine(
                        burify_content, uck_images)
                    return burify_title, new_content, new_images
                else:  # no image at all
                    return burify_title, burify_content, burify_images

        # uck and uck_new
        if 'baidu_uck' in transcoders and uck_content:
            return uck_title, uck_content, uck_images
        elif 'baidu_uck_new' in transcoders and uck_new_content:
            return uck_new_title, uck_new_content, uck_new_images
        else:
            return None, None, None
    except Exception as k:
        logger.error(str(k))
        return None, None, None


def _organize_transcoders(transcoder="chengdujin"):
    """
    get data from different transcoders
    chengdujin: simplr.py
    readability: burify.py
    uck: baidu_uck.py
    nuck: baidu_uck_new.py
    """
    transcoders = []
    if transcoder == 'chengdujin':
        transcoders.append("simplr")
        transcoders.append("baidu_uck")
    elif transcoder == 'readability':
        transcoders.append("burify")
        transcoders.append("baidu_uck")
    elif transcoder == 'uck':
        transcoders.append("baidu_uck")
    elif transcoder == 'nuck':
        transcoders.append('baidu_uck_new')
    return transcoders


def _preprocess(url):
    """
    get the real address out
    """
    if not url:
        logger.error('Method malformed!')
        return None

    try:
        last_http_index = url.rfind('http')
        return url[last_http_index:].strip()
    except Exception as k:
        logger.error(str(k))
        return None


def prepare_link(url):
    """
    decode with the correct encoding
    """
    if not url:
        logger.error('Method malformed!')
        return None

    try:
        resp = requests.get(url, timeout=UCK_TIMEOUT)
        html = resp.content if resp.ok else None
        if html:
            detected = chardet.detect(html)
            encoding = detected['encoding'] if detected else 'utf-8'
            encoding = 'windows-1252' if 'folha.uol.com.br' in url else encoding
            data = html.decode(encoding, 'ignore')
            return hparser.unescape(urllib2.unquote(data)).replace(u'\xa0', ' ')
        else:
            logger.warning("Cannot read %s" % url)
            return None
    except Exception as k:
        logger.info('Problem:[%s] Source:[%s]' % (str(k), url))
        return None


def convert(language="en", title=None, link=None, updated=None, feed=None,
            transcoder="chengdujin", relative_path=None, stdout=False):
    """
    select a transcoder
    send the link
    gather the data
    combine them with the template
    generate paths
    return news and images
    * stdout is to print result directly, no saving to physical disk related
    * stdout default value False
    """
    if not language or not link:
        logger.error('Method malformed! language: %s link: %s' %
                     (language, link))
        if not stdout:
            return None, None, None, None
        else:
            return None, None

    try:
        link_clean = _preprocess(link)
        if link_clean:
            # this wont suck
            transcoders = _organize_transcoders(transcoder)
            title_new, content, images = _transcode(
                link_clean, transcoders, language)
            # remove null content
            content = content.strip() if content else None

            # in case no title is found from feed information
            if not title:
                title = title_new

            if content and title:
                # slimmer the content
                content = html_slimmer(content)
                if not stdout:
                    # embed content in template
                    news = _compose(
                        language, title, updated, feed, _sanitize(content),
                        images)
                    if news:
                        # create web/local path
                        web_path, local_path = _save(news, relative_path)
                        if web_path:
                            # the FINAL return
                            return web_path, local_path, content, images
                        else:
                            if not stdout:
                                return None, None, None, None
                            else:
                                return None, None
                    else:
                        logger.error(
                            'Cannot combine content with the template!')
                        if not stdout:
                            return None, None, None, None
                        else:
                            return None, None
                else:
                    return title, content
            else:
                if not content:
                    logger.info('Transcoder %s failed for %s' %
                                (transcoder, link_clean))
                else:
                    logger.info('Cannot find title for %s' % link_clean)

                if not stdout:
                    # original link is returned as transcoded path
                    logger.info('Original link %s is used as transcoded path')
                    return link_clean, None, None, None
                else:
                    return None, None
        else:
            logger.error(
                'Link [clean %s] [original %s] cannot be parsed' % (
                    link_clean, link))
            if not stdout:
                return None, None, None, None
            else:
                return None, None
    except Exception as k:
        logger.error(str(k))
        if not stdout:
            return None, None, None, None
        else:
            return None, None
