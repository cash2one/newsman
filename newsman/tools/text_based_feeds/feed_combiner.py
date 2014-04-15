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
#FILE_PREFIX = '/home/work/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/users/jinyuan/newsman/newsman/bin/text_based_feeds
# /feed_lists/'
#FILE_PREFIX = '/home/ubuntu/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds
# /feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    line = line.strip()
    if line:
        task = line.split('*|*')
        # task[1] refers to categories
        if len(task) == 4:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[
                3].strip(), None
        else:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[
                3].strip(), task[4].strip()
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

    feed_names = open('%s%s_%s_feed_titles' %
                      (FILE_PREFIX, language, country), 'r')
    names = feed_names.readlines()
    feed_names.close()
    name_dict = {}
    for name in names:
        if name.strip():
            name_splits = name.strip().split('*|*')
            name_dict[name_splits[0].strip()] = name_splits[1].strip()

    new_feeds_list = open('%s%s_%s_feeds_list_new' %
                          (FILE_PREFIX, language, country), 'w')

    for line in lines:
        if line.strip():
            language, category, transcoder, link, labels = _parse_task(line)
            if link in name_dict:
                if labels:
                    new_feeds_list.write('%s*|*%s*|*%s*|*%s*|*%s*|*%s\n' % (
                        language, category, transcoder, link, name_dict[link],
                        labels))
                else:
                    new_feeds_list.write('%s*|*%s*|*%s*|*%s*|*%s\n' % (
                        language, category, transcoder, link, name_dict[link]))
            else:
                print link

    new_feeds_list.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _convert(sys.argv[1], sys.argv[2])
    else:
        print 'Please indicate a language and country'
