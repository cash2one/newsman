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
import math
import nltk
from nltk.tokenize import *
import re
import string
import subprocess
import tinysegmenter
import urllib2

# CONSTANTS
from config.settings import KEYWORD_REGISTRAR
from config.settings import DATA_PATH
from config.settings import THAI_WORDSEG
from config.settings import THAI_WORDSEG_DICT
from config.settings import TOP_KEYWORDS_LIMIT
from config.settings import SCORED_SENTENCE_LIMIT


class PyTeaser:

    """
    PyTeaser extracts key sentences from an article
    """

    def __init__(self, language=None, title=None, article=None, link=None, blog=None, category=None):
        if not language or not title or not article:
            logger.error('Method malformed!')

        self._language = language
        self._title = title
        self._article = article
        self._link = link
        self._blog = blog
        self._category = category

    def summarize(self):
        """
        summarize is the entry to summarization
        """
        # 'clean' the article
        self._clean_article()

        if self._article:
            # find keywords of the article
            compound_keywords = self._find_keywords()
            if compound_keywords:
                keywords = compound_keywords[0]
                words_count = compound_keywords[1]

                # find top keywords
                topwords = self._find_top_keywords(keywords, words_count)
                if topwords:
                    # compute sentence scores
                    sentences_scored = self._score_sentences(topwords)
                    if sentences_scored:
                        # render the data
                        sentences_selected = self._render(sentences_scored)
                        return sentences_selected
        return None

    def _clean_article(self):
        """
        remove html tags, images, links from the article, and encode it appropriately
        """
        try:
            # convert to normal encoding
            self._article = str(
                urllib2.unquote(hparser.unescape(self._article)))

            # remove unnecessary parts
            html_stripper = html2text.HTML2Text()
            html_stripper.ignore_links = True
            html_stripper.ignore_images = True
            html_stripper.ignore_emphasis = True
            # body_width = 0 disables text wrapping
            html_stripper.body_width = 0
            self._article = html_stripper.handle(self._article).strip("#")

            # convert to appropriate encoding
            if isinstance(self._article, str):
                self._article = self._article.decode(
                    chardet.detect(self._article)['encoding'], 'ignore')
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
            if self._language == 'zh' or self._language == 'ja':
                cj_sent_tokenizer = nltk.RegexpTokenizer(
                    u'[^!?.！？。．]*[!?.！？。]*')
                sentences = cj_sent_tokenizer.tokenize(self._article)
            elif self._language == 'th':
                sentences = self._article.split()
            else:  # latin-based
                sentences = nltk.sent_tokenize(self._article)

            # remove spaces
            sentences = [sentence.strip()
                         for sentence in sentences if sentence.strip()]
            return sentences
        except Exception as k:
            logger.error(str(k))
            return None

    def _segment_text(self, text=None):
        """
        segment text into words
        """
        if not text:
            logger.error("Method malformed!")
            return None

        try:
            # put the text in the right encoding
            if isinstance(text, str):
                text = text.decode(
                    chardet.detect(text)['encoding'], 'ignore')

            # chinese and japanese punctuation
            cj_punctuation = u"-〃〈-「『【［[〈《（(｛{」』】］]〉》）)｝}。．.!！?？、-〟〰-＃％-＊，-／：-；-＠-＿｛｝｟-･‐-―“-”…-‧﹏"
            # thai punctuation, from
            # http://blogs.transparent.com/thai/thai-punctuation-marks-other-characters-part-2/
            thai_punctuation = u"อ์()“!,๛ๆฯฯลฯ?."

            words = []
            # word segment
            if self._language == 'ja':
                segmenter = tinysegmenter.TinySegmenter()
                words = segmenter.tokenize(text)
                # remove punctuation
                words = [word.strip()
                         for word in words if word.strip() and word not in cj_punctuation]
            elif self._language == 'zh':
                jieba.enable_parallel(4)
                seg_list = jieba.cut(text)
                for seg in seg_list:
                    words.append(seg)
                # remove punctuation
                words = [word.strip()
                         for word in words if word.strip() and word not in cj_punctuation]
            elif self._language == 'th':
                command = 'echo "%s" | %s %s/scw.conf %s 2>/dev/null' % (
                    str(text), THAI_WORDSEG, THAI_WORDSEG_DICT, THAI_WORDSEG_DICT)
                response = subprocess.Popen(
                    command, stdout=subprocess.PIPE, shell=True)
                content, error = response.communicate()
                if not error and content:
                    if 'error' not in content or 'permission' not in content:
                        content = content.strip()
                        paragraphs = [paragraph.strip()
                                      for paragraph in content.split('\n') if paragraph.strip()]
                        for paragraph in paragraphs:
                            modes = [mode.strip()
                                     for mode in paragraph.split('\t') if mode.strip()]
                            # modes[0]: the orginal
                            # modes[1]: phrase seg
                            # modes[2]: basic wordseg
                            # modes[3]: subphrase seg
                            if len(modes) > 2:
                                words = [word.strip() for word in modes[2].split(u'|') if word.strip()]
                        # remove punctuation
                        words = [
                            word for word in words if word not in thai_punctuation]
            else:
                # for python 2.6
                text = re.compile(
                    r'[^\w ]', flags=re.UNICODE).sub("", unicode(text))
                # for python 2.7
                #text = re.sub(r'[^\w ]', "", unicode(text), flags=re.UNICODE)
                words = [str(word).strip('.').lower() for word in text.split()]
            return words
        except Exception as k:
            logger.error(str(k))
            return None

    def _find_keywords(self):
        """
        compute word-frenquecy map
        """
        try:
            words = self._segment_text(self._article)

            # remove stop words
            stopwords_path = '%s%s_stopwords' % (DATA_PATH, self._language)
            # ar, en, id, ja, pt, th, zh
            f = open(stopwords_path, 'r')
            stopwords = f.readlines()
            f.close()
            #stopwords = [stopword.strip() for stopword in stopwords if stopword.strip()]
            stopwords = [str(re.compile(r'[^\w ]', flags=re.UNICODE).sub("", unicode(stopword.strip())))
                         for stopword in stopwords if stopword.strip()]
            words_filtered = [word for word in words if word not in stopwords]

            # distinct words
            kwords = list(set(words_filtered))

            # word-frenquency
            keywords = [(kword, words_filtered.count(kword))
                        for kword in kwords]
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
            #col = Collection(db, KEYWORD_REGISTRAR)
            top_keywords = keywords[:TOP_KEYWORDS_LIMIT]
            topwords = []

            for top_keyword in top_keywords:
                word = top_keyword[0]
                count = top_keyword[1]

                article_score = float(count) * 1.0 / float(words_count)
                word_score = article_score * 1.5
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
                    if word in keyword_word or keyword_word in word:
                        word_in_keywords_score = word_in_keywords_score + \
                            keyword_count
                        break
            sbs_score = (
                1.0 / math.fabs(len(words)) * float(word_in_keywords_score))
            return sbs_score
        except Exception as k:
            logger.error(str(k))
            return 0

    def _density_based_selection(self, words=None, keywords=None):
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
            for index, word in enumerate(words):
                for keyword in keywords:
                    keyword_word = keyword[0]
                    keyword_count = keyword[1]
                    if (word in keyword_word or keyword_word in word) and keyword_count > 0:
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

            word_in_keywords_sum_each = [float(item[0][0] * item[1][0]) / float(pow((item[0][1] - item[1][1]), 2))
                                         for item in word_in_keywords_zipped]
            word_in_keywords_sum = reduce(
                lambda x, y: x + y, word_in_keywords_sum_each) if word_in_keywords_sum_each else 0

            dbs_score = 1.0 / float(word_in_keywords_count) * float(word_in_keywords_count + 1.0) * \
                float(word_in_keywords_sum)
            return dbs_score
        except Exception as k:
            logger.error(str(k))
            return 0

    def _score_sentence_position(self, position=None, sentence_total=None):
        """
        score the sence by its position in the article
        """
        if position == None or not sentence_total:
            logger.error('Method Malformed!')
            return 0

        try:
            normalized = float(position) / float(sentence_total)
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

    def _score_sentence_length(self, sentence_words=None):
        """
        score the sentence by its length
        """
        if not sentence_words:
            logger.error("Method malformed!")
            return 0

        try:
            IDEAL_SENTENCE_LENGTH = 20  # unicode words
            sentence_length_score = 1.0 - \
                math.fabs(IDEAL_SENTENCE_LENGTH - len(sentence_words)) / float(
                    IDEAL_SENTENCE_LENGTH)
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
            title_words = self._segment_text(self._title)
            if title_words:
                # filter out words that are not in title
                sentence_words = [
                    sentence_word for sentence_word in sentence_words if sentence_word in title_words]
                title_score = float(
                    len(sentence_words)) / float(len(title_words))
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

                if sentence_words:
                    # 1. title-sentence
                    title_score = self._score_title(sentence_words)
                    # 2. sentence length
                    sentence_length_score = self._score_sentence_length(sentence_words)
                    # 3. sentence position in article
                    sentence_position_score = self._score_sentence_position(index + 1, len(sentences))
                    # 4. sentence-keywords
                    sbs_score = self._summation_based_selection(sentence_words, topwords)
                    dbs_score = self._density_based_selection(sentence_words, topwords)
                    keyword_score = float(sbs_score + dbs_score) / 2.0 * 10.0

                    sentence_score = float(title_score * 1.5 + keyword_score * 2.0 + sentence_length_score * 0.5 + sentence_position_score * 1.0) / 4.0
                    # sentence_length_score, sentence_position_score, '[',
                    # sbs_score, dbs_score, ']'
                    sentences_scored.append((sentence, sentence_score, index))

            # rank sentences by their scores
            if sentences_scored:
                sentences_scored = sorted(sentences_scored, key=lambda x: -x[1])
                return sentences_scored
            else:
                return None
        except Exception as k:
            logger.error(str(k))
            return None

    def _render(self, sentences_scored=None):
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
            return sentences_selected
        except Exception as k:
            logger.error(str(k))
            return None


if __name__ == '__main__':
    language = 'en'
    title = "McDonald’s Theory"
    text = """I use a trick with co-workers when we’re trying to decide where to eat for lunch and no one has any ideas. I recommend McDonald’s.

An interesting thing happens. Everyone unanimously agrees that we can’t possibly go to McDonald’s, and better lunch suggestions emerge. Magic!

It’s as if we’ve broken the ice with the worst possible idea, and now that the discussion has started, people suddenly get very creative. I call it the McDonald’s Theory: people are inspired to come up with good ideas to ward off bad ones.

This is a technique I use a lot at work. Projects start in different ways. Sometimes you’re handed a formal brief. Sometimes you hear a rumor that something might be coming so you start thinking about it early. Other times you’ve been playing with an idea for months or years before sharing with your team. There’s no defined process for all creative work, but I’ve come to believe that all creative endeavors share one thing: the second step is easier than the first. Always.

Anne Lamott advocates “shitty first drafts,” Nike tells us to “Just Do It,” and I recommend McDonald’s just to get people so grossed out they come up with a better idea. It’s all the same thing. Lamott, Nike, and McDonald’s Theory are all saying that the first step isn’t as hard as we make it out to be. Once I got an email from Steve Jobs, and it was just one word: “Go!” Exactly. Dive in. Do. Stop over-thinking it.

The next time you have an idea rolling around in your head, find the courage to quiet your inner critic just long enough to get a piece of paper and a pen, then just start sketching it. “But I don’t have a long time for this!” you might think. Or, “The idea is probably stupid,” or, “Maybe I’ll go online and click around for—”

No. Shut up. Stop sabotaging yourself.

The same goes for groups of people at work. The next time a project is being discussed in its early stages, grab a marker, go to the board, and throw something up there. The idea will probably be stupid, but that’s good! McDonald’s Theory teaches us that it will trigger the group into action.

It takes a crazy kind of courage, of focus, of foolhardy perseverance to quiet all those doubts long enough to move forward. But it’s possible, you just have to start. Bust down that first barrier and just get things on the page. It’s not the kind of thing you can do in your head, you have to write something, sketch something, do something, and then revise off it.

Not sure how to start? Sketch a few shapes, then label them. Say, “This is probably crazy, but what if we.…” and try to make your sketch fit the problem you’re trying to solve. Like a magic spell, the moment you put the stuff on the board, something incredible will happen. The room will see your ideas, will offer their own, will revise your thinking, and by the end of 15 minutes, 30 minutes, an hour, you’ll have made progress.

That’s how it’s done"""

    teaser = PyTeaser(language, title, text)
    print str(teaser.summarize())
