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
import textwrap

# CONSTATNS
from config.settings import CATEGORY_IMAGE_SIZE 
from config.settings import DEFAULT_FONT_PATH
from config.settings import DEFAULT_FONT_SIZE
from config.settings import DEFAULT_TEXT_WIDTH
from config.settings import IMAGES_LOCAL_DIR
from config.settings import IMAGES_PUBLIC_DIR


class Text2Image:
    """
    Converts text into image
    """
    
    def __init__(self, text=None, textimage_relative_path=None, background_color='#FFFFFF', font_color='#000000'):
        if not text or not textimage_relative_path:
            logger.error("Method malformed!")
            
        self._text = text
        self._background_color = background_color
        self._font_color = font_color
        self._textimage_relative_path = textimage_relative_path
        self._image = None
        self._draw = None
        self._font = None

        self._set_background()
        self._set_font_size()
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
    
    def _set_font_size(self):
        """
        set font size on the image
        """
        try:
            img_fraction = 1.7
            self._font = ImageFont.truetype(DEFAULT_FONT_PATH, DEFAULT_FONT_SIZE)

            # adjust font size by text
            while self._font.getsize(self._text)[0] < img_fraction * self._image.size[0]:
                font_size += 1
                self._font = ImageFont.truetype(self.FULL_PATH_TO_FONT, fontsize)
        except Exception as k:
            logger.error(str(k))
    
    def _parse_text(self):
        """
        wrap text by default width
        """
        lines = textwrap.wrap(self._text, DEFAULT_TEXT_WIDTH)
        return lines
    
    def _add_text_to_image(self):
        """
        convert text to image
        """
        lines = self._parse_text()
        try:
            for count, line in enumerate(lines):
                width, height = self._font.getsize(line)
                self._draw.text((0, (count * height) + 2), line, fill=self._font_color, font=self._font)

            textimage_local_path = "%s%s" % (IMAGES_LOCAL_DIR, self._textimage_relative_path)
            self._image.save(textimage_local_path, "PNG")
        except Exception as k:
            logger.error(str(k))
            
    def get_image(self):
        textimage_public_path = "%s%s" % (IMAGES_PUBLIC_DIR, self._textimage_relative_path)
        return textimage_public_path
