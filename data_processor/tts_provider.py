#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import nltk
import re
import subprocess
import time
import urllib2


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
        'tts="%s"; lame --decode $tts - | sox -t wav - -t wav - speed 1.1 | lame - $tts' % output_path, stderr=subprocess.PIPE, shell=True)


def download(language='en', text='Service provided by Baidu', output='out.mp3'):
    '''
    languange = ja, en, pt, zh_CN, ar, th
    '''
    text = text.replace('\n', '')
    sents = nltk.sent_tokenize(text)
    text_list = re.split('(\,|\.)', text)
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

    # Todos
    # rewrite: multi-threaded

    # download chunks and write them to the output file
    if isinstance(output, str):
        output = open(output, 'w')
    for idx, val in enumerate(combined_text):
        print 'transmitting ... %s' % val
        mp3url = "http://translate.google.com/translate_tts?tl=%s&q=%s&total=%s&idx=%s" % (
            language, urllib2.quote(val), len(combined_text), idx)
        headers = {"Host": "translate.google.com",
                   "Referer": "http://www.gstatic.com/translate/sound_player2.swf",
                   "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19"}
        req = urllib2.Request(mp3url, '', headers)
        sys.stdout.write('.')
        sys.stdout.flush()
        if len(val) > 0:
            try:
                response = urllib2.urlopen(req)
                output.write(response.read())
                time.sleep(.5)
            except urllib2.HTTPError as e:
                print ('%s' % e)
    output.close()
    print 
