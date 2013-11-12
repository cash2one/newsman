#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

"""
PyTeaser is a Python version of [TextTeaser]<https://github.com/MojoJolo/textteaser/>
PyTeaser uses nltp instead of Scala/Java's OpenNLP as the NLP engine. It also
manages problems of internationalization, languages supported including Thai, 
Arabic, Chinese, Japanese, Portugues and Indonesian
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Nov. 12, 2013


import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

from config.settings import logger
import html2text


def _score_sentences(article=None, title=None, topwords=None):
    """
    """
    if not article or not title or not topwords:
        logger.error("Method malformed!")
        return None

    try:
        pass
    except Exception as k:
        logger.error(str(k))
        return None


def _find_top_keywords(keywords=None, link=None, blog=None, category=None):
    """
    compute top-scored keywords
    """
    if not keywords:
        logger.error("Method malformed!")
        return None

    try:
        pass
    except Exception as k:
        logger.error(str(k))
        return None


def _find_keywords(article=None):
    """
    compute word-frenquecy map
    """
    if not article:
        logger.error("Method malformed!")
        return None

    try:
        pass
    except Exception as k:
        logger.error(str(k))
        return None


def _segment_text(text=None):
    """
    segment thext into words
    """
    if not text:
        logger.error("Method malformed!")
        return None

    try:
        pass
    except Exception as k:
        logger.error(str(k))
        return None


def _split_article(article=None):
    """
    use nltk or other engines to split the article into sentences
    """
    if not article:
        logger.error("Method malformed!")
        return None

    try:
        pass
    except Exception as k:
        logger.error(str(k))
        return None


def _clean_article(article=None):
    """
    remove html tags, images, links from the article, and encode it appropriately
    """
    if not article:
        logger.error("Method malformed!")
        return None

    try:
        pass
    except Exception as k:
        logger.error(str(k))
        return None


def summarize(language=None, title=None, article=None, link=None, blog=None, category=None):
    """
    summarize is the entry to summarization. it does the following:
    1. 'clean' the article
    2. split article into sentences
    3. segement title
    4. compute keywords of the article
    5. find the 'top' keywords
    6. compute score of each sentence
    7. output the first x sentences in ranking
    """
    pass


def _main():
    language = 'en'
    title = ''
    article = ''
    link = ''
    blog = ''
    category = ''


if __name__ == '__main__':
    _main()
