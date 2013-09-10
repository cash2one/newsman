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
env.GIT_REPO_URL = 'https://github.com/chengdujin/newsman'
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
    #env.hosts = ['54.251.107.116', '54.232.81.44', '54.248.227.71']
    env.hosts = ['54.248.227.71']
    #env.key_filename = ['/home/jinyuan/Public/AWS_identifiers/mandy.pem', '/home/jinyuan/Public/AWS_identifiers/guochen.pem', '/home/jinyuan/Public/AWS_identifiers/searchet.pem']
    env.key_filename = '/home/jinyuan/Public/AWS_identifiers/searchet.pem'
    env.BACKUP_PATH = '/home/%s/baks' % env.user
    env.REMOTE_CODEBASE_PATH = '/home/%s/newsman' % env.user
    env.PIP_REQUIREMENTS_PATH = '%s/requirements.txt' % env.REMOTE_CODEBASE_PATH
    #env.servername = ['aws_sing', 'aws_sao', 'aws_tokyo']
    env.servername = 'aws_tokyo'


# ==============================================
# Service
# ==============================================
def setup_sys_install():
    """
    Setup system libraries and binaries
    """
    print "=== SETUP LIBRARIES ==="
    sudo('apt-get -y install build-essential gcc make git-core python-dev python-imaging python-pip curl monit mongodb redis-server sox lame libjpeg8 libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev')


def setup_pip_require():
    """
    Setup pip requirements.
    """
    print('=== SETUP PIP REQUIREMENTS===')
    sudo("pip install -r %s" % env.PIP_REQUIREMENTS_PATH)


def setup_repo():
    """
    git clone from repo in github. Need to add public key to github server.
    """
    print('=== CLONE FROM GITHUB ===')
    with cd(os.path.dirname(env.REMOTE_CODEBASE_PATH)):
        run("git clone %s %s" % (env.GIT_REPO_URL, os.path.basename(env.REMOTE_CODEBASE_PATH)))

    from fabric.contrib.files import uncomment
    uncomment(os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/config.py'), env.host)
    uncomment(os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/config.py'), env.user)
    run("cp %s %s" % (os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/config.py'), os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/publisher/config.py')))

    with cd(os.path.dirname(env.REMOTE_CODEBASE_PATH)):
        run('mkdir -p STATIC/news/ts')
        run("cp -r %s %s" % (os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/templates/static*'), 'STATIC/news/ts'))


def setup():
    """
    Install for all the prequisitions.
    """
    setup_sys_install()
    setup_pip_require()
    setup_repo()


def restart_monit():
    """
    Restart Monit
    """
    print '=== RESTART MONIT ==='
    sudo('/etc/init.d/monit restart')


def stop_monit():
    """
    Stop Monit
    """
    print '=== STOP MONIT ==='
    sudo('/etc/init.d/monit stop')


def start_monit():
    """
    Start Monit
    """
    print '=== START MONIT ==='
    sudo('/etc/init.d/monit start')


def configure_monit():
    """
    Copy monit.conf to /etc/monit
    """
    print '=== CONFIGURE MONIT ==='
    sudo('cp %s /etc/monit/monit.conf' % os.path.join(env.GIT_REPO_URL, 'newsman/configs/monit.conf'))


def restart_mongodb():
    """
    Restart MongoDB server
    """
    print '=== RESTART MONGODB ==='
    sudo('/etc/init.d/mongod restart')


def stop_mongodb():
    """
    Stop MongoDB server
    """
    print '=== STOP MONGODB ==='
    sudo('/etc/init.d/mongod stop')


def start_mongodb():
    """
    Start MongoDB server
    """
    print '=== START MONGODB ==='
    sudo('/etc/init.d/mongod start')


def configure_mongodb():
    """
    Copy mongodb.conf to /etc/mongodb
    """
    print '=== CONFIGURE MONGODB ==='
    sudo('cp %s /etc/mongodb/mongodb.conf' % os.path.join(env.GIT_REPO_URL, 'newsman/configs/mongodb.conf'))


def restart_redis():
    """
    Restart redis server
    """
    print '=== RESTART REDIS ==='
    sudo('/etc/init.d/redis-server restart')


def stop_redis():
    """
    Stop redis server
    """
    print '=== STOP REDIS ==='
    sudo('/etc/init.d/redis-server stop')


def start_redis():
    """
    Start redis server
    """
    print '=== START REDIS ==='
    sudo('/etc/init.d/redis-server start')


def configure_redis():
    """
    Copy redis.conf to /etc/redis
    """
    print '=== CONFIGURE REDIS ==='
    sudo('cp %s /etc/redis/redis.conf' % os.path.join(env.GIT_REPO_URL, 'newsman/configs/redis.conf'))


def deploy_monit():
    """
    Update config file and restart monit
    """
    configure_monit()
    restart_monit()


def deploy_mongodb():
    """
    Update config file and restart mongodb
    """
    configure_mongodb()
    restart_mongodb()


def deploy_redis():
    """
    Update config file and restart redis
    """
    configure_redis()
    restart_redis()


def git_pull():
    """
    Git pull latest code
    """
    print '=== PULL LATEST SOURCE ==='
    with cd(env.REMOTE_CODEBASE_PATH):
        run('git pull')


def deploy_full():
    """
    Update code and restart services
    """
    git_pull()
    deploy_redis()
    deploy_mongodb()
    deploy_monit()


def deploy():
    """
    Update code
    """
    git_pull()
