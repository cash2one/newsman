#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
the script checks the connectivity and other things of a server
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Sept. 01, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')

import time
import urllib2


def _check(url):
    """
    implement server checker
    """
    log = '/home/ubuntu/newsman/server_checker_log'
    now = time.asctime(time.gmtime())
    f = open(log, 'a')
    TIMEOUT = 10
    try:
        response = urllib2.urlopen(url)
        code = response.getcode()
        print now, code
        if code != 200:
            f.write("W %s %i\n" % (str(now), code))
            f.close()
    except Exception as k:
        f.write("E %s %s\n" % (str(now), str(k)))
        f.close()


if __name__ == '__main__':
    url = sys.argv[1]
    _check(url)

