#!/usr/bin/env python
#-*- coding: utf-8 -*-

""" 
summarizer extracts summary or first paragraph from news
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# created Jul. 29, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import chardet
from config import logger
import html2text
import nltk

# CONSTANTS
from config import PARAGRAPH_CRITERIA
from config import SUMMARY_LENGTH_LIMIT


def _get_shorter_text(content, language, limit):
    """
    limit the number of words to 500
    """
    if not content or not language:
        logger.error('Method malformed!')
        return None

    try:
        # data should be processed as unicode, so
        if isinstance(content, str):
            content = content.decode(
                chardet.detect(content)['encoding'], 'ignore')

        # break text by sentence
        if language.startswith('zh') or language == 'ja':
            jp_sent_tokenizer = nltk.RegexpTokenizer(u'[^!?.！？。．]*[!?.！？。]*')
            sentences = jp_sent_tokenizer.tokenize(content)
        else:  # supports latin-based, thai and arabic
            sentences = nltk.sent_tokenize(content)

        enough_sentences = u""
        for sentence in sentences:
            # sentence is in unicode, len() then applies to CJK
            sentence = sentence.strip()
            if sentence:
                if len(enough_sentences) + len(sentence) + 1 <= limit:
                    enough_sentences = "%s %s" % (enough_sentences, sentence)

        return str(enough_sentences.strip())
    except Exception as k:
        pass
        logger.error(str(k))
        return None


def _is_valid(content, language):
    """
    check if the content meets the need
    """
    if not content or not language:
        logger.error('Method malformed!')
        return False

    try:
        if isinstance(content, str):
            content = content.decode(
                chardet.detect(content)['encoding'], 'ignore')

        if language.startswith('zh') or language == 'ja':
            words = content
        else:
            words = content.split()

        if len(words) < PARAGRAPH_CRITERIA:
            return False
        else:
            return True
    except Exception as k:
        pass
        logger.error(str(k))
        return False


def _get_first_paragraph(content, language):
    """
    find the first paragraph from transcoded text
    """
    try:
        # strip off html code
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True
        paragraphs = (h.handle(content)).strip('#').split("\n\n")
        for paragraph in paragraphs:
            if _is_valid(paragraph, language):
                return _get_shorter_text(paragraph, language, SUMMARY_LENGTH_LIMIT)
    except Exception as K:
        pass
        logger.error(str(k))
        return None


def _get_summary(content, language):
    """
    find out the first readable summary
    """
    if not content or not language:
        logger.error('Method malformed!')
        return None

    try:
        paragraphs = content.split("\n\n")
        for paragraph in paragraphs:
            if _is_valid(paragraph, language):
                return _get_shorter_text(paragraph, language, SUMMARY_LENGTH_LIMIT)
    except Exception as k:
        pass
        logger.error(str(k))
        return None


def extract(summary, transcoded, language):
    """
    get the summary/first paragraph, text only
    """
    if not summary and not transcoded:
        logger.error('No data is found!')
        return None

    try:
        result_summary = result_first_paragraph = ""

        # if summary from rss provider is found
        #     use summary, but limit the number of words
        if summary:
            result_summary = _get_summary(summary, language)
        #    if result_summary:
        #        print '  SUMMARY:', len(result_summary), result_summary

        # else if summary could be generated
        #     use summary, limit the number of words

        # else find first paragraph from transcoded
        #     also limit the number of words
        if transcoded:
            result_first_paragraph = _get_first_paragraph(transcoded, language)
        #    if result_first_paragraph:
        # print '  FIRST PARAGRAPH:', len(result_first_paragraph),
        # result_first_paragraph

        return result_summary if result_summary else result_first_paragraph if result_first_paragraph else None
    except Exception as k:
        pass
        logger.error(str(k))
        return None
