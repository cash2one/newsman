#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from data_processor import transcoder

def _main(url, transcoder):
    print transcoder.convert('en', '123 test', url, transcoder, 'test')

if __name__ == "__main__":
    url = sys.argv[1]

    transcoder = "chengdujin"
    if len(sys.argv) > 2:
        transcoder = sys.argv[2]
    _main(url, transcoder)

