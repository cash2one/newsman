#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append('..')


def main(url, language):
    from data_processor import simplr
    print simplr.convert(url, language)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
