#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

# summarizer extracts summary or first paragraph from news
#
# @author Jin Yuan
# @contact jinyuan@baidu.com
# #created Jul. 29, 2013

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import chardet
import html2text
import nltk


def _get_shorter_text(content, language):
    """
    limit the number of words to 500
    """
    if not content or not language:
        return False

    # break text by sentence
    if language.startswith('zh') or language == 'ja':
        pass
    else: # supports latin-based, thai and arabic
        sentences = nltk.sent_tokenize(content)


def _is_valid(content, language):
    """
    check if the content meets the need
    """
    if not content or not language:
        return False

    if language.startswith('zh') or language == 'ja':
        if isinstance(content, str):
            words = content.decode(chardet.detect(content)['encoding'])
    else:
        words = content.split()

    if len(words) < 10:
        return False
    else:
        return True


def extract(entry):
    """
    get the summary/first paragraph, text only
    """
    if not entry:
        raise Exception('ERROR: No data is found!')

    # if summary from rss provider is found
    #     use summary, but limit the number of words
    if entry['summary']:
        paragraphs = entry['summary'].split("\n\n")
        for paragraph in paragraphs:
            if _is_valid(paragraph, entry['language']):
                return _get_shorter_text(paragraph, entry['language'])

    # else if summary could be generated
    #     use summary, limit the number of words
    # else find first paragraph from transcoded
    #     also limit the number of words
    pass

