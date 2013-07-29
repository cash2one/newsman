#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#
#@author Yuan JIN
#@contact jinyuan@baidu.com
#@created Jan 2, 2013
#
#@updated Jan 17, 2013
#
# TODO
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('.')

import cgi
from news import interface
import json


def get_categories_by_language(*bundle):
    ''''''
    return interface.get_categories_by_language(bundle[0]['language'])

def get_latest_entries_by_language(*bundle):
    ''''''
    LIMIT = 10 if 'limit' not in bundle[0] else bundle[0]['limit']
    START_ID = None if 'start_id' not in bundle[0] else bundle[0]['start_id']
    STRATEGY = 1 if 'strategy' not in bundle[0] else bundle[0]['strategy']
    return interface.get_latest_entries_by_language(bundle[0]['language'], limit=LIMIT, start_id=START_ID, strategy=STRATEGY)

def get_previous_entries_by_language(*bundle):
    '''get the latest entries of a feed'''
    LIMIT = 10 if 'limit' not in bundle[0] else bundle[0]['limit']
    END_ID = None if 'end_id' not in bundle[0] else bundle[0]['end_id']
    STRATEGY = 1 if 'strategy' not in bundle[0] else bundle[0]['strategy']
    return interface.get_previous_entries_by_language(bundle[0]['language'], limit=LIMIT, end_id=END_ID, strategy=STRATEGY)

def get_latest_entries_by_category(*bundle):
    ''''''
    LIMIT = 10 if 'limit' not in bundle[0] else bundle[0]['limit']
    START_ID = None if 'start_id' not in bundle[0] else bundle[0]['start_id']
    STRATEGY = 1 if 'strategy' not in bundle[0] else bundle[0]['strategy']
    return interface.get_latest_entries_by_category(bundle[0]['language'], bundle[0]['category'], limit=LIMIT, start_id=START_ID, strategy=STRATEGY)

def get_previous_entries_by_category(*bundle):
    '''get the latest entries of a feed'''
    LIMIT = 10 if 'limit' not in bundle[0] else bundle[0]['limit']
    END_ID = None if 'end_id' not in bundle[0] else bundle[0]['end_id']
    STRATEGY = 1 if 'strategy' not in bundle[0] else bundle[0]['strategy']
    return interface.get_previous_entries_by_category(bundle[0]['language'], bundle[0]['category'], limit=LIMIT, end_id=END_ID, strategy=STRATEGY)

def read_http(environ):
    'read binary image file and write to local disk'
    bin_data = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    bundle = {}
    for key in bin_data.keys():
        bundle[key] = bin_data[key].value
    # call corresponding method
    result = eval(bundle['function'])(bundle)
    if result:
        return json.dumps(result)
    else:
        return 'null'

def application(environ, start_response):
    try:
        output = read_http(environ)
        if output is None:
            raise Exception('Void output!')
        header = [('Content-type', 'text/html'), ('Content-Length', str(len(output)))]
        start_response("200 OK", header)
        return [output]
    except Exception, e:
        header = [('Content-type', 'text/html'), ('Content-Length', str(len(str(e))))]
        start_response("404 Not Found", header)
        return [str(e)]
