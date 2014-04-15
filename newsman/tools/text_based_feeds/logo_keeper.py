#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
logo_keeper puts feed logos into database
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Oct. 29, 2013


import sys

reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

from config.settings import Collection
from config.settings import db
import os

# CONSTANTS
from config.settings import FEED_REGISTRAR

#LOGOS_PUBLIC_PREFIX = 'http://mobile-global.baidu.com/logos/'
#LOGOS_PUBLIC_PREFIX = 'http://220.181.163.36:8080/logos/'

#LOGOS_PREFIX = '/home/work/nginx/html/logos/'
#LOGOS_PREFIX = '/home/users/jinyuan/.jumbo/srv/http/logos/'
#LOGOS_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds
# /logos/'

#FILE_PREFIX = '/home/work/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/users/jinyuan/newsman/newsman/bin/text_based_feeds
# /feed_lists/'
#FILE_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds
# /feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    line = line.strip()
    if line:
        task = line.strip().split('*|*')
        # task[1] refers to categories
        if len(task) == 5:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[
                3].strip(), task[4].strip(), None
        elif len(task) == 6:
            return task[0].strip(), task[1].strip(), task[2].strip(), task[
                3].strip(), task[4].strip(), task[5].strip()
        else:
            return None
    else:
        return None


def _convert(language='en', country=None):
    """
    turn text-based feed infor into database items
    Note. 1. categories: [(), ()]
    """
    logo_list = os.listdir('%s%s_%s' % (LOGOS_PREFIX, language, country))

    # read in file content
    feeds_list = open('%s%s_%s_feeds_list' %
                      (FILE_PREFIX, language, country), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    new_feeds_list = open('%s%s_%s_feeds_list_new' %
                          (FILE_PREFIX, language, country), 'w')

    for line in lines:
        if line.strip():
            language, category, transcoder, link, title, labels = _parse_task(
                line)
            found_logo = False
            for logo in logo_list:
                logo_clean = logo.replace('.png', "").lower()
                if logo_clean in link.lower():
                    logo_path = "%s%s_%s/%s" % (
                        LOGOS_PUBLIC_PREFIX, language, country, logo)
                    if labels:
                        new_feeds_list.write(
                            '%s*|*%s*|*%s*|*%s*|*%s*|*%s*|*%s\n' % (
                                language, category, transcoder, link, title,
                                logo_path, labels))
                    else:
                        new_feeds_list.write('%s*|*%s*|*%s*|*%s*|*%s*|*%s\n' % (
                            language, category, transcoder, link, title,
                            logo_path))
                    found_logo = True
                    break
            if not found_logo:
                print title

    new_feeds_list.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _convert(sys.argv[1], sys.argv[2])
    else:
        print 'Please indicate a language and country'
