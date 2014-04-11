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
#sys.path.append('/home/work')

import cgi
import json
import inquirer
from settings import logger


def get_portal(*bundle):
    """
    get hot news and other categories images and titles
    """
    language = bundle[0]['language']
    country = bundle[0]['country']
    categories = bundle[0]['categories']
    return inquirer.get_portal(language, country, categories)


def get_categories(*bundle):
    """
    get categories and their feeds and labels
    """
    return inquirer.get_categories(bundle[0]['language'], bundle[0]['country'])


def get_latest_entries(*bundle):
    """
    get the latest entries by category
    """
    LIMIT = 10 if 'limit' not in bundle[0] else int(bundle[0]['limit'])
    START_ID = None if 'start_id' not in bundle[0] else bundle[0]['start_id']
    return inquirer.get_latest_entries(bundle[0]['language'],
                                       bundle[0]['country'],
                                       bundle[0]['category'], bundle[0]['feed'],
                                       limit=LIMIT, start_id=START_ID)


def get_previous_entries(*bundle):
    """
    get the latest entries of a feed
    """
    LIMIT = 10 if 'limit' not in bundle[0] else int(bundle[0]['limit'])
    END_ID = None if 'end_id' not in bundle[0] else bundle[0]['end_id']
    return inquirer.get_previous_entries(bundle[0]['language'],
                                         bundle[0]['country'],
                                         bundle[0]['category'],
                                         bundle[0]['feed'], limit=LIMIT,
                                         end_id=END_ID)


def _read_http(environ):
    """
    read binary image file and write to local disk
    """
    bin_data = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    bundle = {}
    # note, CREATE output BY HAND and CHMOD it before executing the following
    # or you will get a "You don't have permission to ...."
    # f = open('/home/work/output', 'w')
    for key in bin_data.keys():
        bundle[key] = bin_data[key].value
    # f.write('Command\n%s\n\n' % str(bundle))
    # call corresponding method
    result = eval(bundle['function'])(bundle)
    # f.write('Result\n%s\n\n' % str(result))
    # f.close()
    if result:
        for r in result:
            if isinstance(r, dict) and r.has_key('_id'):
                r['_id'] = str(r['_id'])
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
        logger.error(str(e))
        header = [('Content-type', 'text/html'),
                  ('Content-Length', str(len(str(e))))]
        start_response("404 Not Found", header)
        return [str(e)]
