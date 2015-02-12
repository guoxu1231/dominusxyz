__author__ = 'shawguo'
from google.appengine.ext import ndb
import webapp2

# Douban Movie model
# http://developers.douban.com/wiki/?title=movie_v2#subject


class DoubanMovie(ndb.Model):
    # from movie page
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
        return 'movie'


class NDBStoreHandler(webapp2.RequestHandler):
    def get(self):
        movie = DoubanMovie(id="123456")
        # movie.id="123456"
        movie.title = "test movie"

        self.response.write(movie.put())
