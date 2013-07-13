#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#@created Mar 18, 2013
#
#
# TODO
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import os

def clean_mem():
    '''Free memory used by python'''
    pids = ''
    for line in os.popen('ps -A | grep python').readlines():
        if line.find('?') != -1:
            pid = line[0:line.find('?')]
            print 'pid: %s' % pid
            pids += pid
    if pids != '':
        print 'pids: %s' % pids
        os.system('kill ' + pids)

if __name__ == "__main__":
    clean_mem()
    sys.exit(0)
