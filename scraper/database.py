#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')


from administration.config import Collection
from administration.config import db
import random
from image_processor import thumbnail
from data_processor import transcoder
from data_processor import tts_provider

from administration.config import LANGUAGES
from administration.config import THUMBNAIL_LOCAL_DIR
from administration.config import THUMBNAIL_SIZE
from administration.config import THUMBNAIL_WEB_DIR


def dedup(entries=None, language=None):
    """
    return entries not found in database
    """
    if not entries:
        return None
    if not language or language not in LANGUAGES:
        raise Exception("ERROR: language not found or not supported!")

    entries_new = []
    col = Collection(db, language)
    for entry in entries:
        # find duplicate in the form of the same link or title
        dup_link = col.find_one({'link': entry['link']})
        dup_title = col.find_one({'title': entry['title']})
        if not dup_link or not dup_title:
            print 'Find a duplicate for %s' % entry['title']
            continue
        else:
            entries_new.append(entry)
    return entries_new if entries_new else None 


# Todos
# break update_database into several shorter mthods
def update(entries=None, language=None):
    ''''''
    if not entries:
        return None
    # collection was created by the feed
    added_entries = []
    col = Collection(db, language)
    for entry in entries:
        duplicated = col.find_one({'link': entry['link']})
        if duplicated:
            print 'Find a duplicate for %s' % entry['title']
            continue
        item = col.find_one({'title': entry['title']})
        if not item:
            # transcode the link
            try:
                random_code = random.random()
                # create a proper name for url encoding
                safe_category = (entry['category']).strip().replace(" ", "-")
                transcoded_path, big_images = transcoder.transcode(entry['language'], entry['title'], entry[
                                                                   'link'], '%s_%s_%s_%s_%f' % (entry['language'], safe_category, entry[feed], entry['updated'], random_code))
                if not transcoded_path:
                    raise Exception('cannot transcode %s' % entry['link'])
                else:
                    entry[
                        'transcoded'] = 'None' if not transcoded_path else transcoded_path
                    entry[
                        'big_images'] = 'None' if not big_images else big_images
                    if entry['image'] == 'None' and entry['big_images'] != 'None':
                        entry['image'] = []
                        bimage_max = 0, 0
                        for bimage in entry['big_images']:
                            bimage_current = thumbnail.get_image_size(bimage)
                            if bimage_current > bimage_max:
                                thumbnail_relative_path = '%s.jpeg' % bimage
                                if len(thumbnail_relative_path) > 200:
                                    thumbnail_relative_path = thumbnail_relative_path[
                                        -200:]
                                try:
                                    thumbnail_url = thumbnail.get(
                                        bimage, thumbnail_relative_path)
                                    entry['image'] = thumbnail_url
                                    bimage_max = bimage_current
                                except IOError as e:
                                    entry['big_images'].remove(bimage)
                    elif entry['image'] and isinstance(entry['image'], list):
                        entry['image'] = entry['image'][0]
                    # Google TTS
                    # only for English, at present
                    if entry['language'] == 'en':
                        try:
                            random_code = random.randint(0, 1000000000)
                            tts_web_path = '%s%s_%s_%i.mp3' % (
                                THUMBNAIL_WEB_DIR, entry['language'], entry['updated'], random_code)
                            tts_local_path = '%s%s_%s_%i.mp3' % (
                                THUMBNAIL_LOCAL_DIR, entry['language'], entry['updated'], random_code)
                            tts_provider.google(
                                entry['language'], entry['title'], tts_local_path)
                            entry['mp3'] = tts_web_path
                        except Exception as e:
                            entry['mp3'] = "None"
                    # then save to database
                    entry_id = col.save(entry)
                    entry['_id'] = str(entry_id)
                    added_entries.append((entry, REDIS_ENTRY_EXPIRATION))
                    print 'processed %s' % entry['title']
            except Exception as e:
                print str(e)
        else:
            print 'Find a duplicate for %s' % entry['title']
    return added_entries
