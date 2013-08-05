#!/usr/bin/python
# -*- coding: utf-8 -*-

# transcoder is the main interface for several transcoders
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import baidu_uck
import burify
from administration.config import hparser
from image_processor import image_helper
import os
import simplr
import threading

from administration.config import NEWS_TEMPLATE
from administration.config import NEWS_TEMPLATE_ARABIC
from administration.config import TRANSCODED_LOCAL_DIR
from administration.config import TRANSCODED_PUBLIC_DIR
from administration.config import TRANSCODING_BTN_AR
from administration.config import TRANSCODING_BTN_EN
from administration.config import TRANSCODING_BTN_IND
from administration.config import TRANSCODING_BTN_JA
from administration.config import TRANSCODING_BTN_PT
from administration.config import TRANSCODING_BTN_TH

# create a local dir for transcoded content if dir does not exist
if not os.path.exists(TRANSCODED_LOCAL_DIR):
    os.mkdir(TRANSCODED_LOCAL_DIR)


class TranscoderAPI(threading.Thread):
    """
    call a transcoder
    """
    def __init__(self, url="this should not exist", transcoder="simplr"):
        threading.Thread.__init__(self)
        self.transcoder = transcoder
        self.url = url
        self.result = None

    def run(self):
        self.result = eval(self.transcoder).convert(self.url)


def _save(data, path):
    """
    save the file on local disk and return web and local path
    """
    if not data or not path:
        return None

    local_path = '%s%s.html' % (TRANSCODED_LOCAL_DIR, path)
    web_path = '%s%s.html' % (TRANSCODED_PUBLIC_DIR, path)

    f = open(local_path, 'w')
    f.write(hparser.unescape(content))
    f.close()
    return web_path, local_path


def _compose(language, title, content):
    """
    combine content with a template
    """
    if not content or not language or not title:
        raise Exception("ERROR: Method not well formed!")

    transcode_button = {'en': TRANSCODING_BTN_EN, 'ja': TRANSCODING_BTN_JA, 'th': TRANSCODING_BTN_TH, 'pt':
                        TRANSCODING_BTN_PT, 'ind': TRANSCODING_BTN_IND, 'en-rIN': TRANSCODING_BTN_EN, 'ar': TRANSCODING_BTN_AR}

    # f reads the template
    f = None
    if language == 'ar':
        f = open(NEWS_TEMPLATE_ARABIC, 'r')
    else:
        f = open(NEWS_TEMPLATE, 'r')
    # a template is found
    if f:
        template = str(f.read())
        f.close()
        return template % (title, title, content, transcode_button[language])
    else:
        raise Exception("ERROR: Cannot find a template!")


def _combine(content, images):
    """
    combine results from transcoders
    """
    if not content or not images:
        return content, images

    # for now, if there are more than one image, take only one of them
    biggest = image_helper.find_biggest_image(images)
    IMAGE_TAG = '<img src="%s" width="%s" height="%s">'
    image = IMAGE_TAG % (
        biggest['url'], str(biggest['width']), str(biggest['height']))
    return "%s %s" % (image, content), images


# TODO: add http string checkers
def _transcode(url, transcoders):
    """
    organize different transcoders
    """
    if not url or not transcoders:
        raise Exception("ERROR: Method not well formed!")

    threads = {}
    for transcoder in transcoders:
        transcoding_request = TranscoderAPI(url, transcoder)
        # thread could be found via transcoder name
        threads[transcoder] = transcoding_request
        transcoding_request.start()
        # 10 second to wait UCK server
        transcoding_request.join(10 * 1000)

    # after a while ... put data in the proper variables
    if 'baidu_uck' in transcoders and 'baidu_uck' in threads:
        if threads['baidu_uck'].result:
            uck_content, uck_images = threads['baidu_uck'].result
    if 'simplr' in transcoders and 'simplr' in threads:
        if threads['simplr'].result:
            simplr.title, simplr_content, simplr_images = threads['simplr'].result
    if 'burify' in transcoders and 'burify' in threads:
        if threads['burify'].result:
            burify_title, burify_content, burify_images = threads['burify'].result

    # use different combinations to create a news page with pictures
    if 'simplr' in transcoders or 'burify' in transcoders:
        if 'simplr' in transcoders and simplr_content:
            # if simplr found any image
            if simplr_images:
                return simplr_title, simplr_content, simplr_images
            elif uck_images:  # add images from uck
                new_content, new_images = _combine(simplr_content, uck_images)
                return simplr_title, new_content, new_images
            else:  # no image at all
                return simplr_title, simplr_content, simplr_images
        elif 'burify' in transcoders and burify_content:
            # if burify found any image
            if burify_images:
                return burify_title, burify_content, burify_images
            elif uck_images:  # add images from uck
                new_content, new_images = _combine(burify_content, uck_images)
                return burify_title, new_content, new_images
            else:  # no image at all
                return burify_title, burify_content, burify_images
    # only uck
    if uck_content:
        return "", uck_content, uck_images
    else:
        raise Exception("ERROR: UCK failed!")


def _organize_transcoders(transcoder="chengdujin"):
    """
    get data from different transcoders
    chengdujin: simplr.py
    readability: burify.py
    uck: baidu_uck.py
    """
    transcoders = []
    if transcoder == 'chengdujin':
        transcoders.append("simplr")
        transcoders.append("baidu_uck")
    elif transcoder == 'readability':
        transcoders.append("burify")
        transcoders.append("baidu_uck")
    else:
        transcoders.append("baidu_uck")
    return transcoders


def _preprocess(link):
    """
    get the real address out
    """
    last_http_index = link.rfind('http')
    return link[last_http_index:].strip()


def convert(language="en", title=None, link=None, transcoder="chengdujin", relative_path=None):
    """
    select a transcoder
    send the link
    gather the data
    combine them with the template
    generate paths
    return news and images
    """
    if not language or not title or not link or not relative_path:
        raise Exception('ERROR: Method not well formed!')

    link = _preprocess(link)
    transcoders = _organize_transcoders(transcoder)
    title_new, content, images = _transcode(link, transcoders)
    # in case uck cannot find a proper title
    if title_new:
        title = title_new

    if content:
        # embed content in template
        news = _compose(language, title, content)
        # create web/local path
        web_path, local_path = _save(news, relative_path)
        return web_path, local_path, images
    else:
        raise Exception("ERROR: Transcoder %s failed for %s" %
                        (transcoder, link))
