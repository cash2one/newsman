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
sys.path.append('/home/ubuntu/bgm_news')

import calendar
from datetime import datetime, timedelta
import time
from watchdog import clean_database, clean_memory, clean_disk
from watchdog import clean_process

# CONSTANTS
from config import DATABASE_REMOVAL_DAYS


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


def _clean_data():
    """
    clean memory, database and files, usually run daily
    """
    print '----------------------cleaning-------------------------'
    # clean database
    clean_database.clean()
    # clean memory
    clean_memory.clean()
    # clean disk
    clean_disk.clean()


def _clean_zombies():
    """
    kill zombie processes, usually run semi-daily, or quasi-daily
    """
    print '----------------------killing zombies-------------------------'
    clean_process.clean()


if __name__ == "__main__":
    modes = {'data':'_clean_data', 'zombie':'_clean_zombies'}
    mode = sys.argv[1]
    eval(modes[mode])()
