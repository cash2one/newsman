#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

from newsman.processor import simplr, summarizer


def main():
    language = 'th'
    title = '10 สุดยอดแก็ดเจ็ตเจ๋ง ๆ แห่งปี 2013 จากนิตยสาร Time'
    title_new, content, images = simplr.convert(
        'http://men.kapook.com/view78131.html', language)
    summarized = summarizer.extract(language=language, title=title,
                                    content=content, summary=None, link=None,
                                    feed=None, category=None)
    print str(summarized)


if __name__ == '__main__':
    main()
