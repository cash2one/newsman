#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys

reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')


def main(url, language):
    from processor import simplr

    title, content, images = simplr.convert(url, language)
    #import re
    #a = re.sub(">\s+<", "><", unicode(content))
    from slimmer import html_slimmer

    content = html_slimmer(content)
    print "--------------------------------------------------------------------"
    print str(content)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
