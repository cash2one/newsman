#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# feed_preview works to get entry and feed structure
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jul. 21, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')

import feedparser

file_suffix = '/home/jinyuan/Downloads/global-mobile-news/alert_maintenance/maintenance/'


def extract_task(line):
    """
    docs needed!
    """
    if line:
        task = line.split('*|*')
        return task[0], task[1], task[2], task[3]
    else:
        return 1

def preview(language='en'):
    """
    docs needed!
    """
    print '---------- retrieving feed information ----------'
    feeds_list = open('%s%s_feeds_list.txt' % (file_suffix, language), 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    output = open('%s%s_preview.txt' % (file_suffix, language), 'w')
    for line in lines:
        language, category, feed_id, feed_link = extract_task(line)
        print feed_id
        output.write('::::: %s :::::\n' % feed_id)
        feed = feedparser.parse(feed_link)

        if feed:
            for f in feed:
                output.write(f + '\n')            
                if 'etag' in f or 'modified' in f or 'encoding' in f:
                    output.write("    %s\n" % feed[f])
            output.write('-----------------\n')

            if len(feed.entries):
                for e in feed.entries[0]:
                    output.write(e + '\n')
                    if 'author' in e or 'tag' in e or 'media' in e or 'thumbnail' in e or e == 'source' or 'link' in e:
                        output.write('    %s\n' % feed.entries[0][e])
        output.write('\n')
    output.close()

if __name__ == '__main__':
    language = sys.argv[1]
    preview(language)
