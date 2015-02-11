__author__ = 'shawguo'

import datetime
import webapp2
from mongolab_rest_wrapper import MONGOLAB_REST_WRAPPER
import logging
from google.appengine.api import memcache


# now = time.strftime("%c")
# print datetime.datetime.utcnow()
# utc_datetime = datetime.datetime.utcnow()
# print datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


class MongolabHeartbeatHandler(webapp2.RequestHandler):
    def get(self):
        heartbeat = {"heartbeat": {"$date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}}
        success = 0
        failed = 0
        try:
            MONGOLAB_REST_WRAPPER.insert_document("shawguo.mongolab_heartbeat", heartbeat)
            logging.debug("mongolab heartbeat success ----- %s" % heartbeat)
            success = MongolabHeartbeatHandler.count_success()
        except BaseException as ex:
            logging.error("mongolab heartbeat failed ------ %s" % ex)
            failed = MongolabHeartbeatHandler.count_failed()
        self.response.write(heartbeat)
        self.response.write("<br>")
        self.response.write("mongolab_heartbeat_success: [%s]%d" % (type(success).__name__, success))
        self.response.write("<br>")
        self.response.write("mongolab_heartbeat_failed: [%s]%d" % (type(failed).__name__, failed))

    @staticmethod
    def count_success():
        return memcache.incr("heartbeat_success", namespace="mongolab", initial_value=0)

    # TODO
    # Keys may be evicted when the cache fills up, according to the cache's LRU policy.
    # Changes in the cache configuration or datacenter maintenance events may also flush some or all of the cache.
    @staticmethod
    def count_failed():
        return memcache.incr("heartbeat_failed", namespace="mongolab", initial_value=0)


class MongolabPurgeHandler(webapp2.RequestHandler):
    def get(self):
        print "no"