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

def preview(language='en', rss_file=None):
    """
    docs needed!
    """
    print '---------- retrieving feed information ----------'
    if not rss_file:
        feeds_list = open('%s%s_feeds_list.txt' % (file_suffix, language), 'r')
    else:
        feed_list = open(rss_file, 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    output = open('%s%s_preview.txt' % (file_suffix, language), 'w')
    error = open('%s%s_error.txt' % (file_suffix, language), 'w')

    for line in lines:
        if line.strip():
            if not rss_file:
                language, category, feed_id, feed_link = extract_task(line)
            else:
                feed_id = line
            feed = feedparser.parse(feed_link)

            if feed:
                if feed.status == 200:
                    output.write('::::: %s :::::\n' % feed_id)
                    print feed.title
                    print 'okay!'
                    for f in feed:
                        output.write(f + '\n')            
                        if 'etag' in f or 'modified' in f or 'encoding' in f:
                            output.write("    %s\n" % feed[f])
                    output.write('-----------------\n')

                    if len(feed.entries):
                        for e in feed.entries[0]:
                            output.write(e + '\n')
                            if 'author' in e or 'tag' in e or 'media' in e or 'thumbnail' in e or e == 'source' or 'link' in e or 'summary' in e or 'comment' in e or e == 'content':
                                output.write('    %s\n' % feed.entries[0][e])
                else:
                    error.write('%s\n' % feed_id)
                    print feed_id
                    print 'problem: %i' % feed.status
        error.write('\n')
        output.write('\n')
    error.close()
    output.close()

if __name__ == '__main__':
    language = sys.argv[1]
    if len(sys.argv) > 2:
        rss_file = sys.argv[2]
        preview(language, rss_file)
    else:
        preview(language)
