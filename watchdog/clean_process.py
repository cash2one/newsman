#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
clean zombie processes
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 22, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')

import subprocess


def clean():
    """
    kill zombie processes if there is any
    """
    command = "kill -HUP `ps -A -ostat,ppid | grep -e '^[Zz]' | awk '{print $2}'`"
    subprocess.Popen(command, stderr=subprocess.PIPE, shell=True)


if __name__ == '__main__':
    clean()

