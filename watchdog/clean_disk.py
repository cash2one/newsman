#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
daily, clean saved expired files, temporary files and unrecorded files on disk
"""
# @author chengudjin
# @contact chengdujin@gmail.com
# @created Aug. 22, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

import calendar
from config import Collection, db
from datetime import datetime, timedelta
import os
import time

# CONSTANS
from config import DATABASE_REMOVAL_DAYS
from config import IMAGES_LOCAL_DIR
from config import MEDIA_LOCAL_DIR
from config import MEDIA_TEMP_LOCAL_DIR
from config import TRANSCODED_LOCAL_DIR


def clean_by_item(candidate):
    """
    remove related files on disk of an item
    mp3_local, transcoded_local, hotnews_image_local, category_image_local, thumbnail_image_local
    """
    # mp3
    if candidate.has_key('mp3_local') and candidate['mp3_local']:
        if os.path.exists(candidate['mp3_local']):
            os.remove(candidate['mp3_local'])
    # transcoded
    if candidate.has_key('transcoded_local') and candidate['transcoded_local']:
        if os.path.exists(candidate['transcoded_local']):
            os.remove(candidate['transcoded_local'])
    # hotnews_image
    if candidate.has_key('hotnews_image_local') and candidate['hotnews_image_local']:
        if os.path.exists(candidate['hotnews_image_local']['url']):
            os.remove(candidate['hotnews_image_local']['url'])
    # category_image
    if candidate.has_key('category_image_local') and candidate['category_image_local']:
        if os.path.exists(candidate['category_image_local']['url']):
            os.remove(candidate['category_image_local']['url'])
    # thumbnail_image
    if candidate.has_key('thumbnail_image_local') and candidate['thumbnail_image_local']:
        if os.path.exists(candidate['thumbnail_image_local']['url']):
            os.remove(candidate['thumbnail_image_local']['url'])


def _clean_tempory_files():
    """
    remove temporary files
    """
    if os.path.exists(MEDIA_TEMP_LOCAL_DIR):
        temp_files = [os.path.join(MEDIA_TEMP_LOCAL_DIR, temp_file) for temp_file in os.listdir(MEDIA_TEMP_LOCAL_DIR)]
        if temp_files:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)


def _clean_unrecorded_files():
    """
    remove files not recorded in database, with a illegal status (longer than DATABASE_REMOVAL_DAYS)
    1. check if the file is overdue
    2. collect it with proper indication, i.e. what is it, an mp3 or an image? what document is it in?
    3. remove duplicates
    4. check if the file is still in database
    5. remove the file if it is not found in database
    """

    def _is_overdue(path):
        """
        find out if the file is overdue
        """
        if not path:
            return False
        if not os.path.exists(path):
            return False

        deadline_datetime = datetime.utcfromtimestamp(os.path.getctime(path)) + timedelta(days=DATABASE_REMOVAL_DAYS)
        deadline_posix = calendar.timegm(deadline_datetime.timetuple())
        now_posix = time.mktime(time.gmtime())

        if deadline_posix < now_posix:  # deadline is earlier than now
            return True
        else:
            return False

    # "en": [(transcoded_local', '/home/work/xxx.html'), ('mp3_local':'/home/work/xxx.mp3')]
    unrecorded_files = {}
    # mp3 files
    if os.path.exists(MEDIA_LOCAL_DIR):
        media_files = [os.path.join(MEDIA_LOCAL_DIR, media_file) for media_file in os.listdir(MEDIA_LOCAL_DIR) if _is_overdue(os.path.join(MEDIA_LOCAL_DIR, media_file))]
        for media_file in media_files:
            if os.path.exists(media_file):
                document_name = media_file.split('_')[0]  # en, en-rIN, pt
                if not unrecorded_files[document_name]:
                    unrecorded_files[document_name] = []
                unrecorded_files[document_name].append(('mp3_local', media_file))

    # image files
    if os.path.exists(IMAGES_LOCAL_DIR):
        image_files = [os.path.join(IMAGES_LOCAL_DIR, image_file) for image_file in os.listdir(IMAGES_LOCAL_DIR) if _is_overdue(os.path.join(IMAGES_LOCAL_DIR, image_file))]
        for image_file in image_files:
            if os.path.exists(image_file):
                document_name = image_file.split('_')[0]
                image_type = '%s_image_local' % os.path.splitext(image_file)[0].split('_')[-1]  # category_image_local
                if not unrecorded_files[document_name]:
                    unrecorded_files[document_name] = []
                unrecorded_files[document_name].append((image_type, image_file))

    # transcoded files
    if os.path.exists(TRANSCODED_LOCAL_DIR):
        transcoded_files = [os.path.join(TRANSCODED_LOCAL_DIR, transcoded_file) for transcoded_file in os.listdir(TRANSCODED_LOCAL_DIR) if _is_overdue(os.path.join(TRANSCODED_LOCAL_DIR, transcoded_file))]
        for transcoded_file in transcoded_files:
            if os.path.exists(transcoded_file):
                document_name = transcoded_file.split('_')[0]
                if not unrecorded_files[document_name]:
                    unrecorded_files[document_name] = []
                unrecorded_files[document_name].append(('transcoded_local', transcoded_file))

    # check and remove an unrecorded file
    for document_name, items in unrecorded_files.iteritems():
        # remove duplicated
        items = list(set(items))

        # check if a file is still in databse
        document = Collection(db, document_name)
        for item in items:
            field = item[0]
            path = item[1]
            found = document.find({field:path})
            if not found:
                # remove it if it were not
                # check if file exists again for safety
                if os.path.exists(path):
                    os.remove(path)


def clean():
    """
    interface to clean temporary and unrecorded files
    """
    _clean_unrecorded_files()
    _clean_tempory_files()


if __name__ == "__main__":
    clean()
