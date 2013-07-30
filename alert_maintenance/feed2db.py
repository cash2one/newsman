#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# feed2db works to turn text-based feed list into database
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# @created Jul. 30, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')


# TODO: add docs
def _parse_task(line):
    """
    docs needed!
    """
    if line:
        task = line.split('*|*')
        return task[0], task[1], task[2], task[3]
    else:
        return None
