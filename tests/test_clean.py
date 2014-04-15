#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

# remove collection
from newsman.config.settings import db

collections = db.collection_names()
for collection in collections:
    if collection != 'system.indexes' and collection != 'feeds':
        db.drop_collection(collection)
print 'Database cleaned!'

# clean memory
from newsman.config.settings import rclient

rclient.flushall()
print 'Memory cleaned!'

# clean physical files
import os
from newsman.config.settings import IMAGES_LOCAL_DIR
from newsman.config.settings import MEDIA_LOCAL_DIR
from newsman.config.settings import TRANSCODED_LOCAL_DIR


def _remove_dir(dir):
    if os.path.exists(dir):
        try:
            files = os.listdir(dir)
            for file in files:
                if file == '.' or file == '..':
                    continue
                path = '%s%s' % (dir, file)
                if not os.path.isdir(path):
                    os.remove(path)
            os.removedirs(dir)
            print '%s removed!' % dir
        except OSError as k:
            print k
    else:
        print '%s does not exist!' % dir


_remove_dir(TRANSCODED_LOCAL_DIR)
_remove_dir(IMAGES_LOCAL_DIR)
_remove_dir(MEDIA_LOCAL_DIR)
