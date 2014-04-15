#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
transcoder_web provides a web interface for three transcoders
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 10, 2013


import sys

reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

from processor import transcoder
import web

render = web.template.render('templates/')
urls = (
    "/transcode", "Transcoders"
)


class Transcoders:
    """
    Class to call different transcoders
    """

    def __init__(self):
        pass

    def GET(self):
        """
        web.py default get method
        """
        data = web.input(url="this should not be seen", language='no language')
        return self._transcode(data.language, data.url)

    def _transcode(self, language, url):
        """
        call each transcoder
        """
        title_simplr, content_simplr = transcoder.convert(
            language=language, link=url, transcoder='chengdujin', stdout=True)
        title_burify, content_burify = transcoder.convert(
            language=language, link=url, transcoder='readability', stdout=True)

        title_uck, content_uck = transcoder.convert(
            language=language, link=url, transcoder='uck', stdout=True)
        title_uck_new, content_uck_new = transcoder.convert(
            language=language, link=url, transcoder='uck_new', stdout=True)
        return render.combiner(title_simplr, content_simplr, title_burify,
                               content_burify, title_uck, content_uck,
                               title_uck_new, content_uck_new,
                               'Original Webpage')


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
