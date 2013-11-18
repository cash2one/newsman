#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from config import Collection
from config import db
from utility import summarizer


def main():
    col = Collection(db, 'en')
    items = col.find({}, {'summary': 1, 'transcoded': 1})
    if items:
        for item in items:
            summary = summarizer.extract(item['summary'], None, 'en')
            print item['_id'], len(summary)
            print summary
            print


if __name__ == '__main__':
    main()
