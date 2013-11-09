#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
thumbnail used to make thumbnails
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul., 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from config.settings import logger
from cStringIO import StringIO
import Image
import urllib2

# CONSTANTS
from config.settings import MIN_IMAGE_SIZE
from config.settings import UCK_TIMEOUT




