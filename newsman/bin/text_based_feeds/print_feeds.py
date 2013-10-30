#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('../..')

from config.settings import Collection, db
import feedparser
FILE_PREFIX = '/home/work/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/ubuntu/newsman/newsman/bin/text_based_feeds/feed_lists/'
#FILE_PREFIX = '/home/jinyuan/Downloads/newsman/newsman/bin/text_based_feeds/feed_lists/'


def _parse_task(line):
    """
    read *_feeds_list.txt
    """
    line = line.strip()
    if line:
        task = line.strip().split('*|*')
        # task[1] refers to categories
        return task[0].strip(), task[1].strip(), task[2].strip(), task[3].strip()
    else:
        return None

def _find(language, country):
    """
    """
    feeds_list = open('%s%s_%s_feeds_list' % (FILE_PREFIX, language, country), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()
    
    feed_titles = open('%s%s_%s_feed_titles' % (FILE_PREFIX, language, country), 'w')
    for line in lines:
        language, category, transcoder, link = _parse_task(line)
        ss = feedparser.parse(link)
        feed_title = ss['feed']['title'] if ss and 'title' in ss['feed'] else None
        print "[%s]" % str(feed_title), link
        feed_titles.write("%s*|*%s\n" % (link, str(feed_title)))
    feed_titles.close()

    """
    col = Collection(db, 'feeds')

    output = {}
    items = col.find()
    for item in items:
        for country in item['countries']:
            country = str(country)
            if country not in output:
                output[country] = []
            ss = feedparser.parse(item['feed_link'])
            print item['feed_link']
            feed_title = ss['feed']['title'] if ss and 'title' in ss['feed'] else item['feed_link']
            print str(feed_title)
            output[country].append('%s  %s' % (item['categories'][0], str(feed_title)))
            print

    f = open('test', 'w')
    for k, v in output.iteritems():
        f.write(k + '\n')
        for i in v:
            f.write("    " + i + '\n')
        f.write('\n')
    f.close()
    """

if __name__ == "__main__":
    if len(sys.argv) > 1:
        _find(sys.argv[1], sys.argv[2])
    else:
        print 'Please indicate a language and country'
