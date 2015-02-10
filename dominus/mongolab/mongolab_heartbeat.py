__author__ = 'shawguo'

import datetime
import webapp2
from mongolab_rest_wrapper import MONGOLAB_REST_WRAPPER
import logging


# now = time.strftime("%c")
# print datetime.datetime.utcnow()
# utc_datetime = datetime.datetime.utcnow()
# print datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


class MongolabHeartbeatHandler(webapp2.RequestHandler):
    def get(self):
        heartbeat = {"heartbeat": {"$date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}}
        try:
            MONGOLAB_REST_WRAPPER.insert_document("shawguo.mongolab_heartbeat", heartbeat)
            logging.debug("mongolab heartbeat success ----- %s" % heartbeat)
        except BaseException as ex:
            logging.error("mongolab heartbeat failed ------ %s" % ex)
        self.response.write(heartbeat)