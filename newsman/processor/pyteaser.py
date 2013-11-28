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
                # print len(sentences)
                # print sentences
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
            # lating punctuation
            #latin_punctuation = "’“”," + string.punctuation
            latin_punctuation = string.punctuation

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
                words = WordPunctTokenizer().tokenize(text)
                # remove punctuation
                words = [word.strip().lower()
                         for word in words if word.strip() and word.strip() not in latin_punctuation]
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

                word_score = article_score * 1.5 + blog_score + category_score
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
    title = "Apple Literally Stole My Thunder"
    text = """I’ve been a developer for iOS since one could develop for iOS. And I’ve created a lot of apps, some very successful. As such, I’ve had my fair share of rejections, both warranted and unwarranted. I’m not one to complain, but this latest is simply unbearable.

The first app I ever developed is still sitting in iTunes Connect. At the time it was innovative, but the world has moved on. Back before there was “an app for that”—before the most popular sites, even Google, became mobile (or responsive)—there was an app I made called, simply, “Images.”

It did one thing, and it did it well: show you images of whatever you searched for. Essentially, it did what Google Images does now on their mobile-optimized site: show you a text field with large, swipable images below. The idea was, if you were out at a party and didn’t know what a honeybadger looked like, you could get that info to share in as few taps as possible.

Apple rejected it. Back then, you were just rejected, with no rhyme nor reason. You actually had to write in just to request you be given an explanation. I did just that. The reason: porn. Since you could type in anything and get an image for it, you could also type in lewd text and possibly receive an explicit image. Any app that allowed this, they said, would be rejected. Nevermind that you could also go to Google images using the native Safari app and do exactly the same thing.

I fought, but lost. This was a big enough “fuck you” that I swore I’d never write another iPhone app.

The App Store eventually became more transparent and logical with its review process. And I didn’t stop developing iPhone apps for more than a few months: I enjoyed it too much, and knew, for better or worse, that it was the future. That app still sits there, never to see the light of day. It was a lot of work back then, for nothing, but I’ve moved on to create a few successful indie apps.

My latest rejection, however, has me fuming — of a weather app I developed a few months ago. Now, I personally see weather apps, like to-do apps and flashlight apps before them, to be one of those lowest-common-denominator apps. They’re relatively easy to build, so lots of them get built by mediocre developers, and the store gets overrun. I was fully aware of this going in.

“There was thunderous applause.”
Which is why I was determined to build something magical, something I’d not seen before. While Apple’s own weather app had nice realistic graphics of weather conditions, other apps were trending toward a very minimal interface using a simple vector icon to represent the weather. I wanted to build something that would appear as if you were looking out of a window. I created OpenGL animations for various weather conditions, including a thunderstorm. Not a video, mind you, but computer generated conditions that looked and moved realistically—weather CGI, essentially. Apple rejected it on the grounds that it was too simple: “We encourage you to review your app concept and evaluate whether you can incorporate additional content and features.”

Originally I wanted to test the waters for such an interface, to see if people would like it before I added additional features—but I was willing to play ball. So I added some things I’d planned to hold off until later. The app integrated with your calendar. It showed hourly forecasts with minute-by-minute precision, and beyond. It showed sunrise and sunset with its animations and a nice moon at the correct phase. It would even notify you of inclement weather without you having to lift a finger.

It was also rejected. This time, the reason read: “It is less about a specific quantity of features…Rather, it is about the experience the app provides.” Does this strike anyone as unfair?

Apple states, in legalese:

“Apps should be engaging and exciting, enabling users to do something they couldn’t do before; or to do something in a way they couldn’t do before or better than they could do it before.”
Everyone can get to the weather, that’s a given. But no one had built anything that let you do it this way before. I eventually gave up, though. I suppose I trusted Apple—if they said that no one wanted to see weather in a beautiful realistic animation, then no one wanted to see it.

You might understand my shock when they unveiled a revamped weather app today. And its most defining new feature? Animated weather. Rain fell, snow drifted, hail dropped, and thunderstorms stormed—just as my app had so confidently done months before. And the audience loved it. When the lightning flashed, there was thunderous applause.

I’m not naive enough to claim Apple actually took my idea. I’m sure they happened to be working on a similar concept. I’m just saying they may have unfairly biased the review process, not wishing for someone to debut a key new aspect of their beloved OS before they were able to do so—not wanting anyone to steal their thunder.

According to Apple, no one wanted a flashy weather app. They were so certain of this, they built one themselves.I’ve been a developer for iOS since one could develop for iOS. And I’ve created a lot of apps, some very successful. As such, I’ve had my fair share of rejections, both warranted and unwarranted. I’m not one to complain, but this latest is simply unbearable.

The first app I ever developed is still sitting in iTunes Connect. At the time it was innovative, but the world has moved on. Back before there was “an app for that”—before the most popular sites, even Google, became mobile (or responsive)—there was an app I made called, simply, “Images.”

It did one thing, and it did it well: show you images of whatever you searched for. Essentially, it did what Google Images does now on their mobile-optimized site: show you a text field with large, swipable images below. The idea was, if you were out at a party and didn’t know what a honeybadger looked like, you could get that info to share in as few taps as possible.

Apple rejected it. Back then, you were just rejected, with no rhyme nor reason. You actually had to write in just to request you be given an explanation. I did just that. The reason: porn. Since you could type in anything and get an image for it, you could also type in lewd text and possibly receive an explicit image. Any app that allowed this, they said, would be rejected. Nevermind that you could also go to Google images using the native Safari app and do exactly the same thing.

I fought, but lost. This was a big enough “fuck you” that I swore I’d never write another iPhone app.

The App Store eventually became more transparent and logical with its review process. And I didn’t stop developing iPhone apps for more than a few months: I enjoyed it too much, and knew, for better or worse, that it was the future. That app still sits there, never to see the light of day. It was a lot of work back then, for nothing, but I’ve moved on to create a few successful indie apps.

My latest rejection, however, has me fuming — of a weather app I developed a few months ago. Now, I personally see weather apps, like to-do apps and flashlight apps before them, to be one of those lowest-common-denominator apps. They’re relatively easy to build, so lots of them get built by mediocre developers, and the store gets overrun. I was fully aware of this going in.

“There was thunderous applause.”
Which is why I was determined to build something magical, something I’d not seen before. While Apple’s own weather app had nice realistic graphics of weather conditions, other apps were trending toward a very minimal interface using a simple vector icon to represent the weather. I wanted to build something that would appear as if you were looking out of a window. I created OpenGL animations for various weather conditions, including a thunderstorm. Not a video, mind you, but computer generated conditions that looked and moved realistically—weather CGI, essentially. Apple rejected it on the grounds that it was too simple: “We encourage you to review your app concept and evaluate whether you can incorporate additional content and features.”

Originally I wanted to test the waters for such an interface, to see if people would like it before I added additional features—but I was willing to play ball. So I added some things I’d planned to hold off until later. The app integrated with your calendar. It showed hourly forecasts with minute-by-minute precision, and beyond. It showed sunrise and sunset with its animations and a nice moon at the correct phase. It would even notify you of inclement weather without you having to lift a finger.

It was also rejected. This time, the reason read: “It is less about a specific quantity of features…Rather, it is about the experience the app provides.” Does this strike anyone as unfair?

Apple states, in legalese:

“Apps should be engaging and exciting, enabling users to do something they couldn’t do before; or to do something in a way they couldn’t do before or better than they could do it before.”
Everyone can get to the weather, that’s a given. But no one had built anything that let you do it this way before. I eventually gave up, though. I suppose I trusted Apple—if they said that no one wanted to see weather in a beautiful realistic animation, then no one wanted to see it.

You might understand my shock when they unveiled a revamped weather app today. And its most defining new feature? Animated weather. Rain fell, snow drifted, hail dropped, and thunderstorms stormed—just as my app had so confidently done months before. And the audience loved it. When the lightning flashed, there was thunderous applause.

I’m not naive enough to claim Apple actually took my idea. I’m sure they happened to be working on a similar concept. I’m just saying they may have unfairly biased the review process, not wishing for someone to debut a key new aspect of their beloved OS before they were able to do so—not wanting anyone to steal their thunder.

According to Apple, no one wanted a flashy weather app. They were so certain of this, they built one themselves."""

    language = 'th'
    title = 'ผอ.รพ.ตำรวจยัน ถูกม็อบกปท.ตัดไฟไม่กระทบ'
    text = """เมนูข่าวfanpage ค้นหา<div class="c1">หน้าแรกข่าว> การเมือง> ผอ.รพ.ตำรวจยัน ถูกม็อบกปท.ตัดไฟไม่กระทบ <div style="font-weight:bold;">ผอ.รพ.ตำรวจยัน ถูกม็อบกปท.ตัดไฟไม่กระทบ</div><div class="c2">28 พ.ย. 56 15.54 น. </div><img src="http://p3.isanook.com/ns/0/di/nwpt/sanook-news.jpg" alt="S! News" style="border:none;" />สนับสนุนเนื้อหา <br /><img src="http://pe2.isanook.com/ns/0/ud/266/1334120/2.jpg" alt="ผอ.รพ.ตำรวจยัน ถูกม็อบกปท.ตัดไฟไม่กระทบ" /><br /><p>ผอ.รพ.ตำรวจยืนยัน กปท.บุกตัดไฟสำนักงานตำรวจฯไม่กระทบ เพราะใช้หม้อไฟคนละแปลง</p><p>ผู้สื่อข่าวรายงานว่า (28 พ.ย.) จากเหตุการณ์กลุ่มกองทัพประชาชนโคนล้มระบอบทักษิณ (กปท.) ได้เดินทางมาชุมุนมบริเวณหน้าสำนักงานตำรวจแห่งชาติ (สตช.) โดย<strong style="font-weight:700;">พล.ต.ต.ปิยะ อุทาโย โฆษกศูนย์อำนวยการรักษาความสงบเรียบร้อย (ศอ.รส.)</strong>เปิดเผยว่า สำนักงานตำรวจแห่งชาติและโรงพยาบาลตำรวจถูกตัดไฟ โดยทาง รพ.และ สตช. มีระบบไฟฟ้าสำรองแต่สามารถใช้ได้เพียง 3 ชั่วโมง พร้อมกล่าวว่าการกระทำดังกล่าวถือว่ามีความผิดทางกฎหมาย</p><p>ล่าสุด เมื่อเวลา 15.00 น. <strong style="font-weight:700;">พล.ต.ท.จงเจตน์ อาวเจนพงษ์ ผอ.รพ.ตำรวจ</strong>ยืนยันว่า รพ.ตำรวจไม่ได้รับผลกระทบ เพราะใช้หม้อแปลงคนละตัว แต่ทางสตช.น่าจะถูกตัดไฟ ส่วนที่ใช้ไฟสำรองตอนนี้คือสถาบันนิติเวช ขณะที่ผู้สื่อข่าวของสำนักข่าวเนชั่นรายงานจาก รพ.ตำรวจ พบว่า ไฟฟ้ายังใช้การได้ปกติ ขณะที่กลุ่มผู้ชุมนุม กปท.ยังปักหลักอยู่ที่หน้าสตช.</p><p>ขอขอบคุณข้อมูลจากคุณ @noppatjak/ภาพจากคุณ @Chanida_Sr</p><p>ติดตามข่าวด่วน เกาะกระแสข่าวดัง บน Facebook คลิกที่นี่!!</p></div>
    """

    teaser = PyTeaser(language, title, text)
    print str(teaser.summarize())
