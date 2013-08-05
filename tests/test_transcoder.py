#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from data_processor import transcoder

print transcoder.convert('en', '旅情そそるクルーズ列車大ヒット　ＪＲ九州「ななつ星」来春まで満席　東西も追随へ', 'http://sankei.jp.msn.com/economy/news/130803/biz13080321140003-n1.htm', 'readability', 'test')
