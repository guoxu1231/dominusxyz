__author__ = 'shawguo'

import webapp2
from google.appengine.ext import ndb
import logging
import urllib


class WifiPasswordHandler(webapp2.RequestHandler):
    """
        intranet shell post wifi password and will be handled by this handler
            post: save password and misc info;
            get: query latest wifi password;
    """

    def get(self):
        q = ndb.gql("SELECT * FROM wifi_password order by create_date desc limit 1")

        # cookies analytics
        cookies = self.request.headers.get("Cookie")
        if cookies is not None:
            cookies = urllib.unquote(cookies).decode('utf8')
            logging.info("[Cookies Analytics] " + cookies)

        for p in q:
            self.response.write(p.password)
        self.response.status = 200

        return

    def post(self):
        password = self.request.get('wifi_password')
        remote_address = (self.request.remote_addr if self.request else '')
        assert password != ""

        ndbObject = WifiPassword()
        ndbObject.password = password
        ndbObject.from_ip = remote_address
        ndbObject.put()

        logging.info(ndbObject)
        self.response.write(ndbObject)
        self.response.status = 200


class WifiPassword(ndb.Model):
    password = ndb.StringProperty(required=True, indexed=False)
    from_ip = ndb.StringProperty(indexed=False)
    user_agent = ndb.StringProperty(indexed=False)
    create_date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def _get_kind(cls):
        return 'wifi_password'