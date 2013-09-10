#!/usr/bin/env python 
#-*- coding: utf-8 -*- 

import sys 
reload(sys) 
sys.setdefaultencoding('UTF-8')
sys.path.append("..")

from config.settings import Collection, db
from config.settings import rclient


def _change_field(language):
    """
    change a key/field name in database and memory
    """
    # memory
    id_total = rclient.zcard("news::%s" % language)
    ids = rclient.zrange("news::%s" % language, 0, id_total)

    for id in ids:
        entry_string = rclient.get(id)
        entry_string_new = entry_string.replace('hot_news_image', 'hotnews_image')
        rclient.setex(id, rclient.ttl(id), entry_string_new)

    # database
    col = Collection(db, language)
    col.update({}, {"rename": {"hot_news_image":"hotnews_image"}}, False, True)
    col.update({}, {"rename": {"hot_news_image_local":"hotnews_image_local"}}, False, True)


if __name__ == '__main__':
    language = sys.argv[1]
    _change_field(language)

