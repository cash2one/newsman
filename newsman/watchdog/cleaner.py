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
sys.path.append('/home/jinyuan/Downloads/newsman/newsman')

import calendar
from config import logging
from datetime import datetime, timedelta
import time
import clean_database
import clean_memory
import clean_disk
import clean_process

# CONSTANTS
from config import DATABASE_REMOVAL_DAYS


def is_overdue(time_stamp):
    """
    find out if the file is overdue
    """
    if not time_stamp:
        logging.error('Method malformed!')
        return True

    try:
        deadline_datetime = datetime.utcfromtimestamp(
            time_stamp) + timedelta(days=DATABASE_REMOVAL_DAYS)
        deadline_posix = calendar.timegm(deadline_datetime.timetuple())
        now_posix = time.mktime(time.gmtime())

        if deadline_posix < now_posix:  # deadline is earlier than now
            return True
        else:
            return False
    except Exception as k:
        logging.exception(str(k))
        return True


def _clean_data():
    """
    clean memory, database and files, usually run daily
    """
    print '----------------------cleaning-------------------------'
    try:
        any_mistake = False
        # clean database
        if not clean_database.clean():
            logging.error('Error found cleaning database')
            any_mistake = True
        # clean memory
        if clean_memory.clean():
            logging.error('Error found cleaning memory')
            any_mistake = True
        # clean disk
        if clean_disk.clean():
            logging.error('Error found cleaning disk')
            any_mistake = True

        if not any_mistake:
            logging.warning('Memory, Database & Disk got cleaned!')
            return True
        else:
            return False
    except Exception as k:
        logging.exception(str(k))
        return False


def _clean_zombies():
    """
    kill zombie processes, usually run semi-daily, or quasi-daily
    """
    print '----------------------killing zombies-------------------------'
    try:
        clean_process.clean()
        return True
    except Exception as k:
        logging.exception(str(k))
        return False


if __name__ == "__main__":
    modes = {'data': '_clean_data', 'zombie': '_clean_zombies'}
    mode = sys.argv[1]
    eval(modes[mode])()
