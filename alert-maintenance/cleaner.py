#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#@created Mar 15, 2013
#
#
# TODO
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

from config import Collection
from config import db
from config import TRANSCODED_LOCAL_DIR
from config import TRANSCODED_WEB_DIR
import os

def clean_transcoded():
    '''clean up useless transcoded page'''
    col = Collection(db, 'ja')
    # return a cursor
    entries = col.find()
    print 'entries size: %d' % entries.count()
    files = os.listdir(TRANSCODED_LOCAL_DIR)
    print 'transcoded files: %d' % len(files)
    useless = []
    for transcoded in files:
        if os.path.isfile(TRANSCODED_LOCAL_DIR+transcoded):
            #count = 0
            #for entry in entries:
            #    if entry['transcoded'].find(transcoded) >= 0:
            #        print 'useful'
            #        print 'web url: %s, local file: %s' % (entry['transcoded'], transcoded)
            #        break
            #    else:
            #        print 'web url: %s, local file: %s' % (entry['transcoded'], transcoded)
            #        count += 1
            #if count == entries.count():
            #    useless.append(TRANSCODED_LOCAL_DIR+transcoded)
            item = col.find_one({'transcoded':TRANSCODED_WEB_DIR+transcoded})
            if not item:
                useless.append(TRANSCODED_LOCAL_DIR+transcoded)
        else:
            print 'is not file'
    print 'useless files: %d' % len(useless)
