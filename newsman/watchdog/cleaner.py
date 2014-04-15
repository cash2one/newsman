#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
cleaner is an interface file to clean database, memory and files on disk
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Jan 2, 2013'

import calendar
import clean_database
import clean_memory
import clean_disk
import clean_process
from datetime import datetime, timedelta
from newsman.config.settings import logger
import sys
import time

# CONSTANTS
from newsman.config.settings import DATABASE_REMOVAL_DAYS

reload(sys)
sys.setdefaultencoding('UTF-8')


def is_overdue(time_stamp):
    """
    find out if the file is overdue
    """
    if not time_stamp:
        logger.error('Method malformed!')
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
        logger.error(str(k))
        return True


def _clean_data():
    """
    clean memory, database and files, usually run daily
    """
    logger.info('----------------------cleaning-------------------------')
    try:
        any_mistake = False
        # clean database
        if not clean_database.clean():
            logger.error('Error found cleaning database')
            any_mistake = True
        # clean memory
        if not clean_memory.clean():
            logger.error('Error found cleaning memory')
            any_mistake = True
        # clean disk
        if not clean_disk.clean():
            logger.error('Error found cleaning disk')
            any_mistake = True

        if not any_mistake:
            logger.info('Memory, Database & Disk got cleaned!')
            return True
        else:
            return False
    except Exception as k:
        logger.error(str(k))
        return False


def _clean_zombies():
    """
    kill zombie processes, usually run semi-daily, or quasi-daily
    """
    logger.info('-----------------killing zombies--------------------')
    try:
        clean_process.clean()
        return True
    except Exception as k:
        logger.error(str(k))
        return False


if __name__ == "__main__":
    modes = {'data': '_clean_data', 'zombie': '_clean_zombies'}
    mode = sys.argv[1]
    eval(modes[mode])()
