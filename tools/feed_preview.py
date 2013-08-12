#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
feed_preview works to get entry and feed structure
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul. 21, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import feedparser

# CONSTANTS
#FILE_SUFFIX = '/home/work/bgm_news/tools/text_based_feeds/feed_lists/'
FILE_SUFFIX = '/home/jinyuan/Downloads/bgm_news/tools/\
text_based_feeds/feed_lists/'
HTTP_CODES = {301: 'RSS address is permanently moved to a new place.',
              302: 'RSS address is temporarily moved to a new place.',
              304: 'RSS has not published new content.',
              410: 'RSS server is gone.'}


def _parse_task(line):
    """
    docs needed!
    """
    if line:
        task = line.split('*|*')
        return task[0], task[1], task[2], task[3]
    else:
        return None


def _preview(language='en', rss_file=None):
    """
    docs needed!
    """
    print '---------- retrieving feed information ----------'
    feeds_list = None
    if not rss_file:
        feeds_list = open('%s%s_feeds_list.txt' % (FILE_SUFFIX, language), 'r')
    else:
        feeds_list = open(rss_file, 'r')
    lines = feeds_list.readlines()
    feeds_list.close()

    output = open('%s%s_preview.txt' % (FILE_SUFFIX, language), 'w')
    error = open('%s%s_error.txt' % (FILE_SUFFIX, language), 'w')

    for line in lines:
        if line.strip():
            if not rss_file:
                language, category, feed_id, feed_link = _parse_task(line)
            else:
                feed_link = line.strip()
            feed = feedparser.parse(feed_link)

            if feed:
                try:
                    if feed.status == 200:
                        if 'title' in feed.feed:
                            print feed.feed.title
                            print 'Okay!'
                            output.write('::::: %s :::::\n' % feed.feed.title)
                        else:
                            print feed.feed.link
                            print 'Okay! But it has no TITLE'
                            output.write('::::: %s :::::\n' % feed.feed.link)
                        for f in feed:
                            output.write(f + '\n')
                            if 'etag' in f or 'modified' in f \
                                    or 'encoding' in f:
                                output.write("    %s\n" % feed[f])
                        output.write('-----------------\n')

                        if len(feed.entries):
                            for e in feed.entries[0]:
                                output.write(e + '\n')
                                if 'author' in e or 'tag' in e \
                                        or 'media' in e or 'thumbnail' in e \
                                        or e == 'source' or 'link' in e \
                                        or 'summary' in e or 'comment' in e \
                                        or e == 'content':
                                    output.write(
                                        '    %s\n' % feed.entries[0][e])
                        output.write('\n')
                    else:
                        print feed_link
                        print 'Problem: %i' % HTTP_CODES[feed.status]
                        error.write('%s Problem: %s\n' %
                                   (feed_link, HTTP_CODES[feed.status]))
                        error.write('\n')
                except Exception as k:
                    error.write('%s  Error: %s\n' % (feed_link, str(k)))
                    print feed_link
                    print k
                    error.write('\n')
            print
    error.close()
    output.close()


if __name__ == '__main__':
    if len(sys.argv) > 2:
        _preview(sys.argv[1], sys.argv[2])
    else:
        _preview(sys.argv[1])
