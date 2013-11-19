#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
Twitter parser parses specific twitter account in real time
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Nov. 19, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')

import twitter
import urllib2

access_token_key = "24129666-M47Q6pDLZXLQy1UITxkijkTdKfkvTcBpleidNPjac"
access_token_secret = "0zHhqV5gmrmsnjiOEOBCvqxORwsjVC5ax4mM3dCDZ7RLk"
consumer_key = "hySdhZgpj5gF12kRWMoVpQ"
consumer_secret = "2AkrRg89SdJL0qHkHwuP933fiBaNTioChMpxRdoicUQ"

api = twitter.Api(consumer_key, consumer_secret, access_token_key, access_token_secret)

def parse():
    """
    """
    pass


if __name__ == "__main__":
    pass
