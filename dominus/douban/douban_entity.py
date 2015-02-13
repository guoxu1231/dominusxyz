__author__ = 'shawguo'
from google.appengine.ext import ndb
import webapp2


class DoubanMovie(ndb.Model):
    """
    Douban Movie model, from movie page
        http://developers.douban.com/wiki/?title=movie_v2#subject
    """
    id = ndb.StringProperty(required=True, indexed=True)
    title = ndb.StringProperty()
    aka = ndb.StringProperty()
    average_rating = ndb.FloatProperty()
    ratings_count = ndb.IntegerProperty()
    wish_count = ndb.IntegerProperty()
    collect_count = ndb.IntegerProperty()
    mainland_pubdate = ndb.DateTimeProperty()  # TODO
    is_coming = ndb.BooleanProperty(default=False)
    comments_count = ndb.IntegerProperty()
    reviews_count = ndb.IntegerProperty()

    # Sys prop
    # App Engine clock times are always expressed in coordinated universal time (UTC).
    create_date = ndb.DateTimeProperty(auto_now_add=True)
    update_date = ndb.DateTimeProperty(auto_now=True)
    sys_debug_msg = ndb.StringProperty()

    @classmethod
    def _get_kind(cls):
        return 'douban_movie'


class DoubanResourceURL(ndb.Model):
    """
    Movie/Book/Music URL
    """
    kind = ndb.StringProperty()
    resource_url = ndb.StringProperty(indexed=True)
    create_date = ndb.DateTimeProperty(auto_now_add=True)
    is_debug = ndb.BooleanProperty(default=True)

    @classmethod
    def _get_kind(cls):
        return 'douban_resource_url'


class DoubanTagURL(ndb.Model):
    """
    Movie/Book/Music Tag URL
    """
    kind = ndb.StringProperty()
    tag_url = ndb.StringProperty(indexed=True)
    create_date = ndb.DateTimeProperty(auto_now_add=True)
    is_debug = ndb.BooleanProperty(default=True)

    @classmethod
    def _get_kind(cls):
        return 'douban_tag_url'


class NDBStoreHandler(webapp2.RequestHandler):
    def get(self):
        movie = DoubanMovie()
        movie.id = "123456"
        movie.title = "test movie"

        self.response.write(movie.put())
