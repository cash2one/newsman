#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
news.py is the wsgi interface to connect the request and the backend
"""
#@author chengdujin
#@contact chengdujin@gmail.com
#@created Jan 2, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('/var/www/wsgi')

import cgi
from config import logging
import json
import inquirer


def get_categories_by_language(*bundle):
    """
    get hot news and other categories images and titles
    """
    return inquirer.get_categories_by_language(bundle[0]['language'])


def get_latest_entries_by_language(*bundle):
    """
    get the latest entries by language
    """
    LIMIT = 10 if 'limit' not in bundle[0] else int(bundle[0]['limit'])
    START_ID = None if 'start_id' not in bundle[0] else bundle[0]['start_id']
    return inquirer.get_latest_entries_by_language(bundle[0]['language'], limit=LIMIT, start_id=START_ID)


def get_previous_entries_by_language(*bundle):
    """
    get the latest entries of a feed
    """
    LIMIT = 10 if 'limit' not in bundle[0] else int(bundle[0]['limit'])
    END_ID = None if 'end_id' not in bundle[0] else bundle[0]['end_id']
    return inquirer.get_previous_entries_by_language(bundle[0]['language'], limit=LIMIT, end_id=END_ID)


def get_latest_entries_by_category(*bundle):
    """
    get the latest entries by category
    """
    LIMIT = 10 if 'limit' not in bundle[0] else int(bundle[0]['limit'])
    START_ID = None if 'start_id' not in bundle[0] else bundle[0]['start_id']
    return inquirer.get_latest_entries_by_category(bundle[0]['language'], bundle[0]['category'], limit=LIMIT, start_id=START_ID)


def get_previous_entries_by_category(*bundle):
    """
    get the latest entries of a feed
    """
    LIMIT = 10 if 'limit' not in bundle[0] else int(bundle[0]['limit'])
    END_ID = None if 'end_id' not in bundle[0] else bundle[0]['end_id']
    return inquirer.get_previous_entries_by_category(bundle[0]['language'], bundle[0]['category'], limit=LIMIT, end_id=END_ID)


def _read_http(environ):
    """
    read binary image file and write to local disk
    """
    bin_data = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    bundle = {}
    # note, CREATE output BY HAND and CHMOD it before executing the following
    # or you will get a "You don't have permission to ...."
    # f = open('/var/www/wsgi/output', 'w')
    for key in bin_data.keys():
        bundle[key] = bin_data[key].value
    # f.write('Command\n%s\n\n' % str(bundle))
    # call corresponding method
    result = eval(bundle['function'])(bundle)
    # f.write('Result\n%s\n\n' % str(result))
    # f.close()
    if result:
        result_json = json.dumps(result, encoding="utf-8")
        return result_json.replace('": null', '": None')  # which is stupid
    else:
        return 'null'


def application(environ, start_response):
    """
    WSGI interface
    """
    try:
        output = _read_http(environ)
        if output is None:
            raise Exception('Void output!')
        header = [('Content-type', 'text/html'),
                  ('Content-Length', str(len(output)))]
        start_response("200 OK", header)
        return [output]
    except Exception, e:
        logging.error(str(e))
        header = [('Content-type', 'text/html'),
                  ('Content-Length', str(len(str(e))))]
        start_response("404 Not Found", header)
        return [str(e)]
