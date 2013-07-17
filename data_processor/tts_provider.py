#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import nltk
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
    def __init__(self, request=None):
        threading.Thread.__init__(self)
        self.request = request
        self.result = None

    def run(self):
        try:
            response = urllib2.urlopen(self.request)
            self.result = response.read()
        except urllib2.HTTPError as e:
            self.result = None 
            print ('HTTPError %s' % e)


# Todos
# rename the file and variables
# remove accepting command line calls
def google(language='en', query='Service provided by Baidu', output_path='out.mp3'):
    """
    1. download mp3 from google tts api
    2. convert it to wav
    3. speed up the wav file, if necessary
    4. convert to mp3
    5. store in some location
    6. return the path
    """
    # generate out.mp3
    download(language, query, output_path)
    subprocess.Popen(
        'tts="%s"; lame --decode $tts - | sox -t wav - -t wav - speed 1.06 | lame - $tts' % output_path, stderr=subprocess.PIPE, shell=True)


# Todos
# to write some boundary checkers
def query_segment(language='en', query='Service provided by Baidu'):
    '''
    remove after implementing line 91: the algorithm only now works for latins
    '''
    query = query.strip()
    sentences = nltk.sent_tokenize(query)
    parts = []
    for sentence in sentences:
        if len(sentence) < 99:
            # none of len(item) in parts will exceed 100
            parts.append(sentence)  # parts: ['xxx, xxx', 'yyy zzz aaa bbb.']
        else:
            phrases = sentence.split(',') # phrases: ['xxx -- xxx', 'yyy zzz aaa']
            for phrase in phrases:
                if len(phrase) < 99:
                    parts.append(phrase)
                else:
                    if language == 'en' | language == 'pt' | language == 'id':
                        words = phrase.split(' ')
                        # none of len(item) in combined_words will exceed 100
                        combined_words = ""  # combined_words = ['yyy zzz. aaa bbb']
                        for word in words:
                            if len(combined_words) + len(word) + 1 < 100: # +1 for possible space
                                combined_words = ("""%s %s""" if word not in string.punctuation else """%s%s""") % (combined_words, word)
                            else:
                                parts.append(combined_words)
                                combined_words = word
                        if combined_words:
                            parts.append(combined_words)
                    # -------------------------- #
                    #  \           |           / #
                    #  _  IMPLEMENT THIS PART _  #
                    #    AS SOON AS POSSIBLE!    # 
                    #  /           |           \ #
                    # -------------------------- #
                    else: # ja, th, ar
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
            segments.append(segment)
            segment = part
    segments.append(segment)
    print 'after some serious thoughts, we get these:'
    for segment in segments:
        print segment
    return segments

# Todos
# Test! Test! Test!
# docs!
def download(language='en', query='Service provided by Baidu', output='out.mp3'):
    '''
    docs needed!
    '''
    segments = query_segment(language, query)

    # download chunks and write them to the output file
    threads = []
    for idx, val in enumerate(segments):
        print 'transmitting ... %s' % val
        mp3url = "http://translate.google.com/translate_tts?tl=%s&q=%s&total=%s&idx=%s" % (
            language, urllib2.quote(val), len(segments), idx)
        headers = {"Host": "translate.google.com",
                   "Referer": "http://www.gstatic.com/translate/sound_player2.swf",
                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19"}
        req = urllib2.Request(mp3url, '', headers)
        if val > 0:
            gt_request = GoogleTranslateAPI(req)
            threads.append(gt_request)
            gt_request.start()
            gt_request.join(1*1000)
    output = open(output, 'w')
    for th in threads:
        sys.stdout.write('.')
        sys.stdout.flush()
        output.write(th.result)
    output.close()
    print 
