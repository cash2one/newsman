#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
daily work, clean expired items and its place in queues in memory
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 22, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

import calendar
import clean_disk, clean_memory
from config import Collection, db
from config import logging
from datetime import datetime, timedelta
import time

# CONSTANTS
from config import FEED_REGISTRAR
from config import DATABASE_REMOVAL_DAYS


def _find_document_names():
    """
    find all documents
    note. documents are represented by language
    """
    try:
        feeds = Collection(db, FEED_REGISTRAR)
        document_names = []
        # only get language and _id
        items = feeds.find({}, {'language':1})
        if items:
            document_names = [item['language'] for item in items]
        return list(set(document_names))
    except Exception as k:
        pass
        logging.exception(str(k))
        return None


def clean():
    """
    remove expired items from database
    """
    logging.info('... cleaning database ...')
    try:
        document_names = _find_document_names()
        if document_names:
            for document_name in document_names:
                document = Collection(db, document_name)

                # compute a threshold
                current_utc_time_posix = calendar.timegm(time.gmtime())
                deadline_datetime = datetime.utcfromtimestamp(current_utc_time_posix) - timedelta(days=DATABASE_REMOVAL_DAYS)
                deadline_posix = calendar.timegm(deadline_datetime.timetuple())

                removal_candidates = document.find({'updated': {'$lt': deadline_posix}})
                for removal_candidate in removal_candidates:
                    # see if removal candidate has a footage in memory
                    clean_memory.clean_by_item(str(removal_candidate['_id']))
                    # remove corresponding files on disk
                    clean_disk.clean_by_item(removal_candidate)
                    # remove the candidate in database
                    document.remove({'_id': removal_candidate['_id']})
            return True
        else:
            logging.error('Cannot find documents')
            return False
    except Exception as k:
        pass
        logging.exception(str(k))
        return False


if __name__ == "__main__":
    clean()
