#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
Fabric config file
Based on https://github.com/fengli/fabfile-deploy/blob/master/fabfile.py
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 21, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')

from fabric.api import *

# CONSTANTS
env.GIT_REPO_URL = 'https://github.com/chengdujin/bgm_news'


def local ():
    env.user = 'jinyuan'
    env.hosts = ['localhost']
    env.servername = 'local'


def staging():
    env.user = 'ubuntu'
    env.hosts = ['54.251.107.116', '54.232.81.44', '54.248.227.71']
    env.key_filename = ['/home/jinyuan/Public/AWS_identifiers/mandy.pem', '/home/jinyuan/Public/AWS_identifiers/guochen.pem', '/home/jinyuan/Public/AWS_identifiers/searchet.pem']
    env.REMOTE_CODEBASE_PATH = '/home/%s/bgm_news' % env.user
    env.PIP_REQUIREMENTS_PATH = '%s/requirements.txt' % env.REMOTE_CODEBASE_PATH
    env.servername = ['aws_sing', 'aws_sao', 'aws_tokyo']

def host_type():
    run('uname -s')

def ll():
    run('ls -lhF')
