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


    def _summation_based_selection(self, words=None, keywords=None):
        """
        simple implementation of summation-based selection algorithm
        """
        if not words or not keywords:
            logger.error('Method malformed!')
            return 0

        try:
            word_in_keywords_score = 0
            for word in words:
                for keyword in keywords:
                    keyword_word = keyword[0]
                    keyword_count = keyword[1]
                    if word == keyword_word:
                        word_in_keywords_score = word_in_keywords_score + keyword_count 
                        break
            sbs_score = 1.0 / abs(len(words)) * word_in_keywords_score
            return sbs_score
        except Exception as k:
            logger.error(str(k))
            return 0


    def _density_based_selection(self, word=None, keywords=None):
        """
        simple implementation of density-based selection algorithm
        """
        if not words or not keywords:
            logger.error('Method malformed!')
            return 0

        try:
            # compute number of keyword and its index in words
            word_in_keywords_count = 1
            word_in_keywords_score_with_index = []
            for word in words:
                for index, keyword in enumerate(keywords):
                    keyword_word = keyword[0]
                    keyword_count = keyword[1]
                    if word == keyword_word and keyword_count > 0:
                        word_in_keywords_score_with_index.append((keyword_count, index)) 
                        word_in_keywords_count = word_in_keywords_count + 1
                        break

            # zip keyword-count-index
            # 1: -_score_with_index 2: -_score_with_index_sliced 3: _zipped
            # 1: [(a, 1), (b, 2), (c, 3), (d, 4)]
            # 2: [(b, 2), (c, 3), (d, 4)]
            # 3: [((a, 1), (b, 2)), ((b, 2), (c, 3)), ((c, 3), (d, 4))] 
            word_in_keywords_score_with_index_sliced = word_in_keywords_score_with_index[1:]
            word_in_keywords_zipped = zip(word_in_keywords_score_with_index, word_in_keywords_score_with_index_sliced)

            word_in_keywords_sum_each = [(item[0][0] * item[1][0]) / pow((item[0][1] - item[1][1]), 2)  for item in word_in_keywords_zipped]
            word_in_keywords_sum = reduce(lambda x, y: x + y, word_in_keywords_sum_each)

            dbs_score = (1.0 / (word_in_keywords_count * (word_in_keywords_count + 1.0))) * word_in_keywords_sum
            return dbs_score
        except Exception as k:
            logger.error(str(k))
            return 0


    def _score_sentence_position(self, position, sentence_total):
        """
        score the sence by its position in the article
        """
        if not position or not sentence_total:
            logger.error('Method Malformed!')
            return 0

        try:
            normalized = positon / sentence_total
            sentence_position_score = 0

            if normalized > 0 and normalized <= 0.1:
                sentence_position_score = 0.17
            elif normalized > 0.1 and normalized <= 0.2:
                sentence_position_score = 0.23
            elif normalized > 0.2 and normalized <= 0.3:
                sentence_position_score = 0.14
            elif normalized > 0.3 and normalized <= 0.4:
                sentence_position_score = 0.08
            elif normalized > 0.4 and normalized <= 0.5:
                sentence_position_score = 0.05
            elif normalized > 0.5 and normalized <= 0.6:
                sentence_position_score = 0.04
            elif normalized > 0.6 and normalized <= 0.7:
                sentence_position_score = 0.06
            elif normalized > 0.7 and normalized <= 0.8:
                sentence_position_score = 0.04
            elif normalized > 0.8 and normalized <= 0.9:
                sentence_position_score = 0.04
            elif normalized > 0.9 and normalized <= 1.0:
                sentence_position_score = 0.15
            else:
                sentence_position_score = 0

            return sentence_position_score
        except Exception as k:
            logger.error(str(k))
            return 0

    
    def _score_sentence_length(self, sentence_words):
        """
        score the sentence by its length
        """
        if not sentence_words:
            logger.error("Method malformed!")
            return 0

        try:
            IDEAL_SENTENCE_LENGTH = 20 # unicode words
            sentence_length_score = (IDEAL_SENTENCE_LENGTH - abs(IDEAL_SENTENCE_LENGTH - len(sentence_words))) / float(IDEAL_SENTENCE_LENGTH)
            return sentence_length_score
        except Exception as k:
            logger.error(str(k))
            return 0


    def _score_title(self, sentence_words=None):
        """
        compute number of title words in a sentence
        """
        if not sentence_words:
            logger.error("Method malformed!")
            return 0

        try:
            title_words = self._segment_text(self.title) 
            if title_words:
                # filter out words that are not in title
                sentence_words = [sentence_word for sentence_word in sentence_words if sentence_word in title_words]
                title_score = len(sentence_words) / len(title_words)
                return title_score
            else:
                returen 0
        except Exception as k:
            logger.error(str(k))
            return 0


    def _score_sentences(self, topwords=None):
        """
        compute four factors to score a sentence
        """
        if not topwords:
            logger.error("Method malformed!")
            return None

        try:
            sentences_with_score = []
            sentences = self._split_article()

            for index, sentence in enumerate(sentences):
                sentence_words = self._segment_text(sentence)

                # 1. title-sentence
                title_score = self._score_title(sentence_words)
                # 2. sentence length
                sentence_length_score = self._score_sentence_length(sentence_words)
                # 3. sentence position in article
                sentence_position_score = self._score_sentence_position(index, len(sentences))
                # 4. sentence-keywords
                sbs_score = self._summation_based_selection(sentence_words, topwords) 
                dbs_score = self._density_based_selection(sentence_words, topwords)
                keyword_score = (sbs_score + dbs_score) / 2.0 * 10.0

                sentence_score = title_score * 1.5 + keyword_score * 2.0 + sentence_length_score * 0.5 + sentence_position_score * 1.0 / 4.0
                sentences_with_score.append((sentence, sentence_score, index))

            return sentences_with_score
        except Exception as k:
            logger.error(str(k))
            return None


if __name__ == '__main__':
    teaser = PyTeaser()
    teaser.summarize()
