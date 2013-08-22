#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
cleaner is an interface file to clean database, memory and files on disk
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('/home/jinyuan/Downloads/bgm_news')

from bson.objectid import ObjectId
import calendar
from config import Collection, db
from config import rclient
from datetime import datetime, timedelta
import feedparser
import os
from scraper import memory
import time
from watchdog import clean_database, clean_memory, clean_disk

# CONSTANTS
from config import DATABASE_REMOVAL_DAYS
from config import IMAGES_LOCAL_DIR
from config import IMAGES_PUBLIC_DIR
from config import LANGUAGES
from config import MEMORY_RESTORATION_DAYS
from config import TRANSCODED_LOCAL_DIR
from config import TRANSCODED_PUBLIC_DIR


def is_overdue(time_stamp):
    """
    find out if the file is overdue
    """
    if not time_stamp:
        return False

    deadline_datetime = datetime.utcfromtimestamp(time_stamp) + timedelta(days=DATABASE_REMOVAL_DAYS)
    deadline_posix = calendar.timegm(deadline_datetime.timetuple())
    now_posix = time.mktime(time.gmtime())

    if deadline_posix < now_posix:  # deadline is earlier than now
        return True
    else:
        return False


def clean():
    """
    cleaner interface
    """
    print '----------------------cleaning-------------------------'
    # clean database
    clean_database.clean()
    # clean memory
    clean_memory.clean()
    # clean disk
    clean_disk.clean()


if __name__ == "__main__":
    clean()
