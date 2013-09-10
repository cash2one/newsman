#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
tts_provider breaks text into paragraphs and grabs text-to-speech from google
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul., 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('../config')

import nltk
import os
from settings import logger
import re
import string
import subprocess
import tinysegmenter
import threading
import urllib2

# CONSTANTS
from settings import GOOGLE_TTS_TIMEOUT
from settings import MEDIA_LOCAL_DIR
from settings import MEDIA_PUBLIC_DIR
from settings import MEDIA_TEMP_LOCAL_DIR
from settings import LANGUAGES


if not os.path.exists(MEDIA_LOCAL_DIR):
    os.mkdir(MEDIA_LOCAL_DIR)

if not os.path.exists(MEDIA_TEMP_LOCAL_DIR):
    os.mkdir(MEDIA_TEMP_LOCAL_DIR)


# TODO: write docs
class GoogleTranslateAPI(threading.Thread):

    """
    doc needed!
    """

    def __init__(self, language='en', text='Service provided by Baidu'):
        threading.Thread.__init__(self)
        self.language = language
        self.text = text
        self.result = None

    def run(self):
        response = subprocess.Popen(
            '''curl --silent --connect-timeout %s -A Mozilla "http://translate.google.com/translate_tts?ie=UTF-8&oe=UTF-8&tl=%s&q=%s"''' %
            (GOOGLE_TTS_TIMEOUT, self.language, urllib2.quote(self.text)), stdout=subprocess.PIPE, shell=True)

        content, error = response.communicate()
        if not error and content:
            if 'error' not in content or 'permission' not in content:
                self.result = content
            else:
                logger.error('Errors or Permission found in HTTP response')
                self.result = None
        else:
            if error:
                logger.error('Error %s found for %s' % (str(error), self.text))
                self.result = None
            else:
                logger.error('No content returned for %s' % self.text)
                self.result = None


# TODO: rename the file and variables
# TODO: remove accepting command line calls
def google(language='en', query='Service provided by Baidu', relative_path='do_not_exist.mp3'):
    """
    1. download mp3 from google tts api
    2. convert it to wav
    3. speed up the wav file, if necessary
    4. convert to mp3
    5. store in some location
    6. return the path
    """
    if not language or not query or not relative_path:
        logger.error('Method malformed!')
        return None, None
    if language not in LANGUAGES:
        logger.error('%s not supported!' % language)
        return None, None

    try:
        # generate out.mp3
        tmp_file = _download(language, query, '%s%s-tmp.mp3' %
                             (MEDIA_TEMP_LOCAL_DIR, relative_path[:-4]))
        if tmp_file:
            # form paths
            tts_local_path = '%s%s' % (MEDIA_LOCAL_DIR, relative_path)
            tts_web_path = '%s%s' % (MEDIA_PUBLIC_DIR, relative_path)

            command = 'lame -S --decode {0} - | sox -q -t wav - -t wav - speed 1.06 | lame -S - {1}; rm {0}'.format(
                tmp_file, tts_local_path)
            subprocess.Popen(command, stderr=subprocess.PIPE, shell=True)
            logger.info('... MP3 acceleration is successfully completed!')
            return tts_web_path, tts_local_path
        else:
            logger.info(
                '%s is revoked due to erros found in downloading!' % relative_path)
            return None, None
    except Exception as k:
        logger.error(str(k))
        return None, None


# TODO: write some boundary checkers
# TODO: determine how do these languages separate words
# TODO: get encoding of a feed. use that if indicated, else 'utf-8'
def _query_segment(language='en', query='Service provided by Baidu'):
    """
    remove after implementing line 91: the algorithm only now works for latins
    """

    def _remove_brackets(text):
        """
        remove brackets, latin or japanese from a sentence
        """
        no_bracket_parts = re.split(u"[\（\(].+?[\）\)]", text)
        return ''.join(no_bracket_parts)

    try:
        # pre-process
        query = unicode(query.strip())
        # remove content within a () or （）
        query = _remove_brackets(query)
        # remove \n
        query = query.replace('\n', ' ')

        sentences = None
        if language == 'ja':
            #jp_sent_tokenizer = nltk.RegexpTokenizer(u'^ !?.！？。．]*[!?.！？。]*')
            jp_sent_tokenizer = nltk.RegexpTokenizer(u'[^!?.！？。．]*[!?.！？。]*')
            sentences = jp_sent_tokenizer.tokenize(query)
        else:
            sentences = nltk.sent_tokenize(query)

        if sentences:
            # convert to utf-8 and remove spaces
            sentences = filter(
                lambda x: x, [sentence.strip().encode('utf-8') for sentence in sentences])

        parts = []
        for sentence in sentences:
            if len(sentence) < 99:
                # none of len(item) in parts will exceed 100
                # parts: ['xxx, xxx', 'yyy zzz aaa bbb.']
                parts.append(sentence.strip())
            else:
                phrases = None
                # phrases: ['xxx -- xxx', 'yyy zzz aaa']
                if language == 'ja':
                    phrases = sentence.split('、')
                else:
                    phrases = sentence.split(',')
                # remove spaces
                if phrases:
                    phrases = filter(
                        lambda x: x, [phrase.strip().encode('utf-8') for phrase in phrases])

                for phrase in phrases:
                    if len(phrase) < 99:
                        parts.append(phrase.strip())
                    else:
                        words = None
                        if language == 'ja':
                            segmenter = tinysegmenter.TinySegmenter()
                            words = segmenter.tokenize(unicode(phrase))
                        else:
                            words = phrase.split()
                        # convert back to utf-8
                        # remove spaces
                        if words:
                            words = filter(
                                lambda x: x, [word.strip().encode('utf-8') for word in words])

                        # none of len(item) in combined_words will exceed 100
                        # combined_words = ['yyy zzz. aaa bbb']
                        combined_words = ""
                        for word in words:
                            # +1 for possible space
                            if len(combined_words) + len(word) + 1 < 100:
                                if language == 'ja':
                                    combined_words = ("""%s%s""" if word not in string.punctuation else """%s%s""") % (
                                        combined_words, word)
                                else:
                                    combined_words = ("""%s %s""" if word not in string.punctuation else """%s%s""") % (
                                        combined_words, word)
                                combined_words = combined_words.strip()
                            else:
                                parts.append(combined_words.strip())
                                combined_words = word
                        if combined_words:
                            parts.append(combined_words.strip())
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
        return segments
    except Exception as k:
        logger.error(str(k))
        return None


# TODO: Test! Test! Test!
# TODO: boundary checkers
# TODO: write docs!
def _download(language='en', query='Service provided by Baidu', tmp_file='do_not_exist.mp3'):
    """
    docs needed!
    other ways to write _download
    1. https://github.com/hungtruong/Google-Translate-TTS/blob/master/GoogleTTS.py
    2. https://github.com/gavinmh/tts-api/blob/master/text_segmenter.py
    """

    try:
        # break a long sentence/paragraph into google-acceptable length
        segments = _query_segment(language, query)

        # download chunks and write them to the output file
        threads = []
        if segments:
            for segment in segments:
                if segment:
                    logger.info('... Transmitting "%s"' % segment)
                    gt_request = GoogleTranslateAPI(language, segment)
                    threads.append(gt_request)
                    gt_request.start()
                    gt_request.join(GOOGLE_TTS_TIMEOUT)

            out = open(tmp_file, 'a')
            download_completed = True
            for th in threads:
                sys.stdout.flush()
                if th.result:
                    out.write(th.result)
                else:
                    download_completed = False
                    break
            out.close()

            if download_completed:
                return tmp_file
            else:
                logger.error('Download not completed, now removing the file')
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                return None
        else:  # nothing generated from the query
            logger.error('Nothing generated from the query')
            return None
    except Exception as k:
        logger.error(
            'Part of tts dowload went wrong, now removing the file: %s' % str(k))
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        return None
