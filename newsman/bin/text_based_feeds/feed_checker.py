#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
feed2db works to turn text-based feed list into database
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 30, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

from config.settings import Collection
from config.settings import db

# CONSTANTS
from config.settings import FEED_REGISTRAR
FILE_PREFIX = '/home/users/jinyuan/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/work/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/ubuntu/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds/feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    line = line.strip()
    if line:
        task = line.strip().split('*|*')
        # task[1] refers to categories
        if len(task) == 5:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[3].strip(), task[4].strip(), None
        else:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[3].strip(), task[4].strip(), task[5].strip()
    else:
        return None


def _convert(language='en', country=None):
    """
    turn text-based feed infor into database items
    Note. 1. categories: [(), ()]
    """
    # read in file content
    feeds_list = open('%s%s_%s_feeds_list' %
                      (FILE_PREFIX, language, country), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    link_dict = title_dict = {}

    for line in lines:
        if line.strip():
            language, category, transcoder, link, title, labels = _parse_task(
                line)
            # link check
            if link not in link_dict:
                link_dict[link] = title
            else:
                print link, title
            # title check
            if title not in title_dict:
                title_dict[title] = link
            else:
                print title, link

if __name__ == "__main__":
    if len(sys.argv) > 1:
        _convert(sys.argv[1], sys.argv[2])
    else:
        print 'Please indicate a language and country'
