#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

from newsman.processor import transcoder


def _main(language, url, trans):
    print transcoder.convert(language, '123 tests', url, 1385035380, 'Engadget',
                             trans, 'tests')


if __name__ == "__main__":
    url = sys.argv[1]

    trans = "chengdujin"
    if len(sys.argv) > 2:
        trans = sys.argv[2]
    language = 'en'
    if len(sys.argv) > 3:
        language = sys.argv[3]
    _main(language, url, trans)
