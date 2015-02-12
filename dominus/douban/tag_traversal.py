__author__ = 'shawguo'

import webapp2
from google.appengine.api import taskqueue
import logging




# TODO travese specific tag page and extract links from it.
class TagHandler(webapp2.RequestHandler):
    def get(self):
        print "hello"


def link_enqueue(kind, url):
    try:
        taskqueue.add(queue_name='DoubanLinkQueue', url='/douban/link', params={'kind': kind, "url": url})
    except BaseException as ex:
        logging.warning("push %s to [DoubanLinkQueue] failed: %s" % (url, ex))
        return False


# fetch link content and extract expected fields from the url.
class LinkHandler(webapp2.RequestHandler):
    def post(self):
        # payload
        url = self.request.get('url')
        kind = self.request.get('kind')

        logging.debug("[LinkHandler]_[%s]_%s" % (kind, url))
        self.response.status = 200  # 200 OK



        # TODO xpath_extract