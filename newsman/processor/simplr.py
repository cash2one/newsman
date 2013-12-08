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
import codecs
from config.settings import logger
from furl import furl
import illustrator
import transcoder
import math
import posixpath
import re
import tinysegmenter
import urlparse

# CONSTANTS
HIDDEN_IMAGE = {
    'http://sankei.jp.msn.com/': ('div', {'class': 'img250 imgright'}), 'http://www.cnn.co.jp/': ('div', {'id': 'leaf_large_image', 'class': 'img-caption'}),
    'http://news.goo.ne.jp/': ('p', {'class': 'imager'}), 'http://jp.reuters.com/': ('td', {'id': "articlePhoto", 'class': "articlePhoto"})}


class Simplr:
    regexps = {
        'unlikely_candidates': re.compile("banner|button|combx|comment|community|copyright|disqus|extra|foot|header|menu|remark|rss|poll|shoutbox|sidebar|sponsor|sns|ad-break|agegate|pagination|pager|popup|posted|pr|tweet|twitter", re.I),
        'ok_maybe_its_a_candidate': re.compile("and|article|body|column|content|main|post|shadow", re.I),
        'positive': re.compile("article|blog|body|content|entry|hentry|image|main|page|pagination|photo|post|story|text", re.I),
        'negative': re.compile("banner|combx|comment|com|contact|foot|footer|footnote|genre|logo|masthead|media|meta|outbrain|poll|pr|promo|ranking|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget|link", re.I),
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
        try:
            self.candidates = {}
            self.url = url
            self.language = language

            self.data = transcoder.prepare_link(self.url)
            self.data = self.regexps['replace_brs'].sub(
                "</p><p>", str(self.data))
            self.data = self.regexps['replace_fonts'].sub(
                "<\g<1>span>", str(self.data))

            self.html = BeautifulSoup(self.data)
            self._remove_script()
            self._remove_style()
            self._remove_link()

            self.title = self._get_title()
            self.short_title = self._get_short_title()
            self.content = self._get_article()
            self.images = self._get_images()
        except Exception as k:
            logger.error(str(k))

    def _remove_script(self):
        try:
            for elem in self.html.findAll("script"):
                elem.extract()
        except Exception as k:
            logger.error(str(k))

    def _remove_style(self):
        try:
            for elem in self.html.findAll("style"):
                elem.extract()
        except Exception as k:
            logger.error(str(k))

    def _remove_link(self):
        try:
            for elem in self.html.findAll("link"):
                elem.extract()
        except Exception as k:
            logger.error(str(k))

    def _get_images(self):
        try:
            if self.content:
                # find_images normalizes images afterwards
                images, content_new = illustrator.find_images(
                    self.content, self.url)
                if content_new and content_new != self.content:
                    self.content = content_new
                return images
            else:
                return None
        except Exception as k:
            logger.error(str(k))
            return None

    def _get_article(self):
        try:
            _ignored_image = None

            for elem in self.html.findAll(True):
                unlikely_match_string = elem.get(
                    'id', '') + elem.get('class', '')

                if self.regexps['unlikely_candidates'].search(unlikely_match_string) and not self.regexps['ok_maybe_its_a_candidate'].search(unlikely_match_string) and elem.name != 'body':
                    # print elem
                    # print self.regexps['unlikely_candidates'].findall(unlikely_match_string)
                    # print 'id', elem.get('id') if elem.get('id') else None
                    # print 'class', elem.get('class') if elem.get('class') else None
                    # print '++++++++++++++++++++++++++++++++++++++++++++'
                    # print
                    # print
                    elem.extract()
                    continue

                # remove site-specific segments
                if self.url.startswith('http://community.travel.yahoo.co.jp/') and re.compile('pt02|pt10', re.I).search(unlikely_match_string):
                    elem.extract()
                    continue

                if self.url.startswith('http://news.nifty.com/') and re.compile('pr|banner', re.I).search(unlikely_match_string):
                    elem.extract()
                    continue

                if 'kapook.com' in self.url and elem.name == 'table':
                    # if elem.get('bordercolor') and elem.get('bordercolor') == '#FF0000':
                    # print elem
                    # print '&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                    # print
                    elem.extract()
                    continue

                if elem.name == 'div':
                    s = elem.renderContents(encoding=None)
                    if not self.regexps['div_to_p_elements'].search(s):
                        elem.name = 'p'
                    else:
                        if 'kapook.com' in self.url:
                            if elem.get('align') and (elem.get('align') == 'center' or elem.get('align') == 'left'):
                                # print elem
                                # print '+++++++++++++++++++++++++++++++++++'
                                # print
                                elem.name = 'p'
                else:
                    if self.url.startswith('http://jp.reuters.com/'):
                        if elem.get('id') and elem.get('id') == 'articlePhoto':
                            elem.name = 'p'
                            _ignored_image = elem
                    elif 'kapook.com' in self.url:
                        if elem.parent.name == 'div':
                            if elem.name == 'img' and elem.parent.get('id') and (elem.parent.get('id') == 'article' or elem.parent.get('id') == 'container2'):
                                elem.name = 'p'
                                # print elem
                                # print elem.parent
                                # print "**********************"
                                # print
                            else:
                                # print elem
                                # print elem.parent.attrs
                                # print "**********************"
                                # print
                                pass

            for node in self.html.findAll('p'):
                parent_node = node.parent
                grand_parent_node = parent_node.parent
                inner_text = node.text
                # print node
                # print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
                # print

                if not parent_node or len(inner_text) < 20:
                    continue

                parent_hash = hash(str(parent_node))
                grand_parent_hash = hash(str(grand_parent_node))

                if parent_hash not in self.candidates:
                    self.candidates[
                        parent_hash] = self._initialize_node(parent_node)
                    # print 'pn-class', parent_hash, parent_node.get('class'), self._get_class_weight(parent_node)
                    # print 'pn-id', parent_hash, parent_node.get('id'),
                    # self._get_class_weight(parent_node)

                if grand_parent_node and grand_parent_hash not in self.candidates:
                    self.candidates[grand_parent_hash] = self._initialize_node(
                        grand_parent_node)
                    # print 'gpn-class', grand_parent_hash, grand_parent_node.get('class'), self._get_class_weight(grand_parent_node)
                    # print 'gpn-id', grand_parent_hash,
                    # grand_parent_node.get('id'),
                    # self._get_class_weight(grand_parent_node)

                content_score = 1
                content_score += inner_text.count(',')
                content_score += inner_text.count(u'，')
                #content_score += inner_text.count('、')
                #content_score += inner_text.count(u'、')
                content_score += min(math.floor(len(inner_text) / 100), 3)
                # print content_score, node
                # print 'OLD %s %s  Parent' % (self.candidates[parent_hash]['score'], parent_hash)
                # print 'OLD %s %s  Grand' %
                # (self.candidates[grand_parent_hash]['score'], grand_parent_hash)
                self.candidates[parent_hash]['score'] += content_score

                if grand_parent_node:
                    self.candidates[grand_parent_hash][
                        'score'] += content_score * 0.7

                # print 'NEW %s %s  Parent' % (self.candidates[parent_hash]['score'], parent_hash)
                # print 'NEW %s %s  Grand' % (self.candidates[grand_parent_hash]['score'], grand_parent_hash)
                # print '@@@@@'
                # print

            top_candidate = None
            for key in self.candidates:
                # the more links and captions it has, the lower score
                self.candidates[key]['score'] = self.candidates[key][
                    'score'] * (1 - self._get_link_density(self.candidates[key]['node']))
                if not top_candidate or self.candidates[key]['score'] > top_candidate['score']:
                    top_candidate = self.candidates[key]

            content = ''
            if top_candidate:
                content = top_candidate['node']
                if _ignored_image and not content.find('img'):
                    if self.url.startswith('http://jp.reuters.com/'):
                        content.insert(0, _ignored_image)
                # print 'Top Candidate'
                # print content
                # print
                # print
                # '------------------------------------------------------------'

                content = self._clean_article(content)

            return content
        except Exception as k:
            logger.error(str(k))

    def _clean_article(self, content):
        try:
            self._clean_comments(content)
            self._clean(content, 'h1')
            self._clean(content, 'object')
            self._clean_conditionally(content, "form")

            if len(content.findAll('h2')) == 1:
                self._clean(content, 'h2')

            self._clean(content, 'iframe')

            self._clean_conditionally(content, "table")
            self._clean_conditionally(content, "ul")
            # print 'Before removing div'
            # print content
            # print
            # print
            # '----------------------------------------------------------------'
            self._clean_conditionally(content, "div")
            # print 'After removing div'
            # print content
            # print
            # print
            # '----------------------------------------------------------------'
            self._clean_style(content)

            self._fix_images_path(content)
            self._fix_links_path(content)

            # image retriver
            article_image = None
            matched_link = [
                link for link in HIDDEN_IMAGE if self.url.startswith(link)]
            if matched_link:
                html_tag, html_attrs = HIDDEN_IMAGE[matched_link[0]]
                found_image = content.find(name=html_tag, attrs=html_attrs)
                if not found_image:
                    article_image = self.html.find(
                        name=html_tag, attrs=html_attrs)
                    if article_image:
                        self._fix_images_path(article_image)
                        self._fix_links_path(article_image)

            content = content.renderContents(encoding=None)
            if article_image:
                article_image = article_image.renderContents(encoding=None)
                content = article_image + content
            content = self.regexps['kill_breaks'].sub("<br />", content)
            return content
        except Exception as k:
            logger.error(str(k))
            return None

    def _clean(self, e, tag):
        try:
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
        except Exception as k:
            logger.error(str(k))

    def _clean_comments(self, e):
        try:
            comments = e.findAll(text=lambda text: isinstance(text, Comment))
            [comment.extract() for comment in comments]
        except Exception as k:
            logger.error(str(k))

    def _clean_style(self, e):
        try:
            for elem in e.findAll(True):
                del elem['class']
                del elem['id']
                del elem['style']
        except Exception as k:
            logger.error(str(k))

    def _clean_conditionally(self, e, tag):
        try:
            tags_list = e.findAll(tag)

            new_tags_list = []
            for node in tags_list:
                if node.parent in tags_list:
                    continue
                else:
                    new_tags_list.append(node)

            for node in new_tags_list:
                weight = self._get_class_weight(node)
                hash_node = hash(str(node))
                if hash_node in self.candidates:
                    content_score = self.candidates[hash_node]['score']
                else:
                    content_score = 0
                # print node

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
                    # elif weight >= 25 and link_density > 0.5:
                    #    to_remove = True
                    elif (embed_count == 1 and content_length < 35) or embed_count > 1:
                        to_remove = True

                    # print weight, p, img, li, input, link_density,
                    # content_length, to_remove
                    if to_remove:
                        node.extract()
                # print
        except Exception as k:
            logger.error(str(k))

    def _get_title(self):
        try:
            title = ''
            try:
                title = self.html.find('title').text
            except:
                pass
            return title
        except Exception as k:
            logger.error(str(k))
            return None

    def _get_short_title(self):
        try:
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
        except Exception as k:
            logger.error(str(k))
            return None

    def _initialize_node(self, node):
        try:
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
        except Exception as k:
            logger.error(str(k))
            return None

    def _get_class_weight(self, node):
        try:
            weight = 0
            if node:
                if node.get('class'):
                    if self.regexps['negative'].search(node['class']):
                        # print 'no-1'
                        weight -= 25
                    if self.regexps['positive'].search(node['class']):
                        # print 'yes-1'
                        weight += 25

                if node.get('id'):
                    if self.regexps['negative'].search(node['id']):
                        # print 'no-2'
                        weight -= 25
                    if self.regexps['positive'].search(node['id']):
                        # print 'yes-2'
                        weight += 25

            return weight
        except Exception as k:
            logger.error(str(k))
            return 0

    def _get_link_density(self, node):
        try:
            links = node.findAll('a')
            text_length = len(node.text)

            if text_length == 0:
                return 0
            link_length = 0
            for link in links:
                link_length += len(link.text)

            return float(link_length) / float(text_length)
        except Exception as k:
            logger.error(str(k))
            return 0

    def _fix_links_path(self, node):
        try:
            atags = node.findAll('a')
            for atag in atags:
                href = atag.get('href', None)
                if not href:
                    atag.extract()
                    continue

                if 'http://' != href[:7] and 'https://' != href[:8]:
                    new_href = urlparse.urljoin(self.url, href)

                    new_href_arr = urlparse.urlparse(new_href)
                    new_path = posixpath.normpath(new_href_arr[2])
                    new_href = urlparse.urlunparse(
                        (new_href_arr.scheme, new_href_arr.netloc, new_path,
                         new_href_arr.params, new_href_arr.query,
                         new_href_arr.fragment))
                    atag['href'] = new_href
        except Exception as k:
            logger.error(str(k))

    def _fix_images_path(self, node):
        try:
            imgs = node.findAll('img')
            for img in imgs:
                src = img.get('src', None)
                if not src:
                    img.extract()
                    continue

                # remove width or height attributes
                from copy import copy
                attrs = copy(img.attrs)
                for attr in attrs:
                    if attr[0] == 'width' or attr[0] == 'height':
                        img.attrs.remove(attr)
                attrs = None
                del attrs

                if 'http://' != src[:7] and 'https://' != src[:8]:
                    new_src = urlparse.urljoin(self.url, src)

                    new_src_arr = urlparse.urlparse(new_src)
                    new_path = posixpath.normpath(new_src_arr[2])
                    new_src = urlparse.urlunparse(
                        (new_src_arr.scheme, new_src_arr.netloc, new_path,
                         new_src_arr.params, new_src_arr.query,
                         new_src_arr.fragment))
                    img['src'] = new_src

                # optimization made for asahi.com
                if 'asahicom.jp' in img['src'] and img['src'].endswith('_commL.jpg'):
                    img['src'] = img['src'].replace('_commL.jpg', '_comm.jpg')

                # optimization made for excite.co.jp
                if 'image.excite.co.jp' in img['src'] and img['src'].endswith('_s.jpg'):
                    img['src'] = img['src'].replace('_s.jpg', '.jpeg')

                # optimization made for news.goo.ne.jp
                if 'img.news.goo.ne.jp' in img['src'] and img['src'].endswith('.jpg'):
                    img['src'] = img['src'].replace('/s_', '/m_')

                # optimization made for img.mainichi.jp
                if 'img.mainichi.jp' in img['src'] and img['src'].endswith('.jpg'):
                    if self.url.startswith('http://mainichi.jp'):
                        f = furl(self.url)
                        # 20131201k0000m040041000c
                        mainichi_id = str(f.path).split('/')[-1][:-5]
                        mainichi_year = mainichi_id[:4]
                        mainichi_month = mainichi_id[4:6]
                        mainichi_day = mainichi_id[6:8]
                        img['src'] = "http://mainichi.jp/graph/%s/%s/%s/%s/image/001.jpg" % (
                            mainichi_year, mainichi_month, mainichi_day, mainichi_id)

                # optimization made for sankei.jp.msn.com
                if 'sankei.jp.msn.com' in img['src']:
                    if img['src'].endswith('-n1.jpg'):
                        img['src'] = img['src'].replace('-n1.jpg', '-p1.jpg')
                    elif img['src'].endswith('-s1.jpg'):
                        img['src'] = img['src'].replace('-s1.jpg', '-p1.jpg')

                # optimization made for jp.reuters.com
                if 's1.reutersmedia.net/resources/r/' in img['src']:
                    f = furl(img['src'])
                    if 'll' in f.args:
                        del f.args['ll']
                    if 'pl' in f.args:
                        del f.args['pl']
                    if 'fw' in f.args:
                        del f.args['fw']
                    if 'fh' in f.args:
                        del f.args['fh']
                    if 'w' in f.args:
                        del f.args['w']
                    if f.url.startswith(codecs.BOM_UTF8):
                        img['src'] = f.url[3:]
                    else:
                        img['src'] = f.url
        except Exception as k:
            logger.error(str(k))


def convert(url, language):
    """
    an interface to expose Simplr
    """
    if not url:
        logger.error("Cannot transcode nothing!")
        return None, None, None

    # pdb.set_trace()
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
