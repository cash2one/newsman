#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
fabric config file
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 21, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')

from fabric.api import *

env.user = 'ubuntu'
env.hosts = ['54.251.107.116']
env.key_filename = ['/home/jinyuan/Public/AWS_identifiers/mandy.pem']

def host_type():
    run('uname -s')

def ll():
    run('ls')
