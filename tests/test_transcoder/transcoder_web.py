#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# transcoder_web provides a web interface for three transcoders
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Aug. 10, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

import web
from data_processor import transcoder

render = web.template.render('templates/')
urls = (
    "/transcode", "Transcoders"
)


class Transcoders:
    def GET(self):
        data = web.input(url="this should not be seen", language='no language')
        return self._transcode(data.language, data.url)

    
    def _transcode(self, language, url):
        """
        call each transcoder
        """
        transcoded_simplr = transcoder.convert(language=language, link=url, transcoder='chengdujin', stdout=True)
        #transcoded_burify = transcoder.convert(language=language, link=url, transcoder='readability', stdout=True)
        #transcoded_baidu_uck = transcoder.convert(language=language, link=url, transcoder='uck', stdout=True)
        #return self._combine(transcoded_simplr, transcoded_burify, transcoded_baidu_uck)
        return transcoded_simplr

    
    def _combine(self, s, r, u):
        """
        combine results from each transcoder
        """
        return render.combiner(s, r, u)
    

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
