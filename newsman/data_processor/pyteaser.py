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
from nltk.tokenize import *
import string
import subprocess
import tinysegmenter
import urllib2

# CONSTANTS
from config.settings import KEYWORD_REGISTRAR
from config.settings import STOP_WORDS
from config.settings import THAI_WORDCUT_INPUT
from config.settings import THAI_WORDCUT_OUTPUT
from config.settings import TOP_KEYWORDS_LIMIT
from config.settings import SCORED_SENTENCE_LIMIT


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
        """
        # 'clean' the article
        self._clean_article()

        # find keywords of the article
        compound_keywords = self._find_keywords()
        keywords = compound_keywords[0]
        words_count = compound_keywords[1]

        # find top keywords
        topwords = self._find_top_keywords(keywords, words_count)

        # compute sentence scores
        sentences_scored = self._score_sentences(topwords)

        # render the data
        sentences_selected = self._render(sentences_scored)
        return sentences_selected

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
            self.article = self.article.decode(
                chardet.detect(self.article)['encoding'], 'ignore')
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
                cj_sent_tokenizer = nltk.RegexpTokenizer(
                    u'[^!?.！？。．]*[!?.！？。]*')
                sentences = cj_sent_tokenizer.tokenize(self.article)
            elif self.language == 'th':
                sentences = self.article.split()
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
                text = text.decode(
                    chardet.detect(self.article)['encoding'], 'ignore')

            # chinese and japanese punctuation
            cj_punctuation = u"-〃〈-「『【［[〈《（(｛{」』】］]〉》）)｝}。．.!！?？、-〟〰-＃％-＊，-／：-；-＠-＿｛｝｟-･‐-―“-”…-‧﹏"
            # thai punctuation, from
            # http://blogs.transparent.com/thai/thai-punctuation-marks-other-characters-part-2/
            thai_punctuation = u"อ์()“!,๛ๆฯฯลฯ?."

            # word segment
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
            elif self.language == 'th':
                response = subprocess.Popen('''swath -m max < %s 2>&1 | tee %s''' % (
                    THAI_WORDCUT_INPUT, THAI_WORDCUT_OUTPUT), stdout=subprocess.PIPE, shell=True)
                content, error = response.communicate()
                if not error and content:
                    if 'error' not in content or 'permission' not in content:
                        content = content.strip()
                        words = [
                            word for word in content.split("|") if word.strip()]
                        # remove punctuation
                        words = [
                            word for word in words if word not in thai_punctuation]
            else:
                words = WordPunctTokenizer.tokenize(text)
                # remove punctuation
                words = [word.lower()
                         for word in words if word not in string.punctuation]
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
            stopwords_path = '%s%s_stopwords' % (STOP_WORDS, self.language)
            # ar, en, id, ja, pt, th, zh
            f = open(stopwords_path, 'r')
            stopwords = f.readlines()
            f.close()
            words = [word for word in words if word not in stopwords]

            # distinct words
            kwords = list(set(words))

            # word-frenquency
            keywords = [(kword, words.count(kword)) for kword in kwords]
            keywords = sorted(keywords, key=lambda x: -x[1])

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
            top_keywords = keywords[:TOP_KEYWORDS_LIMIT]
            topwords = []

            for top_keyword in top_keywords:
                word = top_keyword[0]
                count = top_keyword[1]

                blog_count = col.find(
                    {'blog': self.blog, 'language': self.language}).count() + 1.0
                category_count = col.find(
                    {'category': self.category, 'language': self.language}).count() + 1.0
                col.save({'word': word, 'count': count, 'link': self.link, 'blog':
                         self.blog, 'category': self.category, 'language': self.language})

                article_score = count / words_count
                blog_score = reduce(lambda x, y: x + y, [item['count'] for item in col.find(
                    {'word': word, 'blog': self.blog}, {'count': 1, '_id': 0})]) / blog_count
                category_score = reduce(lambda x, y: x + y, [item['count'] for item in col.find(
                    {'word': word, 'category': self.category}, {'count': 1, '_id': 0})]) / category_count

                word_score = article_score * 1.5 + blog_score + category_score
                topwords.append((word, word_score))

            topwords = sorted(topwords, key=lambda x: -x[1])
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
                        word_in_keywords_score = word_in_keywords_score + \
                            keyword_count
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
                        word_in_keywords_score_with_index.append(
                            (keyword_count, index))
                        word_in_keywords_count = word_in_keywords_count + 1
                        break

            # zip keyword-count-index
            # 1: -_score_with_index 2: -_score_with_index_sliced 3: _zipped
            # 1: [(a, 1), (b, 2), (c, 3), (d, 4)]
            # 2: [(b, 2), (c, 3), (d, 4)]
            # 3: [((a, 1), (b, 2)), ((b, 2), (c, 3)), ((c, 3), (d, 4))]
            word_in_keywords_score_with_index_sliced = word_in_keywords_score_with_index[
                1:]
            word_in_keywords_zipped = zip(
                word_in_keywords_score_with_index, word_in_keywords_score_with_index_sliced)

            word_in_keywords_sum_each = [(item[0][0] * item[1][0]) / pow((item[0][1] - item[1][1]), 2)
                                         for item in word_in_keywords_zipped]
            word_in_keywords_sum = reduce(
                lambda x, y: x + y, word_in_keywords_sum_each)

            dbs_score = (1.0 / (word_in_keywords_count * (word_in_keywords_count + 1.0))) * \
                word_in_keywords_sum
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
            IDEAL_SENTENCE_LENGTH = 20  # unicode words
            sentence_length_score = (IDEAL_SENTENCE_LENGTH - abs(
                IDEAL_SENTENCE_LENGTH - len(sentence_words))) / float(IDEAL_SENTENCE_LENGTH)
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
                sentence_words = [
                    sentence_word for sentence_word in sentence_words if sentence_word in title_words]
                title_score = len(sentence_words) / len(title_words)
                return title_score
            else:
                return 0
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
            sentences_scored = []
            sentences = self._split_article()

            for index, sentence in enumerate(sentences):
                sentence_words = self._segment_text(sentence)

                # 1. title-sentence
                title_score = self._score_title(sentence_words)
                # 2. sentence length
                sentence_length_score = self._score_sentence_length(
                    sentence_words)
                # 3. sentence position in article
                sentence_position_score = self._score_sentence_position(
                    index, len(sentences))
                # 4. sentence-keywords
                sbs_score = self._summation_based_selection(
                    sentence_words, topwords)
                dbs_score = self._density_based_selection(
                    sentence_words, topwords)
                keyword_score = (sbs_score + dbs_score) / 2.0 * 10.0

                sentence_score = title_score * 1.5 + keyword_score * 2.0 + \
                    sentence_length_score * 0.5 + \
                    sentence_position_score * 1.0 / 4.0
                sentences_scored.append((sentence, sentence_score, index))

            # rank sentences by their scores
            sentences_scored = sorted(sentences_scored, key=lambda x: -x[1])
            return sentences_scored
        except Exception as k:
            logger.error(str(k))
            return None

    def _render(self, sentences_scored):
        """
        select indicated number of key sentences, rank them by their original 
        position in the article and output in JSON

        sentence_scored: (sentence, score, index)
        """
        if not sentences_scored:
            logger.error('Method malformed!')
            return None

        try:
            sentences_scored_limited = sentences_scored[:SCORED_SENTENCE_LIMIT]
            # reorder sentence by their position in article
            # order by increasing
            sentences_scored_limited = sorted(
                sentences_scored_limited, key=lambda x: x[2])

            sentences_selected = '\n\n'.join(
                [item[0] for item in sentences_scored_limited])
            return output
        except Exception as k:
            logger.error(str(k))
            return None


if __name__ == '__main__':
    title = "Astronomic news: the universe may not be expanding after all"
    text = """Now that conventional thinking has been turned on its head in a paper by Prof Christof Wetterich at the University of Heidelberg in Germany. He points out that the tell-tale light emitted by atoms is also governed by the masses of their constituent particles, notably their electrons. The way these absorb and emit light would shift towards the blue part of the spectrum if atoms were to grow in mass, and to the red if they lost it.  Because the frequency or ÒpitchÓ of light increases with mass, Prof Wetterich argues that masses could have been lower long ago. If they had been constantly increasing, the colours of old galaxies would look red-shifted Ð and the degree of red shift would depend on how far away they were from Earth. ÒNone of my colleagues has so far found any fault [with this],Ó he says.  Although his research has yet to be published in a peer-reviewed publication, Nature reports that the idea that the universe is not expanding at all Ð or even contracting Ð is being taken seriously by some experts, such as Dr HongSheng Zhao, a cosmologist at the University of St Andrews who has worked on an alternative theory of gravity. ÒI see no fault in [Prof WetterichÕs] mathematical treatment,Ó he says. ÒThere were rudimentary versions of this idea two decades ago, and I think it is fascinating to explore this alternative representation of the cosmic expansion, where the evolution of the universe is like a piano keyboard played out from low to high pitch.Ó  Prof Wetterich takes the detached, even playful, view that his work marks a change in perspective, with two different views of reality: either the distances between galaxies grow, as in the traditional balloon picture, or the size of atoms shrinks, increasing their mass. Or itÕs a complex blend of the two. One benefit of this idea is that he is able to rid physics of the singularity at the start of time, a nasty infinity where the laws of physics break down. Instead, the Big Bang is smeared over the distant past: the first note of the ''cosmic pianoÕÕ was long and low-pitched.  Harry Cliff, a physicist working at CERN who is the Science MuseumÕs fellow of modern science, thinks it striking that a universe where particles are getting heavier could look identical to one where space/time is expanding. ÒFinding two different ways of thinking about the same problem often leads to new insights,Ó he says. ÒString theory, for instance, is full of 'dualitiesÕ like this, which allow theorists to pick whichever view makes their calculations simpler.Ó  If this idea turns out to be right Ð and that is a very big if Ð it could pave the way for new ways to think about our universe. If we are lucky, they might even be as revolutionary as Edwin HubbleÕs, almost a century ago.  Roger Highfield is director of external affairs at the Science Museum"""

    teaser = PyTeaser('en', title, text)
    print teaser.summarize()
