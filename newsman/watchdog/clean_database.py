#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
daily work, clean expired items and its place in queues in memory
"""
__author__ = 'chengdujin'
__contact__ = 'chengdujin@gmail.com'
__created__ = 'Aug. 22, 2013'

from bson.objectid import ObjectId
import calendar
import clean_disk
import clean_memory
from datetime import datetime, timedelta
from newsman.config.settings import Collection, db
from newsman.config.settings import logger
import sys
import time

# CONSTANTS
from newsman.config.settings import FEED_REGISTRAR
from newsman.config.settings import DATABASE_REMOVAL_DAYS

reload(sys)
sys.setdefaultencoding('UTF-8')


def clean_by_item(candidate):
    """
    remove candidate in database
    """
    if not candidate:
        logger.error('Method malformed! %s' % str(candidate))
        return False

    try:
        document_name = candidate['language']
        document = Collection(db, document_name)
        document.remove({'_id': ObjectId(candidate['_id'])})
        return True
    except Exception as k:
        logger.error(str(k))
        return False


def _find_document_names():
    """
    find all documents
    note. documents are represented by language
    """
    try:
        feeds = Collection(db, FEED_REGISTRAR)
        document_names = []
        # only get language and _id
        items = feeds.find({}, {'language': 1})
        if items:
            document_names = [item['language'] for item in items]
        return list(set(document_names))
    except Exception as k:
        logger.error(str(k))
        return None


def clean():
    """
    remove expired items from database
    """
    logger.info('... cleaning database ...')
    try:
        document_names = _find_document_names()
        if document_names:
            for document_name in document_names:
                document = Collection(db, document_name)

                # compute a threshold
                current_utc_time_posix = calendar.timegm(time.gmtime())
                deadline_datetime = datetime.utcfromtimestamp(
                    current_utc_time_posix) - timedelta(
                    days=DATABASE_REMOVAL_DAYS)
                deadline_posix = calendar.timegm(deadline_datetime.timetuple())

                removal_candidates = document.find(
                    {'updated': {'$lt': deadline_posix}})
                for removal_candidate in removal_candidates:
                    # see if removal candidate has a footage in memory
                    clean_memory.clean_by_item(str(removal_candidate['_id']))
                    # remove corresponding files on disk
                    clean_disk.clean_by_item(removal_candidate)
                    # remove the candidate in database
                    document.remove({'_id': removal_candidate['_id']})
            return True
        else:
            logger.error('Cannot find documents')
            return False
    except Exception as k:
        logger.error(str(k))
        return False


if __name__ == "__main__":
    clean()
