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

from config.settings import logger
from PIL import Image, FontFile, ImageFont, ImageDraw
import nltk
import textwrap

# CONSTATNS
from config.settings import CATEGORY_IMAGE_SIZE 
from config.settings import DEFAULT_FONT_PATH
from config.settings import IMAGES_LOCAL_DIR
from config.settings import IMAGES_PUBLIC_DIR


class Text2Image:
    """
    Converts text into image
    """
    
    def __init__(self, language=None, text=None, textimage_relative_path=None, background_color='#FFFFFF', font_color='#000000'):
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

        self._set_background()
        self._add_text_to_image()
        
    def _set_background(self):
        """
        set the image background
        """
        try:
            self._image = Image.new("RGB", CATEGORY_IMAGE_SIZE, self._background_color)
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
            img_fraction = 0.85
            self._font = ImageFont.truetype(DEFAULT_FONT_PATH, self._font_size)

            # adjust font size by text
            while self._font.getsize(line)[0] < img_fraction * self._image.size[0]:
                self._font_size += 1
                self._font = ImageFont.truetype(DEFAULT_FONT_PATH, self._font_size)
        except Exception as k:
            logger.error(str(k))
            return None
    
    def _parse_text(self):
        """
        use nltk or other engines to split text into sentences
        """
        try:
            sentences = None
            # special: thai, arabic
            if self._language == 'zh' or self._language == 'ja':
                cj_sent_tokenizer = nltk.RegexpTokenizer(
                    u'[^!?.！？。．]*[!?、.！？。]*')
                sentences = cj_sent_tokenizer.tokenize(self._text)
            elif self._language == 'th':
                sentences = self._text.split()
            else:  # latin-based
                sentences = nltk.sent_tokenize(self._text)

            sentences = [sentence.strip()
                         for sentence in sentences if sentence.strip()]

            if self._language in ['en', 'in', 'pt']:
                lines = []
                for sentence in sentences:
                    splits = textwrap.wrap(sentence, 25)
                    lines.extend(splits)

                sentences = []
                for index in xrange(len(lines)):
                    if index + 1 < len(lines):
                        possible = "%s %s" % (lines[index], lines[index + 1])
                        if len(textwrap.wrap(possible, 25)) == 1:
                            sentences.append(possible)  
                        else:
                            sentences.append(lines[index])
            return sentences
        except Exception as k:
            logger.error(str(k))
            return None

    def _add_text_to_image(self):
        """
        convert text to image
        """
        lines = self._parse_text()
        self._set_font_size(lines[0])

        try:
            for count, line in enumerate(lines):
                width, height = self._font.getsize(line)
                if ((count + 2) * height + height + 20) > self._image.size[1]:
                    line = "......"
                    self._draw.text((self._image.size[0] / 2 - 20, ((count + 1) * height) + 10), line, fill=self._font_color, font=self._font)
                    break
                else:
                    print text
                    self._draw.text((15, ((count + 1) * height) + 10), line, fill=self._font_color, font=self._font)

            textimage_local_path = "%s%s" % (IMAGES_LOCAL_DIR, self._textimage_relative_path)
            self._image.save(textimage_local_path, "PNG")
        except Exception as k:
            logger.error(str(k))
            
    def get_image(self):
        textimage_public_path = "%s%s" % (IMAGES_PUBLIC_DIR, self._textimage_relative_path)
        return textimage_public_path


if __name__ == "__main__":
    #language = 'en'
    #text = "skdfjasldkfjadsl;fjads, sdfksodfksdf. jsidfjo. Typhoon-hit town that saw less death but all the destruction feels forgotten as aid passes by"

    language = 'ja'
    text = u"日印との関係重視、ブータン首相インタビュー…中国と国交樹立急がず"
    test = Text2Image(language, text, "test1.png")
    test.get_image()
