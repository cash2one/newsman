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

import threading
from image_processor import image_helper


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
        self.result = eval(self.transcoder)(self.url)


def _combine(content, images):
    """
    combine results from transcoders
    """
    if not content or not images:
        return content, images

    # for now, if there are more than one image, take only one of them
    biggest = image_helper.find_biggest_image(images)
    IMAGE_TAG = '<img src="%s" width="%s" height="%s">'
    image = IMAGE_TAG % (biggest['url'], str(biggest['width']), str(biggest['height']))
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
            simplr_content, simplr_images = threads['simplr'].result
    if 'burify' in transcoders and 'burify' in threads:
        if threads['burify'].result:
            readability_content, readability_images = threads['burify'].result

    # use different combinations to create a news page with pictures
    if 'simplr' in transcoders or 'burify' in transcoders:
        if 'simplr' in transcoders and simplr_content:
            # if simplr found any image
            if simplr_images:
                return simplr_content, simplr_images
            elif uck_images: # add images from uck
                return _combine(simplr_content, uck_images)
            else: # no image at all
                return simplr_content, simplr_images
        elif 'burify' in transcoders and burify_content:
            # if burify found any image
            if burify_images:
                return burify_content, burify_images
            elif uck_images: # add images from uck
                return _combine(burify_content, uck_images)
            else: # no image at all
                return burify_content, burify_images
    # only uck
    if uck_content:
        return uck_content, uck_images
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
    _transcode(link, transcoders)

    '''
    #transcoded = transcode_by_readability(link)
    transcoded = TRANSCODED_ENCODING + transcode_by_readability(link)   # lijun
    
    import re

    # adding attribute for htmls : lijun
    jpgindex = transcoded.find('jpg')
    if jpgindex != -1:
        strinfo = re.compile('.jpg"')
        transcoded = strinfo.sub('.jpg" width=100% height="auto"', transcoded)

    pngindex = transcoded.find('png')
    if pngindex != -1:
        strinfo = re.compile('.png"')
        transcoded = strinfo.sub('.png" width=100% height="auto"', transcoded)
    '''
    results = transcode_by_uck(language, title, link)
    if results:
        transcoded, images = results
        # demo to return an exception
        if not transcoded:
            raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))
        # sanitizing work put here
        web_path, local_path = generate_path(transcoded, relative_path)
        if not web_path:
            raise Exception('ERROR: Cannot generate web path for %s properly!' % link)
        return web_path, local_path, images
    else:
        raise Exception('ERROR: Transcoder %s failed for %s' % ('UCK', link))
