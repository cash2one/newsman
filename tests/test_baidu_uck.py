#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

reload(sys)
sys.setdefaultencoding('UTF-8')

from newsman.processor import baidu_uck


def _main(url):
    baidu_uck.convert(url)


if __name__ == "__main__":
    url = sys.argv[1]
    _main(url)
