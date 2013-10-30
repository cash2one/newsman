#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
simplr is a simplified readability implementation in python
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Aug. 4, 2013


import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")

from BeautifulSoup import BeautifulSoup, Comment
from config.settings import logger
import image_helper
import transcoder
import math
import posixpath
import re
import tinysegmenter
import urlparse

import pdb


class Simplr:
    regexps = {
        'unlikely_candidates': re.compile("combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter", re.I),
        'ok_maybe_its_a_candidate': re.compile("and|article|body|column|main|shadow", re.I),
        'positive': re.compile("article|body|content|entry|hentry|main|page|pagination|post|text|blog|story|image", re.I),
        'negative': re.compile("combx|comment|com|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget", re.I),
        'extraneous': re.compile("print|archive|comment|discuss|e[\-]?mail|share|reply|all|login|sign|single", re.I),
        'div_to_p_elements': re.compile("<(a|blockquote|dl|div|img|ol|p|pre|table|ul)", re.I),
        'replace_brs': re.compile("(<br[^>]*>[ \n\r\t]*){2,}", re.I),
        'replace_fonts': re.compile("<(/?)font[^>]*>", re.I),
        'trim': re.compile("^\s+|\s+$", re.I),
        'normalize': re.compile("\s{2,}", re.I),
        'kill_breaks': re.compile("(<br\s*/?>(\s|&nbsp;?)*)+", re.I),
        'videos': re.compile("http://(www\.)?(youtube|vimeo)\.com", re.I),
        'skip_footbote_link': re.compile("^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$", re.I),
        'next_link': re.compile("(next|weiter|continue|>([^\|]|$)|»([^\|]|$))", re.I),
        'prev_link': re.compile("(prev|earl|old|new|<|«)", re.I)
    }

    def __init__(self, url, language):
        """
        docs needed!
        """
        self.candidates = {}
        self.url = url
        self.language = language

        self.data = transcoder.prepare_link(self.url)
        self.data = self.regexps['replace_brs'].sub("</p><p>", self.data)
        self.data = self.regexps['replace_fonts'].sub("<\g<1>span>", self.data)

        self.html = BeautifulSoup(self.data)
        self._remove_script()
        self._remove_style()
        self._remove_link()

        self.title = self._get_title()
        self.short_title = self._get_short_title()
        self.content = self._get_article()
        self.images = self._get_images()

    def _remove_script(self):
        for elem in self.html.findAll("script"):
            elem.extract()

    def _remove_style(self):
        for elem in self.html.findAll("style"):
            elem.extract()

    def _remove_link(self):
        for elem in self.html.findAll("link"):
            elem.extract()

    def _get_images(self):
        if self.content:
            # find_images normalizes images afterwards
            return image_helper.find_images(self.content)
        else:
            return None

    def _get_article(self):
        for elem in self.html.findAll(True):
            unlikely_match_string = elem.get('id', '') + elem.get('class', '')

            if self.regexps['unlikely_candidates'].search(unlikely_match_string) and not self.regexps['ok_maybe_its_a_candidate'].search(unlikely_match_string) and elem.name != 'body':
                elem.extract()
                continue

            if elem.name == 'div':
                s = elem.renderContents(encoding=None)
                if not self.regexps['div_to_p_elements'].search(s):
                    elem.name = 'p'

        for node in self.html.findAll('p'):
            parent_node = node.parent
            grand_parent_node = parent_node.parent
            inner_text = node.text

            if not parent_node or len(inner_text) < 20:
                continue

            parent_hash = hash(str(parent_node))
            grand_parent_hash = hash(str(grand_parent_node))

            if parent_hash not in self.candidates:
                self.candidates[
                    parent_hash] = self._initialize_node(parent_node)

            if grand_parent_node and grand_parent_hash not in self.candidates:
                self.candidates[grand_parent_hash] = self._initialize_node(
                    grand_parent_node)

            content_score = 1
            content_score += inner_text.count(',')
            content_score += inner_text.count(u'，')
            content_score += min(math.floor(len(inner_text) / 100), 3)
            #print content_score, inner_text
            #print

            self.candidates[parent_hash]['score'] += content_score

            if grand_parent_node:
                self.candidates[grand_parent_hash][
                    'score'] += content_score / 2

        top_candidate = None
        #print '-------------------------------------------------'

        for key in self.candidates:
            # the more links and captions it has, the lower score
            self.candidates[key]['score'] = self.candidates[key][
                'score'] * (1 - self._get_link_density(self.candidates[key]['node']))
            if not top_candidate or self.candidates[key]['score'] > top_candidate['score']:
                top_candidate = self.candidates[key]
        #print top_candidate
        #print
        #print '--------------------------------------------------'

        content = ''
        if top_candidate:
            content = top_candidate['node']
            content = self._clean_article(content)
        return content

    def _clean_article(self, content):
        self._clean_comments(content)
        self._clean(content, 'h1')
        self._clean(content, 'object')
        self._clean_conditionally(content, "form")

        if len(content.findAll('h2')) == 1:
            self._clean(content, 'h2')

        self._clean(content, 'iframe')

        self._clean_conditionally(content, "table")
        self._clean_conditionally(content, "ul")
        self._clean_conditionally(content, "div")
        #print 'After removing div'
        #print content
        #print
        #print '---------------------------------------------------------------'
        self._clean_style(content)

        self._fix_images_path(content)

        content = content.renderContents(encoding=None)
        content = self.regexps['kill_breaks'].sub("<br />", content)
        return content

    def _clean(self, e, tag):
        target_list = e.findAll(tag)
        is_embed = 0
        if tag == 'object' or tag == 'embed':
            is_embed = 1

        for target in target_list:
            attribute_values = ""
            for attribute in target.attrs:
                attribute_values += target[attribute[0]]

            if is_embed and self.regexps['videos'].search(attribute_values):
                continue

            if is_embed and self.regexps['videos'].search(target.renderContents(encoding=None)):
                continue
            target.extract()

    def _clean_comments(self, e):
        comments = e.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

    def _clean_style(self, e):
        for elem in e.findAll(True):
            del elem['class']
            del elem['id']
            del elem['style']

    def _clean_conditionally(self, e, tag):
        tags_list = e.findAll(tag)

        new_tags_list = []
        for node in tags_list:
            if node.parent in tags_list:
                continue
            else:
                new_tags_list.append(node)

        for node in new_tags_list:
            weight = self._get_class_weight(node.div)
            hash_node = hash(str(node))
            if hash_node in self.candidates:
                content_score = self.candidates[hash_node]['score']
            else:
                content_score = 0
            #print node

            if weight + content_score < 0:
                node.extract()
            else:
                p = len(node.findAll("p"))
                img = len(node.findAll("img"))
                li = len(node.findAll("li")) - 100
                input = len(node.findAll("input"))
                embed_count = 0
                embeds = node.findAll("embed")
                for embed in embeds:
                    if not self.regexps['videos'].search(embed['src']):
                        embed_count += 1
                link_density = self._get_link_density(node)
                content_length = len(node.text)
                to_remove = False

                if img > p:
                    to_remove = True
                elif li > p and tag != "ul" and tag != "ol":
                    to_remove = True
                elif input > math.floor(p / 3):
                    to_remove = True
                elif content_length < 25 and (img == 0 or img > 2):
                    to_remove = True
                elif weight < 25 and link_density > 0.2:
                    to_remove = True
                #elif weight >= 25 and link_density > 0.5:
                #    to_remove = True
                elif (embed_count == 1 and content_length < 35) or embed_count > 1:
                    to_remove = True

                #print weight, p, img, li, input, link_density, content_length, to_remove
                if to_remove:
                    node.extract()
            #print

    def _get_title(self):
        title = ''
        try:
            title = self.html.find('title').text
        except:
            pass
        return title

    def _get_short_title(self):
        title = ''
        try:
            orig = self.html.find('title').text
            segmenter = tinysegmenter.TinySegmenter()
            # remove unnecessary parts
            for delimiter in [' | ', ' - ', ' :: ', ' / ']:
                if delimiter in orig:
                    parts = orig.split(delimiter)
                    if self.language.startswith('zh') or self.language == 'ja':
                        words_head = segmenter.tokenize(unicode(parts[0]))
                        words_tail = segmenter.tokenize(unicode(parts[-1]))
                        if len(words_head) >= 4:
                            title = parts[0]
                            break
                        elif len(words_tail) >= 4:
                            title = parts[-1]
                            break
                    else:
                        if len(parts[0].split()) >= 4:
                            title = parts[0]
                            break
                        elif len(parts[-1].split()) >= 4:
                            title = parts[-1]
                            break
            if not title:
                orig = title
            if ': ' in orig:
                parts = orig.split(': ')
                if self.language.startswith('zh') or self.language == 'ja':
                    words_tail = segmenter.tokenize(unicode(parts[-1]))
                    if len(words_tail) >= 4:
                        title = parts[-1]
                    else:
                        title = orig.split(': ', 1)[1]
                else:
                    if len(parts[-1].split()) >= 4:
                        title = parts[-1]
                    else:
                        title = orig.split(': ', 1)[1]
            if not title:
                return orig
        except:
            pass
        return title

    def _initialize_node(self, node):
        content_score = 0

        if node.name == 'div':
            content_score += 5
        elif node.name == 'blockquote':
            content_score += 3
        elif node.name == 'form':
            content_score -= 3
        elif node.name == 'th':
            content_score -= 5

        content_score += self._get_class_weight(node)
        return {'score': content_score, 'node': node}

    def _get_class_weight(self, node):
        weight = 0
        if node:
            if node.get('class'):
                if self.regexps['negative'].search(node['class']):
                    weight -= 25
                if self.regexps['positive'].search(node['class']):
                    weight += 25

            if node.get('id'):
                if self.regexps['negative'].search(node['id']):
                    weight -= 25
                if self.regexps['positive'].search(node['id']):
                    weight += 25

        return weight

    def _get_link_density(self, node):
        links = node.findAll('a')
        text_length = len(node.text)

        if text_length == 0:
            return 0
        link_length = 0
        for link in links:
            link_length += len(link.text)

        return link_length / text_length

    def _fix_images_path(self, node):
        imgs = node.findAll('img')
        for img in imgs:
            src = img.get('src', None)
            if not src:
                img.extract()
                continue

            if 'http://' != src[:7] and 'https://' != src[:8]:
                new_src = urlparse.urljoin(self.url, src)

                new_src_arr = urlparse.urlparse(new_src)
                new_path = posixpath.normpath(new_src_arr[2])
                new_src = urlparse.urlunparse(
                    (new_src_arr.scheme, new_src_arr.netloc, new_path,
                     new_src_arr.params, new_src_arr.query,
                     new_src_arr.fragment))
                img['src'] = new_src


def convert(url, language):
    """
    an interface to expose Simplr
    """
    if not url:
        logger.error("Cannot transcode nothing!")
        return None, None, None

    #pdb.set_trace()
    try:
        readable = Simplr(url, language)
        if readable:
            return readable.short_title, readable.content, readable.images
        else:
            logger.info('Simplr cannot parse the data')
            return None, None, None
    except Exception as k:
        logger.error('%s for %s' % (str(k), str(url)))
        return None, None, None
