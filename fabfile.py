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


def local():
    """
    Setup local machine
    """
    print '=== SETUP LOCAL MACHINE ==='
    env.user = 'jinyuan'
    env.hosts = ['127.0.0.1']
    env.servername = 'local'
    env.BACKUP_PATH = '/home/%s/Documents/baks' % env.user
    env.REMOTE_CODEBASE_PATH = '/home/%s/Documents/newsman' % env.user
    env.PIP_REQUIREMENTS_PATH = os.path.join(
        env.REMOTE_CODEBASE_PATH, 'requirements.pip')
    env.SERVICE_CONFIG_PATH = os.path.join(
        env.REMOTE_CODEBASE_PATH, 'newsman/config')


def AWS():
    """
    Setup common settings for all AWS servers
    """
    print '=== SET AWS SERVER CONFIGURATION ==='
    env.user = 'ubuntu'
    env.BACKUP_PATH = '/home/%s/baks' % env.user
    env.REMOTE_CODEBASE_PATH = '/home/%s/newsman' % env.user
    env.PIP_REQUIREMENTS_PATH = os.path.join(
        env.REMOTE_CODEBASE_PATH, 'requirements.pip')
    env.SERVICE_CONFIG_PATH = os.path.join(
        env.REMOTE_CODEBASE_PATH, 'newsman/config')


def tokyo():
    """
    Set up basic settings for AWS Tokyo server
    """
    AWS()
    print '=== SET TOKYO SERVER CONFIGURATION ==='
    env.hosts = ['54.248.227.71']
    env.key_filename = '/home/jinyuan/Public/AWS_identifiers/searchet.pem'
    env.servername = 'aws_tokyo'
    env.languages = ['ja', 'zh-CN', 'zh-HK']


def singapore():
    """
    Set up basic settings for AWS Singapore server
    """
    AWS()
    print '=== SET SINGAPORE SERVER CONFIGURATION ==='
    env.hosts = ['54.251.107.116']
    env.key_filename = '/home/jinyuan/Public/AWS_identifiers/mandy.pem'
    env.servername = 'aws_singapore'
    env.languages = ['en-rIN', 'ind', 'th']


def sao():
    """
    Set up basic settings for AWS Sao Paolo server
    """
    AWS()
    print '=== SET SAO PAOLO SERVER CONFIGURATION ==='
    env.hosts = ['54.232.81.44']
    env.key_filename = '/home/jinyuan/Public/AWS_identifiers/guochen.pem'
    env.servername = 'aws_sao'
    env.languages = ['en', 'pt']


# ==============================================
# Service
# ==============================================
def setup_sys_install():
    """
    Setup system libraries and binaries
    """
    print "=== SETUP SYSTEM LIBRARIES ==="
    sudo('apt-get -y update')
    sudo('apt-get -y install build-essential gcc make git-core python-dev python-imaging python-pip curl monit mongodb redis-server sox lame libjpeg8 libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev sendmail-bin sensible-mda')
    sudo('apt-get -y upgrade')
    stop_sendmail_logging()


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
    print '=== CLONE FROM GITHUB ==='
    with cd(os.path.dirname(env.REMOTE_CODEBASE_PATH)):
        run("git clone %s %s" %
            (env.GIT_REPO_URL, os.path.basename(env.REMOTE_CODEBASE_PATH)))
    configure_settings()
    setup_folders()


def configure_settings():
    """
    Modify settings file according to the server
    """
    print '=== CONFIGURE REPO SETTINGS ==='
    from fabric.contrib.files import uncomment
    uncomment(
        os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/config/settings.py'), env.host)
    uncomment(
        os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/config/settings.py'), env.user)
    run("cp %s %s" % (os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/config/settings.py'),
        os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/publisher/settings.py')))


def setup_folders():
    """
    Create folders needed by code
    """
    print '=== SETUP FOLDERS ==='
    with cd(os.path.dirname(env.REMOTE_CODEBASE_PATH)):
        run('mkdir -p STATIC/news/ts')
        run("cp -r %s %s" %
            (os.path.join(env.REMOTE_CODEBASE_PATH, 'newsman/templates/static*'), 'STATIC/news/ts'))


def stop_sendmail_logging():
    """
    Stop sendmail logging
    """
    print '=== STOP SENDMAIL LOGGING'
    from fabric.contrib.files import append, comment
    comment('/etc/rsyslog.conf', 'mail', use_sudo=True)
    append('/etc/rsyslog.conf', 'mail.none', use_sudo=True)
    sudo('/etc/init.d/rsyslog restart')


def initialize_sys_work():
    """
    Initialize system work
    """
    print '=== INITIALIZE SYSTEM WORK'
    stop_sendmail_logging()
    setup_folders()
    configure_settings()


def setup():
    """
    Install for all the prequisitions.
    """
    setup_sys_install()
    setup_repo()
    setup_pip_require()
    initialize_sys_work()


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
    sudo('cp -r %s /etc/monit/' %
         os.path.join(env.SERVICE_CONFIG_PATH, 'monit/*'))


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
    sudo('cp %s /etc/mongodb.conf' %
         os.path.join(env.SERVICE_CONFIG_PATH, 'mongodb/mongodb.conf'))


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
    sudo('cp %s /etc/redis/redis.conf' %
         os.path.join(env.SERVICE_CONFIG_PATH, 'redis/redis.conf'))


def configure_cron():
    """
    Configure crontab jobs
    """
    print '=== CONFIGURE CRON JOBS ==='


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


def deploy_cron():
    """
    Update cron job
    """
    configure_cron()
    put(os.path.join(env.REMOTE_CODEBASE_PATH,
        'newsman/config/cron/crontab'), '/tmp/crontab')
    sudo('crontab < /tmp/crontab')


def git_pull():
    """
    Git pull latest code
    """
    print '=== PULL LATEST SOURCE ==='
    with cd(env.REMOTE_CODEBASE_PATH):
        run('git pull')


def service():
    """
    Update code and restart services
    """
    deploy_redis()
    deploy_mongodb()
    deploy_monit()
    deploy_crontab()


def deploy():
    """
    Update code
    """
    git_pull()
    configure_settings()
