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
import os

# CONSTANTS
env.GIT_REPO_URL = 'https://github.com/chengdujin/ubuntu-essentials'
env.REDIS_URL = 'http://download.redis.io/releases/redis-2.6.16.tar.gz'
env.MONGODB_URL = 'http://fastdl.mongodb.org/linux/mongodb-linux-x86_64-2.4.6.tgz'


def local ():
    env.user = 'jinyuan'
    env.hosts = ['localhost']
    env.servername = 'local'


def aws():
    """
    set up basic settings for aws connectoins
    """
    env.user = 'ubuntu'
    env.hosts = ['54.251.107.116', '54.232.81.44', '54.248.227.71']
    env.key_filename = ['/home/jinyuan/Public/AWS_identifiers/mandy.pem', '/home/jinyuan/Public/AWS_identifiers/guochen.pem', '/home/jinyuan/Public/AWS_identifiers/searchet.pem']
    env.REMOTE_CODEBASE_PATH = '/home/%s/newsman' % env.user
    env.BACKUP_PATH = '/home/%s/baks' % env.user
    env.PIP_REQUIREMENTS_PATH = '%s/requirements.txt' % env.REMOTE_CODEBASE_PATH
    env.servername = ['aws_sing', 'aws_sao', 'aws_tokyo']

# ==============================================
# Setup setting
# ==============================================
def setup_repo ():
    """
    git clone from repo in github. Need to add public key to github server.
    """
    print '=== CLONE FROM GITHUB ==='
    with cd(os.path.dirname(env.REMOTE_CODEBASE_PATH)):
        run("git clone %s" % (env.GIT_REPO_URL))
        

def ll():
    print '=== LISTING ==='
    run('ls -lFh')
        

# ==============================================
# Service
# ==============================================
def setup_services(os_type):
    """
    install apache2, mongodb and redis
    """
    # create folder for temporary install files
    with cd(os.path.dirname(env.BACKUP_PATH)):
        run("mkdir %s" % os.path.basename(env.BACKUP_PATH))
    # install services
    install_apache2(os_type)
    install_mongodb(os_type)
    install_redis(os_type)


def setup_sys_install():
    """
    Setup system libraries and binaries
    """
    print "=== SETUP LIBRARIES ==="
    sudo('apt-get -y update')
    sudo('apt-get -y install build-essential gcc make git-core python-dev python-imaging python-pip curl monit mongodb sox lame libjpeg libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev')


def setup_pip_require ():
    """
    Setup pip requirements.
    """
    print('=== SETUP PIP REQUIREMENTS===')
    sudo("pip install -r %s" % env.PIP_REQUIREMENTS_PATH)


def install_redis(os_path):
    """
    download redis from the provider, compile and install it
    """
    print "=== install redis ==="
    with cd(env.BACKUP_PATH):
        if os_path == 'ubuntu':
            run('wget %s' % env.REDIS_URL)
        elif os_path == 'centos':
            pass
