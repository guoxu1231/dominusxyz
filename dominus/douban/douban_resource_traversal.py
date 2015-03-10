__author__ = 'shawguo'

import webapp2
from google.appengine.api import taskqueue
import logging
import requests
from lxml import etree
from dominus.douban.douban_entity import DoubanResourceURL
from dominus.douban.douban_entity import DoubanMovie
from dominus.mongolab.mongolab_rest_wrapper import MONGOLAB_REST_WRAPPER
import re

MOCK_IE_HTTP_HEADER = {}  # TODO
HTTP_TIMIOUT = 20  # 20 seconds
DATASTORE_CHOICE = {"gae": False, "mongolab": True}


class TagEntryHandler(webapp2.RequestHandler):
    """
    Tag first page
        extract first and last 'start' number from pagination link;
        enqueue all tag url to TagURLHandler
    Requrired HTTP Params:
        tag_entry_url = http://movie.douban.com/tag/%E7%A7%91%E5%B9%BB
        kind = movie/book/music
    Example URL
        http://dominusxyz.appspot.com/douban/entry?kind=movie&tag_entry_url=http%3A%2F%2Fmovie.douban.com%2Ftag%2F%25E7%25A7%2591%25E5%25B9%25BB
    Design:
        well-formed website convention over smart crawler
        douban tag & paginator convention
    """
    PAGINATOR_XPATH = {"movie": "/html/body//div[@class='paginator']/a/@href",
                       "music": "TODO",
                       "book": "TODO"}  # TODO configurable?

    def get(self):

        # payload
        kind = self.request.get('kind')
        xpath = self.request.get('xpath')  # TODO
        tag_entry_url = self.request.get('tag_entry_url')
        debug = bool(self.request.get('debug'))  # anything True, blank char False

        # debug = True  # add debug mode
        debug_url = "http://movie.douban.com/tag/%E7%A7%91%E5%B9%BB"
        url = None
        if debug:
            kind = "movie"
            url = debug_url
        else:
            url = tag_entry_url

        assert debug or (kind != "" and tag_entry_url != "")

        try:
            response = requests.get(url, headers=MOCK_IE_HTTP_HEADER, timeout=HTTP_TIMIOUT)
        except BaseException as e:
            logging.error("get douban url %s failed %s" % (url, e))
            self.response.status = 500  # 500 Internal Server Error, Retry the task
            return

        if response.status_code == requests.codes.ok:
            encoding = response.encoding
            text = response.text

            tag_url_list = []
            start_list = []
            max_start = 0
            try:
                parser = etree.HTMLParser(recover=True, encoding=encoding)
                tree = etree.fromstring(text, parser)

                # xpath query
                tag_url_list = tree.xpath(self.PAGINATOR_XPATH[kind])
                # find out max start in paginator url
                for tag_url in tag_url_list:
                    start_list.append(int(re.search('start=(\d+)&type=T', tag_url).group(1)))
                max_start = max(start_list)  # key parameter for following logic
            except BaseException as e:
                logging.error(e)
                self.response.status = 500
                return

            # enqueue push queue
            total = 0
            for paginator_start in range(0, max_start, 20):
                try:
                    tag_url = tag_entry_url + "?start=%d&type=T" % paginator_start
                    taskqueue.add(queue_name='DoubanTagQueue', url='/douban/tag', method="GET",
                                  params={"kind": kind,
                                          "tag_url": tag_url})
                except BaseException as ex:
                    logging.error(
                        "push %s to [DoubanTagQueue] failed: %s" % (tag_url, ex))  # TODO is it possible in GAE?
                    continue
                total += 1

            # viewable results in browser
            self.response.write("[%s] visiable tag url:%d, total tag url:%d" % (kind, len(tag_url_list), total))
            self.response.write("<br>")
            self.response.write("max paginator:%d" % max_start)
            self.response.write("<br>")
            self.response.write(tag_url_list)
            logging.info("[%s] visiable tag url:%d, total tag url:%d, max paginator:%d" % (
                kind, len(tag_url_list), total, max_start))
            logging.info(tag_url_list)

            self.response.status = 200
            return
        else:
            logging.error("get douban url %s failed (status_code=%s)" % (url, response.status_code))
            self.response.status = 500  # 500 Internal Server Error, Retry the task
            return


class CleanupHandler(webapp2.RequestHandler):
    """
        cleanup tag and link push queue
    """

    def get(self):
        print 'wo'


class TagURLHandler(webapp2.RequestHandler):
    """
    Extract multiple resource url from tag url.
    tag list url http://movie.douban.com/tag/%E7%A7%91%E5%B9%BB?start=0&type=T
    Requrired HTTP Params:
        kind = movie/book/music
        tag_url like http://movie.douban.com/tag/%E7%A7%91%E5%B9%BB?start=0&type=T
    """

    RESOURCE_URL_XPATH = {"movie": "/html/body//div[@id='content']//div[@class='article']//a[@class='nbg']/@href",
                          "music": "TODO",
                          "book": "TODO"}  # TODO configurable?

    def get(self):

        # payload
        kind = self.request.get('kind')
        xpath = self.request.get('xpath')  # TODO
        tag_url_2 = self.request.get('tag_url')
        debug = bool(self.request.get('debug'))  # anything True, blank char False

        # debug = True  # add debug mode
        debug_url = "http://movie.douban.com/tag/%E7%A7%91%E5%B9%BB?start=%s&type=T"
        url = None
        if debug:
            kind = "movie"
            url = debug_url
        else:
            url = tag_url_2

        assert debug or (kind != "" and tag_url_2 != "")

        try:
            response = requests.get(url, headers=MOCK_IE_HTTP_HEADER, timeout=HTTP_TIMIOUT)
        except BaseException as e:
            logging.error("get douban url %s failed %s" % (url, e))
            self.response.status = 500  # 500 Internal Server Error, Retry the task
            return

        if response.status_code == requests.codes.ok:
            encoding = response.encoding
            text = response.text

            resource_url_list = []
            try:
                parser = etree.HTMLParser(recover=True, encoding=encoding)
                tree = etree.fromstring(text, parser)

                # xpath query
                resource_url_list = tree.xpath(self.RESOURCE_URL_XPATH[kind])
            except BaseException as e:
                logging.error(e)
                self.response.status = 500
                return

            # viewable results in browser
            self.response.write("[%s] total resource url:%d" % (kind, len(resource_url_list)))
            self.response.write("<br>")
            self.response.write(resource_url_list)
            logging.info("[%s] total resource url:%d" % (kind, len(resource_url_list)))
            logging.info(resource_url_list)

            # put it to datastore
            is_duplicated = False
            ndb = None
            for resource_url in resource_url_list:
                if DATASTORE_CHOICE['gae']:
                    try:
                        ndb = DoubanResourceURL(kind=kind, resource_url=resource_url)
                        # FIXME duplication check by memcache&Resource_URL table
                        if is_duplicated:
                            continue
                        ndb.put()
                    except BaseException as ex:
                        logging.error("Write %s to the datastore error - %s" % (ndb, ex))
                        # FIXME
                        # suspended generator put(context.py:810) raised OverQuotaError(The API call
                        # datastore_v3.Put() required more quota than is available.)

                        # Write DoubanResourceURL(key=Key('douban_resource_url', None),
                        # create_date=datetime.datetime(2015, 2, 13, 14, 30, 13, 867490),
                        # is_debug=True, kind=u'movie', resource_url=u'http://movie.douban.com/subject/1949528/')
                        # to the datastore error - The API call datastore_v3.Put() required more quota than is available.
                elif DATASTORE_CHOICE['mongolab']:
                    try:
                        print "d"
                    except:
                        print 'hl'


            # enqueue push queue
            for resource_url in resource_url_list:
                try:
                    taskqueue.add(queue_name='DoubanResourceQueue', url='/douban/resource', method="GET",
                                  params={"kind": kind, "resource_url": resource_url})
                except BaseException as ex:
                    logging.error("push %s to [DoubanResourceQueue] failed: %s" % (
                        resource_url, ex))  # TODO is it possible in GAE?

            self.response.status = 200
            return
        else:
            logging.error("get douban url %s failed (status_code=%s)" % (url, response.status_code))
            self.response.status = 500  # 500 Internal Server Error, Retry the task
            return


def movie_url_enqueue(kind, url):
    try:
        taskqueue.add(queue_name='DoubanResourceQueue', url='/douban/resource', method="GET",
                      params={'kind': kind, "resource_url": url, 'tag': 'movie'})
    except BaseException as ex:
        logging.warning("push %s to [DoubanLinkQueue] failed: %s" % (url, ex))
        return False


class ResourceURLHandler(webapp2.RequestHandler):
    """
    Fetch content from resource url and extract expected fields.
    """

    def get(self):
        # payload
        resource_url = self.request.get('resource_url')
        kind = self.request.get('kind')
        tag = self.request.get('tag')

        assert resource_url is not None and resource_url != ""
        logging.debug("[ResourceURLHandler]_[%s]_%s" % (kind, resource_url))

        if kind == 'movie':
            movie = DoubanMovie()
            movie.id = int(re.search('start=(\d+)&type=T', resource_url).group(1))
            xpath_extract_movie(movie, resource_url)
            logging.info("[Douban Movie] :%s" % movie)

        self.response.status = 200  # 200 OK


def xpath_extract_movie(movie, resource_url):
    """

    :param movie:
    :param resource_url:
    :return: None = Fatal error
    """
    try:
        response = requests.get(resource_url, headers=MOCK_IE_HTTP_HEADER, timeout=HTTP_TIMIOUT)
    except BaseException as e:
        logging.error("get douban url %s failed %s" % (resource_url, e))
        return None

    if response.status_code == requests.codes.ok:
        encoding = response.encoding
        text = response.text

        try:
            parser = etree.HTMLParser(recover=True, encoding=encoding)
            tree = etree.fromstring(text, parser)
        except BaseException as ex:
            logging.error("get douban url %s failed %s" % (resource_url, ex))
            return None

        #debug
        # print tree.xpath("/html/body//div[@class='subject-others-interests-ft']/a[1]")[0].text

        try:
            movie.title = tree.xpath("/html/body/div[@id='wrapper']/div[@id='content']/h1/span[1]")[0].text
        except BaseException as e:
            movie.sys_debug_msg += "movie.title!!!%s\n" % e
        try:
            movie.year = re.search("\((\d+)\)",tree.xpath("/html/body/div[@id='wrapper']/div[@id='content']/h1/span[2]")[0].text).group(1)
        except BaseException as e:
            movie.sys_debug_msg += "movie.year!!!%s\n" % e
        try:
            movie.average_rating = float(tree.xpath("/html/body/div[@id='wrapper']//div[@class='rating_wrap clearbox']//strong[@class='ll rating_num']")[0].text)
        except BaseException as e:
            movie.sys_debug_msg += "movie.average_rating!!!%s\n" % e
        try:
            movie.ratings_count = int(tree.xpath("/html/body//div[@class='rating_wrap clearbox']/p[2]/a/span[@property='v:votes']")[0].text)
        except BaseException as e:
            movie.sys_debug_msg += "movie.average_rating!!!%s\n" % e
        try:
            movie.wish_count = int(re.search("(\d+).*",tree.xpath("/html/body//div[@class='subject-others-interests-ft']/a[1]")[0].text).group(1)) #FIXME regex
        except BaseException as e:
            movie.sys_debug_msg += "movie.wish_count!!!%s\n" % e
        try:
            movie.collect_count = int(re.search("(\d+).*",tree.xpath("/html/body//div[@class='subject-others-interests-ft']/a[2]")[0].text).group(1)) #FIXME regex
        except BaseException as e:
            movie.sys_debug_msg += "movie.collect_count!!!%s\n" % e

    else:
        return False


def main():
    movie = DoubanMovie()
    resource_url = "http://movie.douban.com/subject/1652587/"
    movie.id = re.search('subject\/(\d+)\/', resource_url).group(1)
    xpath_extract_movie(movie, resource_url)

    print movie




if __name__ == "__main__":
    main()