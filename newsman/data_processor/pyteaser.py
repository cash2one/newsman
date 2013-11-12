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



def _score_sentences(article=None, title=None, topwords=None):
    """
    """
    pass


def _find_top_keywords(keywords=None, link=None, blog=None, category=None):
    """
    compute top-scored keywords
    """
    pass


def _find_keywords(article=None):
    """
    compute word-frenquecy map
    """
    pass


def _segment_text(text=None):
    """
    segment thext into words
    """
    pass


def _split_article(article=None):
    """
    use nltk or other engines to split the article into sentences
    """
    pass


def _clean_article(article=None):
    """
    remove html tags, images, links from the article, and encode it appropriately
    """
    pass


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
