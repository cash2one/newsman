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

import chardet
from config.settings import hparser
from config.settings import logger
import html2text
import nltk
import tinysegmenter
import urllib2


class PyTeaser:
    """
    PyTeaser extracts key sentences from an article
    """

    def __init__(self, language=None, title=None, article=None, link=None, blog=None, category=None):
        if not language or not title or not article:
            logger.error('Method malformed!')

        self.language = language
        self.title = title
        self.article = article
        self.link = link
        self.blog = blog
        self.category = category
        self.sentences = None


    def summarize(self):
        """
        summarize is the entry to summarization
        3. segement title
        4. compute keywords of the article
        5. find the 'top' keywords
        6. compute score of each sentence
        7. output the first x sentences in ranking
        """
        # 'clean' the article
        _clean_article()

        # split article into sentences
        _split_article()


    def _clean_article(self):
        """
        remove html tags, images, links from the article, and encode it appropriately
        """
        try:
            # convert to normal encoding
            self.article = str(urllib2.unquote(hparser.unescape(self.article)))

            # remove unnecessary parts
            html_stripper = html2text.HTML2Text()
            html_stripper.ignore_links = True
            html_stripper.ignore_images = True
            html_stripper.ignore_emphasis = True
            self.article = html_stripper.handle(self.article).strip("#")

            # convert to appropriate encoding
            self.article = self.article.decode(chardet.detect(self.article)['encoding'], 'ignore')
        except Exception as k:
            logger.error(str(k))
            return None


    def _split_article(self):
        """
        use nltk or other engines to split the article into sentences
        """
        try:
            # special: thai, arabic
            if self.language == 'zh' or self.language == 'ja':
                cj_sent_tokenizer = nltk.RegexpTokenizer(u'[^!?.！？。．]*[!?.！？。]*')
                self.sentences = cj_sent_tokenizer.tokenize(self.article)
            else:  # latin-based
                self.sentences = nltk.sent_tokenize(self.article)

            # remove spaces
            self.sentences = [sentence.strip() for sentence in sentences]
        except Exception as k:
            logger.error(str(k))
            return None


    def _segment_text(self, text=None):
        """
        segment thext into words
        """
        if not text:
            logger.error("Method malformed!")
            return None

        try:
            # put the text in the right encoding
            if isinstance(text, str):
                text = text.decode(chardet.detect(self.article)['encoding'], 'ignore')

            if self.language == 'zh' or self.language == 'ja':
                segmenter = tinysegmenter.TinySegmenter()
                words = segmenter.tokenize(text)
                cj_punctuation = u"-〃〈-「『【［[〈《（(｛{」』】］]〉》）)｝}。．.!！?？、-〟〰-＃％-＊，-／：-；-＠-＿｛｝｟-･‐-―“-”…-‧﹏"
                words = [word for word in words if word not in cj_punctuation]
            else:
                from nltk.tokenize import *
                words = WordPunctTokenizer.tokenize(text)
                # remove punctuation
                import string
                words = [word.lower() for word in words if word not in string.punctuation]
            return words
        except Exception as k:
            logger.error(str(k))
            return None


    def _find_keywords(self):
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


if __name__ == '__main__':
    teaser = PyTeaser()
    teaser.summarize()
