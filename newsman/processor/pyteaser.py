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
                for t in topwords:
                    print t[0]
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
            sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
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
                command = 'echo "%s" | %s %s/scw.conf %s' % (
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
                            words = [word.strip()
                                     for word in modes[2].split(u'|') if word.strip()]
                        # remove punctuation
                        words = [
                            word for word in words if word not in thai_punctuation]
            else:
                text = re.sub(r'[^\w ]', "", unicode(text), flags=re.UNICODE)
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
            #print len(words)
            #f = open('/home/jinyuan/Downloads/chengdujin.output', 'w')
            #for t in words:
            #    f.write('%s\n' % t)
            #f.close()

            # remove stop words
            stopwords_path = '%s%s_stopwords' % (DATA_PATH, self._language)
            # ar, en, id, ja, pt, th, zh
            f = open(stopwords_path, 'r')
            stopwords = f.readlines()
            stopwords = [stopword.strip()
                         for stopword in stopwords if stopword.strip()]
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
                    {'blog': self._blog, 'language': self._language}).count() + 1.0
                category_count = col.find(
                    {'category': self._category, 'language': self._language}).count() + 1.0
                col.save({'word': word, 'count': count, 'link': self._link, 'blog':
                         self._blog, 'category': self._category, 'language': self._language})

                article_score = float(count) / float(words_count)
                blog_score = float(reduce(lambda x, y: x + y, [item['count'] for item in col.find(
                    {'word': word, 'blog': self._blog}, {'count': 1, '_id': 0})])) / float(blog_count)
                category_score = float(reduce(lambda x, y: x + y, [item['count'] for item in col.find(
                    {'word': word, 'category': self._category}, {'count': 1, '_id': 0})])) / float(category_count)

                #word_score = article_score * 1.5 + blog_score + category_score
                word_score = article_score * 1.5
                topwords.append((word, word_score))

            topwords = sorted(topwords, key=lambda x: -x[1])
            # print '-------------------------------------'
            # for topword in topwords:
            #    print topword[0]
            # print '-------------------------------------'
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
            # print len(words), word_in_keywords_score
            sbs_score = 1.0 / \
                float(abs(len(words))) * float(word_in_keywords_score)
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
            # print word_in_keywords_score_with_index
            word_in_keywords_score_with_index_sliced = word_in_keywords_score_with_index[
                1:]
            word_in_keywords_zipped = zip(
                word_in_keywords_score_with_index, word_in_keywords_score_with_index_sliced)

            word_in_keywords_sum_each = [float(item[0][0] * item[1][0]) / float(pow((item[0][1] - item[1][1]), 2))
                                         for item in word_in_keywords_zipped]
            word_in_keywords_sum = reduce(
                lambda x, y: x + y, word_in_keywords_sum_each) if word_in_keywords_sum_each else 0

            # print word_in_keywords_count, word_in_keywords_sum
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
            sentence_length_score = float(IDEAL_SENTENCE_LENGTH - abs(
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

                # 1. title-sentence
                title_score = self._score_title(sentence_words)
                # 2. sentence length
                sentence_length_score = self._score_sentence_length(
                    sentence_words)
                # 3. sentence position in article
                sentence_position_score = self._score_sentence_position(
                    index + 1, len(sentences))
                # 4. sentence-keywords
                sbs_score = self._summation_based_selection(
                    sentence_words, topwords)
                dbs_score = self._density_based_selection(
                    sentence_words, topwords)
                keyword_score = float(sbs_score + dbs_score) / 2.0 * 10.0

                sentence_score = float(title_score * 1.5 + keyword_score * 2.0 +
                                       sentence_length_score * 0.5 +
                                       sentence_position_score * 1.0) / 4.0
                # print sentence, sentence_score, title_score,
                # sentence_length_score, sentence_position_score, '[',
                # sbs_score, dbs_score, ']'
                sentences_scored.append((sentence, sentence_score, index))

            # rank sentences by their scores
            sentences_scored = sorted(sentences_scored, key=lambda x: -x[1])
            return sentences_scored
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
    title = "Don’t go to art schoolDon’t go to art school"
    text = """The traditional approach is failing us. It’s time for a change.

I’ve had it.

I will no longer encourage aspiring artists to attend art school. I just won’t do it. Unless you’re given a full ride scholarship (or have parents with money to burn), attending art school is a waste of your money.

I have a diploma from the best public art school in the nation. Prior to that I attended the best private art school in the nation. I’m not some flaky, disgruntled art graduate, either. I have a quite successful career, thankyouverymuch.

But I am saddened and ashamed at art schools and their blatant exploitation of students. Graduates are woefully ill-prepared for the realities of being professional artists and racked with obscene amounts of debt. By their own estimation, the cost of a four year education at RISD is $245,816. As way of comparison, the cost of a diploma from Harvard Law School is a mere $236,100.

This is embarrassing. It’s downright shameful. That any art school should deceive its students into believing that this is a smart decision is cruel and unusual.

Artists are neither doctors nor lawyers. We do not, on average, make huge six-figure salaries. We can make livable salaries, certainly. Even comfortable salaries. But we ain’t usually making a quarter mil a year. Hate to break it to you. An online debt repayment calculator recommended a salary exceeding $400,000 in order to pay off a RISD education within 10 years.

Don’t do it.

Don’t start your career with debilitating debt.

Please. I beg you. Think long and hard whether you’re willing to pay student loan companies $3000 every single month for the next 10 years.

You’ve got other options.
You don’t have to go to college to be an artist. Not once have I needed my diploma to get a job. Nobody cares. The education is all that matters. The work that you produce should be your sole concern.

There are excellent atelier schools all over the world that offer superior education for a mere fraction of the price. Here are a few:

Watt’s Atelier
Los Angeles Academy of Figurative Arts
The Safehouse Atelier
There are more. Many, many more. And none of them will cost nearly as much as a traditional four year school.

And then there are the online options. The availability of drawing and painting resources is incredible.

Sitting at a computer I have direct access to artists all over the world. I have the combined wisdom of the artistic community to pull from at my leisure. For less than a few grand a year I can view more educational material than I would see at any art school. You can get a year of access to all of the Gnomon Workshop’s videos for the cost of a few days at the average art school.

With all of these options it can be a little daunting. So you know what? I’ve come up with a plan for you. Do this:

The $10k Ultimate Art Education
$500 - Buy an annual subscription to The Gnomon Workshop and watch every single video they have.
$404.95 - Buy Glenn Vilppu’s Anatomy Lectures and watch all of them.
$190 - Buy all of these books and read them cover to cover.
$1040 ($20/week x 52 weeks) - Weekly figure drawing sessions. Look up nearby colleges and art groups and find a weekly session to attend.
$2500 - Sign up for a SmART School Mentorship when you feel ready to get one-on-one guidance to push your abilities.
$2400 - Sign up for four classes from CGMA. Get taught by professionals in the industry on exactly the skills you want to learn.
Free - Watch all of these keynotes.
Free - Study other things for free. Suggested topics: business, history, philosophy, English, literature, marketing, and anything else you might be interested in.
$500 - Throughout the year, use at least this much money to visit museums in your area. And not just art museums. All museums.
Free - Create accountability. One of the great advantages to attending a school is the comradery. So use the internet to create your own. Go join a forum where you can give and receive critique on the work you’re developing. There are many different ones out there that can suit whatever flavor you prefer.
The rest - Materials. Buy yourself some good art materials to create with. Whether digital or traditional. Don’t skimp.
There. For less than a quarter of the tuition for RISD you’ve got yourself a killer education. You’ve received more quality, focused education than I think you’ll find at any art school.

Moving forward
There has never been a better time to be an artist. I’m inspired by the sheer quantity and quality of internet resources available to artists.

But I encourage all aspiring artists to think long and hard about their options. Student loans are unforgivable through bankruptcy and can wreck your financial future. Establishing a career while under the unceasing brutality of student loans makes an already difficult task nearly impossible.

Find another path. Art is a wonderful, beautiful, fulfilling pursuit. Don’t ruin it with a mountain of debt."""


    teaser = PyTeaser(language, title, text)
    print str(teaser.summarize())
