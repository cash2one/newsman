#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import nltk
import re
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
def google(language='en', text='Service provided by Baidu', output_path='out.mp3'):
    """
    1. download mp3 from google tts api
    2. convert it to wav
    3. speed up the wav file, if necessary
    4. convert to mp3
    5. store in some location
    6. return the path
    """
    # generate out.mp3
    download(language, text, output_path)
    subprocess.Popen(
        'tts="%s"; lame --decode $tts - | sox -t wav - -t wav - speed 1.06 | lame - $tts' % output_path, stderr=subprocess.PIPE, shell=True)


# Todos
# could separate download to at leat two methods
def download(language='en', text='Service provided by Baidu', output='out.mp3'):
    '''
    languange = ja, en, pt, zh_CN, ar, th
    '''
    text = text.replace('\n', '')
    # simplified case only for latins
    combined_text = nltk.sent_tokenize(text)
    """
    text_list = re.split('(\,)', text)
    combined_text = []
    for idx, val in enumerate(text_list):
        if idx % 2 == 0:
            combined_text.append(val)
        else:
            joined_text = ''.join((combined_text.pop(), val))
            if len(joined_text) < 100:
                combined_text.append(joined_text)
            else:
                subparts = re.split('( )', joined_text)
                temp_string = ""
                temp_array = []
                for part in subparts:
                    temp_string = temp_string + part
                    if len(temp_string) > 80:
                        temp_array.append(temp_string)
                        temp_string = ""
                # append final part
                temp_array.append(temp_string)
                combined_text.extend(temp_array)
    """

    # Todos
    # rewrite: multi-threaded

    # download chunks and write them to the output file
    threads = []
    for idx, val in enumerate(combined_text):
        print 'transmitting ... %s' % val
        mp3url = "http://translate.google.com/translate_tts?tl=%s&q=%s&total=%s&idx=%s" % (
            language, urllib2.quote(val), len(combined_text), idx)
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
