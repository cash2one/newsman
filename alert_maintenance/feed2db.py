#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# feed2db works to turn text-based feed list into database
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jul. 30, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from administration.config import Collection
from administration.config import db
from administration.config import FEED_REGISTRAR

file_suffix = '/home/jinyuan/Downloads/global-mobile-news/alert_maintenance/maintenance/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    if line:
        task = line.split('*|*')
        return task[0], task[1], task[2], task[3]
    else:
        return None


def _convert(language='en'):
    """
    turn text-based feed infor into database items
    """
    feeds_list = open('%s%s_feeds_list.txt' % (file_suffix, language), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    for line in lines:
        if line.strip():
            language, category, feed_title, feed_link = _parse_task(line)
