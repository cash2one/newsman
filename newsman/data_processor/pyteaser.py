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
from config.settings import Collection, db
from config.settings import hparser
from config.settings import logger
import html2text
import jieba
import nltk
import tinysegmenter
import urllib2

# CONSTANTS
from config.settings import KEYWORD_REGISTRAR
from config.settings import STOP_WORDS


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


    def summarize(self):
        """
        summarize is the entry to summarization
        3. segement title
        5. find the 'top' keywords
        6. compute score of each sentence
        7. output the first x sentences in ranking
        """
        # 'clean' the article
        self._clean_article()

        # find keywords of the article
        compound_keywords = self._find_keywords()
        keywords = compound_keywords[0]
        words_count = compound_keywords[1]

        # find top keywords
        topwords = self._find_top_keywords(keywords, words_count)


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
            sentences = None
            # special: thai, arabic
            if self.language == 'zh' or self.language == 'ja':
                cj_sent_tokenizer = nltk.RegexpTokenizer(u'[^!?.！？。．]*[!?.！？。]*')
                sentences = cj_sent_tokenizer.tokenize(self.article)
            else:  # latin-based
                sentences = nltk.sent_tokenize(self.article)

            # remove spaces
            sentences = [sentence.strip() for sentence in sentences]
            return sentences
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

            # chinese and japanese punctuation
            cj_punctuation = u"-〃〈-「『【［[〈《（(｛{」』】］]〉》）)｝}。．.!！?？、-〟〰-＃％-＊，-／：-；-＠-＿｛｝｟-･‐-―“-”…-‧﹏"
            if self.language == 'ja':
                segmenter = tinysegmenter.TinySegmenter()
                words = segmenter.tokenize(text)
                # remove punctuation
                words = [word for word in words if word not in cj_punctuation]
            elif self.language == 'zh':
                jieba.enable_parallel(4)
                seg_list = jieba.cut(text)
                for seg in seg_list:
                    words.append(seg)
                # remove punctuation
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
        try:
            words = self._segment_text(self.article)

            # remove stop words
            stopwords_path = '%s%s' % (STOP_WORDS, self.language)
            # ar, en, id, ja, pt, th, zh
            f = open(stopwords_path, 'r')
            stopwords = f.readlines()
            f.close()
            words = [word for word in words if word not in stopwords]
            
            # distinct words
            kwords = list(set(words))
            
            # word-frenquency
            keywords = [(kword, words.count(kword)) for kword in kwords]
            keywords = sorted(keywords, key=lambda x:-x[1])

            return (keywords, len(words))
        except Exception as k:
            logger.error(str(k))
            return None


    def _find_top_keywords(self, keywords=None, words_count=None):
        """
        compute top-scored keywords
        """
        if not keywords or not words_count:
            logger.error("Method malformed!")
            return None

        try:
            col = Collection(db, KEYWORD_REGISTRAR)
            TOP_KEYWORDS = 10
            top_keywords = keywords[:TOP_KEYWORDS]
            topwords = []

            for top_keyword in top_keywords:
                word = top_keyword[0]
                count = top_keyword[1]

                blog_count = col.find({'blog':self.blog, 'language':self.language}).count() + 1.0
                category_count = col.find({'category':self.category, 'language':self.language}).count() + 1.0
                col.save({'word':word, 'count':count, 'link':self.link, 'blog':self.blog, 'category':self.category, 'language':self.language})

                article_score = count / words_count
                blog_score = reduce(lambda x, y: x + y, [item['count'] for item in col.find({'word':word, 'blog':self.blog}, {'count':1, '_id':0})]) / blog_count
                category_score = reduce(lambda x, y: x + y, [item['count'] for item in col.find({'word':word, 'category':self.category}, {'count':1, '_id':0})]) / category_count

                word_score = article_score * 1.5 + blog_score + category_score
                topwords.append((word, word_score))

            topwords = sorted(topwords, key=lambda x:-x[1])
            return topwords
        except Exception as k:
            logger.error(str(k))
            return None


    def _score_sentences(self, sentence=None, topwords=None):
        """
        """
        if not sentences or not topwords:
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
