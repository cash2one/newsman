#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import nltk
import os
import random
import re
import string
import subprocess
import time
import threading
import urllib2


class GoogleTranslateAPI(threading.Thread):
    """
    doc to be made
    """
    def __init__(self, language='en', text='Service provided by Baidu'):
        threading.Thread.__init__(self)
        self.language = language
        self.text = text
        self.result = None

    def run(self):
        response = subprocess.Popen(
            '''curl -A Mozilla "http://translate.google.com/translate_tts?tl=%s&q=%s"''' %
            (self.language, urllib2.quote(self.text)), stdout=subprocess.PIPE, shell=True)
        content, error = response.communicate()
        if not error and content:
            if 'error' not in content or 'permission' not in content:
                self.result = content
            else:
                raise Exception
        else:
            raise Exception


# Todos
# rename the file and variables
# remove accepting command line calls
def google(language='en', query='Service provided by Baidu', output_path='do_not_exist.mp3'):
    """
    1. download mp3 from google tts api
    2. convert it to wav
    3. speed up the wav file, if necessary
    4. convert to mp3
    5. store in some location
    6. return the path
    """
    # generate out.mp3
    tmp_file = _download(language, query, '%s-tmp.mp3' % output_path[:-4])
    subprocess.Popen(
        'lame -S --decode {0} - | sox -q -t wav - -t wav - speed 1.06 | lame -S - {1}; rm {0}'.format(tmp_file, output_path), stderr=subprocess.PIPE, shell=True)
    print '----------- MISSION ACCOMPLISHED ----------'


# Todos
# to write some boundary checkers
def _query_segment(language='en', query='Service provided by Baidu'):
    '''
    remove after implementing line 91: the algorithm only now works for latins
    '''
    query = query.strip()
    sentences = nltk.sent_tokenize(query)
    parts = []
    for sentence in sentences:
        if len(sentence) < 99:
            # none of len(item) in parts will exceed 100
            parts.append(sentence.strip())  # parts: ['xxx, xxx', 'yyy zzz aaa bbb.']
        else:
            # phrases: ['xxx -- xxx', 'yyy zzz aaa']
            phrases = sentence.split(',')
            for phrase in phrases:
                if len(phrase) < 99:
                    parts.append(phrase.strip())
                else:
                    if language == 'en' | language == 'pt' | language == 'id':
                        words = phrase.split(' ')
                        # none of len(item) in combined_words will exceed 100
                        # combined_words = ['yyy zzz. aaa bbb']
                        combined_words = ""
                        for word in words:
                            # +1 for possible space
                            if len(combined_words) + len(word) + 1 < 100:
                                combined_words = ("""%s %s""" if word not in string.punctuation else """%s%s""") % (
                                    combined_words, word)
                            else:
                                parts.append(combined_words.strip())
                                combined_words = word
                        if combined_words:
                            parts.append(combined_words.strip())
                    # -------------------------- #
                    # \           |           /  #
                    # _  IMPLEMENT THIS PART _   #
                    # AS SOON AS POSSIBLE!    #
                    # /           |           \  #
                    # -------------------------- #
                    else:  # ja, th, ar
                        # Todos
                        # determine how do these languages separate words
                        pass
    segments = []
    # a higher-level version of 'combined_words' algorithm
    segment = ""
    for part in parts:
        if len(segment) + len(part) + 1 < 100:
            segment = """%s %s""" % (segment, part)
        else:
            segments.append(segment.strip())
            segment = part
    segments.append(segment.strip())
    print '---------- after some serious thoughts, we get these: -----------'
    for segment in segments:
        print segment
    return segments
    print '----------                     :                      -----------'


# Todos
# Test! Test! Test!
# boundary checkers
# docs!
def _download(language='en', query='Service provided by Baidu', tmp_file='do_not_exist.mp3'):
    '''
    docs needed!
    other ways to write _download
    1. https://github.com/hungtruong/Google-Translate-TTS/blob/master/GoogleTTS.py
    2. https://github.com/gavinmh/tts-api/blob/master/text_segmenter.py
    '''
    segments = _query_segment(language, query)

    # download chunks and write them to the output file
    try:
        threads = []
        for segment in segments:
            if segment:
                print 'transmitting ... %s' % segment
                gt_request = GoogleTranslateAPI(language, segment)
                threads.append(gt_request)
                gt_request.start()
                gt_request.join(2 * 1000)
        out = open(tmp_file, 'a')
        for th in threads:
            sys.stdout.write('.')
            sys.stdout.flush()
            if th.result:
                out.write(th.result)
            else:
                raise Exception
        out.close()
        return tmp_file
    except Exception as e:
        print '!Exception: removing file ...'
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        return None
