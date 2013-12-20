#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
text2img converts text into an image
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Nov. 15, 2013


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import chardet
from config.settings import logger
from PIL import Image, FontFile, ImageFont, ImageDraw
import nltk
import re
import subprocess
import textwrap
import tinysegmenter

# CONSTATNS
from config.settings import CATEGORY_IMAGE_SIZE
from config.settings import DATA_PATH
from config.settings import FONT_PATH_EN
from config.settings import FONT_PATH_IN
from config.settings import FONT_PATH_JA
from config.settings import FONT_PATH_PT
from config.settings import FONT_PATH_TH
from config.settings import FONT_PATH_ZH
from config.settings import IMAGES_LOCAL_DIR
from config.settings import IMAGES_PUBLIC_DIR
from config.settings import TEXT_WIDTH_EN
from config.settings import TEXT_WIDTH_IN
from config.settings import TEXT_WIDTH_JA
from config.settings import TEXT_WIDTH_PT
from config.settings import TEXT_WIDTH_TH
from config.settings import TEXT_WIDTH_ZH
from config.settings import THAI_WORDSEG
from config.settings import THAI_WORDSEG_DICT


class Text2Image:

    """
    Converts text into image
    """

    def __init__(self, language=None, text=None, textimage_relative_path=None, background_color='#000000', font_color='#FFFFFF'):
        if not language or not text or not textimage_relative_path:
            logger.error("Method malformed!")

        self._language = language
        self._text = text
        self._background_color = background_color
        self._font_color = font_color
        self._textimage_relative_path = textimage_relative_path
        self._font_size = 1
        self._image = None
        self._draw = None
        self._font = None

        # danamic loading specific import
        FONT_PATH = 'FONT_PATH_%s' % self._language.upper()
        TEXT_WIDTH = 'TEXT_WIDTH_%s' % self._language.upper()
        self._font_path = eval(FONT_PATH)
        self._text_width = eval(TEXT_WIDTH)

        self._set_background()
        self._add_text_to_image()

    def _set_background(self):
        """
        set the image background
        """
        try:
            #self._image = Image.new("RGB", CATEGORY_IMAGE_SIZE, self._background_color)
            self._image = Image.open("%s/home_bg.png" % DATA_PATH)
            self._draw = ImageDraw.Draw(self._image)
        except Exception as k:
            logger.error(str(k))
            return None

    def _set_font_size(self, line=None):
        """
        set font size on the image
        """
        if not line:
            logger.error("Method malformed!")
            return None

        try:
            img_fraction = 0.67
            self._font = ImageFont.truetype(self._font_path, self._font_size)

            # adjust font size by text
            while self._font.getsize(line)[0] < img_fraction * self._image.size[0]:
                self._font_size = self._font_size + 1
                # print self._font_size, self._font.getsize(line)[0]
                self._font = ImageFont.truetype(
                    self._font_path, self._font_size)
        except Exception as k:
            logger.error(str(k))
            return None

    def _parse_text(self):
        """
        use nltk or other engines to split text into sentences
        """
        try:
            sentences = []

            # convert to appropriate encoding
            if isinstance(self._text, str):
                self._text = self._text.decode(
                    chardet.detect(self._text)['encoding'], 'ignore')

            # special: thai, arabic
            if self._language == 'zh':
                cj_punctuation = u"""-|〃|。|．|\.|!|！|\?|？|、|-|〟|〰|-|-|＊|，|,|-|／|：|-|；|-|-|＿|-|･|‐|-|―|-|…|-|‧|﹏"""
                sentences = re.split(cj_punctuation, self._text)
            if self._language == 'ja':
                segmenter = tinysegmenter.TinySegmenter()
                sentences = segmenter.tokenize(self._text)
                sentences = [
                    sentence for sentence in sentences if sentence.strip()]
            elif self._language == 'th':
                if self._text and self._text.strip():
                    try:
                        # preprocess text - remove single quote
                        if self._text.count('"') % 2:
                            self._text = self._text.replace('"', '')
                        command = '''echo \"%s\" | %s %s/scw.conf %s 2>/dev/null''' % (
                            str(self._text.strip().lower()), THAI_WORDSEG, THAI_WORDSEG_DICT, THAI_WORDSEG_DICT)
                        response = subprocess.Popen(
                            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        content, error = response.communicate()
                        if not error and content:
                            if 'error' not in content or 'permission' not in content:
                                content = content.strip()
                                paragraphs = [paragraph.strip()
                                              for paragraph in content.split('\n') if paragraph.strip()]
                                for paragraph in paragraphs:
                                    # modes[0]: the orginal [1]: phrase seg
                                    # [2]: basic wordseg [3]: subphrase seg
                                    modes = [mode.strip()
                                             for mode in paragraph.split('\t') if mode.strip()]
                                    # for mode in modes:
                                    #    print  str(mode)
                                    # u'|' is very crucial(, instead of '|')
                                    if len(modes) > 2:
                                        sentences.extend(
                                            [sentence for sentence in modes[2].split(u'|') if sentence])
                        elif error:
                            raise Exception(
                                '%s over %s' % (str(error), str(self._text.strip())))
                    except Exception as k:
                        logger.error(
                            'Problem [%s] for [%s]' % (str(k), str(self._text)))
            else:  # latin-based
                sentences = nltk.sent_tokenize(self._text)

            # remove void lines
            if sentences:
                sentences = [sentence.strip()
                             for sentence in sentences if sentence.strip()]

            if self._language in ['en', 'in', 'pt', 'ja', 'zh', 'th']:
                lines = []
                for sentence in sentences:
                    splits = textwrap.wrap(sentence, self._text_width)
                    # print str(' | '.join(splits))
                    lines.extend(splits)

                sentences = []
                previous_line = None
                for index in xrange(len(lines)):
                    current_line = lines[index]
                    # print str(current_line)
                    if previous_line:
                        # print '  previous', str(previous_line)
                        possible_line = ""
                        if self._language in ['en', 'in', 'pt']:
                            possible_line = u"%s %s" % (
                                previous_line, current_line)
                        else:
                            possible_line = u"%s%s" % (
                                previous_line, current_line)

                        if len(textwrap.wrap(possible_line, self._text_width)) == 1:
                            # print '    possible', str(possible_line)
                            previous_line = possible_line
                        else:
                            # print '    no possible', str(current_line)
                            sentences.append(previous_line)
                            previous_line = current_line
                    else:
                        # print '  no previous', str(current_line)
                        previous_line = current_line
                    # if current_line is the last one, add it to list
                    if index + 1 == len(lines):
                        sentences.append(previous_line)

            # print
            # for s in sentences:
            #    print '*', str(s)
            return sentences
        except Exception as k:
            logger.error(str(k))
            return None

    def _add_text_to_image(self):
        """
        convert text to image
        """
        sentences = self._parse_text()
        # pick up the longest sentence
        # length evaluation should be done in str, not unicode
        longest_sentence = max([(len(str(sentence)), index)
                               for index, sentence in enumerate(sentences)], key=lambda x: x[0])
        # print '[longest sentence]', str(sentences[longest_sentence[1]])
        # longest_sentence: (sentence_length, sentence_index)
        self._set_font_size(sentences[longest_sentence[1]])

        try:
            for count, sentence in enumerate(sentences):
                width, height = self._font.getsize(sentence)
                if ((count + 2) * height + 30 + count * 16) > self._image.size[1]:
                    sentence = ". . . . . ."
                    self._draw.text(((self._image.size[0] - 30) / 2 - self._font.getsize(sentence)[0] / 2, (
                        (count - 1) * height) + 30 + height / 2 + count * 8), sentence, fill=self._font_color, font=self._font)
                    break
                else:
                    # print str(sentence)
                    self._draw.text(
                        (40, (count * height) + 30 + count * 8), sentence, fill=self._font_color, font=self._font)

            textimage_local_path = "%s%s" % (
                IMAGES_LOCAL_DIR, self._textimage_relative_path)
            # print textimage_local_path
            self._image.save(textimage_local_path, "PNG")
        except Exception as k:
            logger.error(str(k))

    def get_image(self):
        try:
            textimage_public_path = "%s%s" % (
                IMAGES_PUBLIC_DIR, self._textimage_relative_path)
            textimage = {'url': textimage_public_path, 'width':
                         CATEGORY_IMAGE_SIZE[0], 'height': CATEGORY_IMAGE_SIZE[1]}
            return textimage
        except Exception as k:
            logger.error(str(k))
            return None


if __name__ == "__main__":
    #language = 'en'
    #text = "House defies Obama health plan fixes, blurs party lines"
    #text = "The bank reached the agreement with 21 institutional investors in 330 residential mortgage-backed securities trusts issued by JPMorgan and Bear Stearns, which it took over during the financial crisis, according to the bank and lawyers for the investors."

    #language = 'ja'
    #text = "日印との関係重視、ブータン首相インタビュー…中国と国交樹立急がず"
    #text = "親日国として知られるブータンのツェリン・トブゲイ首相（４８）が５日、首都ティンプーの首相府で産経新聞の単独インタビューに応じ、日本と隣国インドとの関係を重視していく方針を強調した。国境問題を抱える中国との早期の国交樹立については、否定的な見解を示した。"

    #language = 'zh'
    #text = "延迟退休将渐进实现 不会“一夜涨5岁”"
    #text = "人民网北京11月15日电 十八届三中全会审议通过了《中共中央关于全面深化改革若干重大问题的决定》,《决定》今日全文播发。"

    #language = 'th'
    #text = "ผบ.สส. ชี้ คำพิพากษาศาลโลก ต้องเข้าสภาฯ ก่อนถกเขมร ยัน ไม่ใช้แผนที่ 1/200,000 กำหนดบริเวณพื้นที่ใกล้ปราสาทพระวิหาร"

    language = 'pt'
    text = "Este resultado é explicado depois de a Avianca Holdings S.A. alcançar, no período julho-setembro de 2013, um lucro líquido ajustado de R$ 230,17 milhões (US$ 99,1 milhões), disse a companhia em um comunicado."

    # print str(text)
    test = Text2Image(language, text, "test1.png", "#000000", "#FFFFFF")
    test.get_image()
