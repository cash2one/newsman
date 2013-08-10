#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

import web
render = web.template.render('templates/')

from data_processor import simplr, baidu_uck, readability

urls = (
    "/transcode/(.*)", "Transcoders"
)


class Transcoders:
    def GET(self, url):
        return _transcode(url)
    
    def _transcode(self, url):
        """
        call each transcoder
        """
        transcoded_simplr = render.simplr(url)
        transcoded_readability = render.readability(url)
        transcoded_baidu_uck = render.baidu_uck(url)
        return
    
    def _combine(self, s, r, u):
        """
        combine results from each transcoder
        """
        pass

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
