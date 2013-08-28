#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from config import logger
logger.error('error')
logger.info('info')
logger.exception('exception')
logger.critical('critical')
logger.warning('warning')
