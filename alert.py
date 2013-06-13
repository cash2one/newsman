#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#@created Mar 5, 2013
#
#
# TODO
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import socket
import re
import smtplib
import os

def mail(address):
    sendmail_location = '/usr/sbin/sendmail'
    p = os.popen('%s -t' % sendmail_location, 'w')
    p.write('Subject: Tokyo server %s is down\n' % address)
    p.write('\n')
    p.write('Apache or redis has crashed due to low memory, script has restarted it, check it')
    status = p.close()
    if status != 0:
        print 'Sendmail exit status', status

def check_server(address, port):
    #s = socket.socket()
    #print 'ready to connect %s at port: %s' % (address, port)
    #try:
    #    s.connect((address, port))
    #    print 'connecting to %s at port: %s' % (address, port)
    #    return 'success'
    #except socket.error,e:
    #    print 'connect %s at port: %s failed:  %s' % (address, port, e)
    #    print 'apache or redis will restart at once'
    #    os.system('sudo service apache2 restart')
    #    os.system('sudo service redis-server restart')
    #    mail(address)
    #    return 'failure'
    out_apache = os.popen('sudo service apache2 status').read().lower()
    out_redis = os.popen('sudo service redis-server status').read().lower()
    if out_apache.find('not') != -1 or out_redis.find('not') != -1:
        print 'Server has crashed down, restart server'
        os.system('sudo service apache2 restart')
        os.system('sudo service redis-server restart')
        mail(address)
        return 'failure'
    else:
        return 'success'

if __name__== '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-a', '--address', dest='address', default='localhost', help='ADDRESS for web-server', metavar='ADDRESS')
    parser.add_option('-p', '--port', type='int', default=80, help='PORT for web-server', metavar='PORT')

    (options, args) = parser.parse_args()
    print 'option: %s, args: %s' % (options, args)
    check = check_server(options.address, options.port)
    print 'return: %s' % check
    sys.exit(not check)
