import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../..')

from config.settings import Collection, db
from config.settings import FEED_REGISTRAR


def _convert(language, country):
    feeds = Collection(db, FEED_REGISTRAR)
    f = open('feed_lists/%s_%s_feed_titles' % (language, country), 'r')
    data = f.readlines()
    f.close()
    for d in data:
        print d
        url, title = d.strip().split('*|*')
        item = feeds.update({'language':language, 'countries':country, 'feed_link':url}, {'$set':{'feed_title':title}})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        _convert(sys.argv[1], sys.argv[2])
    else:
        print 'Please indicate a language and country'
