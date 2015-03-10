__author__ = 'shawguo'

from datetime import date
from datetime import datetime
import logging
import webapp2
import json
import traceback
from google.appengine.api import urlfetch
from lxml import etree
from google.appengine.api import taskqueue
from dominus.google_api import get_google_calendar_service
from dominus.google_api import DOUBAN_CALENDAR_ID
from dominus.douban.douban_resource_traversal import movie_url_enqueue


# ComingMovieV2Handler
#   Using Push Queues to handle delete/insert events and avoid HTTP 403 error
#   (probably caused by exceeding GAE resource quota limiation)

class ComingMovieV2Handler(webapp2.RequestHandler):

    DOUBAN_URL = "http://movie.douban.com/coming"
    # chinese unicode encoding
    YEAR_CODE = u"\u5e74"
    DAY_CODE = u"\u65e5"
    MONTH_CODE = u"\u6708"

    def get(self):

        douban_url = self.DOUBAN_URL

        # proxy //Issue 544: urlfetch cannot be used behind a proxy

        # mock-user / optional
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)
        # Chrome/35.0.1916.114 Safari/537.36'}
        # req=urllib2.Request(url,headers=headers)
        try:
            # prevent error "Deadline exceeded while waiting for HTTP response from URL"
            # urlfetch.set_default_fetch_deadline(120) TODO not necessary
            response = urlfetch.fetch(douban_url)
        except BaseException as e:
            logging.error("error to open url http://movie.douban.com/coming caused by %s" % e)
            return

        logging.info(douban_url + " fetch success\n %s" % response.content[0:100])

        try:
            # parse html page
            encoding = "utf-8"
            parser = etree.HTMLParser(recover=True, encoding=encoding)
            tree = etree.fromstring(response.content, parser)

            # xpath query
            html_tbody = tree.xpath(
                "/html/body/div[@id='wrapper']/div[@id='content']/div[@class='grid-16-8 clearfix']/div[@class='article']/table[@class='coming_list']/tbody")
            assert len(html_tbody) == 1 and html_tbody[0].tag == "tbody"

        except BaseException as e:
            logging.error(
                "error to parse the html content from http://movie.douban.com/coming via lxml.HTMLParser\n %s" % e)
            return

        html_tr_movies = html_tbody[0].getchildren()
        assert len(html_tr_movies) > 0 and html_tr_movies[0].tag == "tr"
        logging.info("total coming movies: " + str(len(html_tr_movies)))

        # (async) clear all events in target calendar
        self.clear_calendar()

        google_calednar_service = get_google_calendar_service()
        success_event = 0
        total_movies = len(html_tr_movies)
        try:
            for movie_tr in html_tr_movies:   # XML Element Object
                html_td_list_movie = movie_tr.getchildren()
                movie_date = html_td_list_movie[0].text.encode('utf-8').strip()
                movie_name = html_td_list_movie[1].getchildren()[0].text.encode('utf-8').strip()
                movie_link = html_td_list_movie[1].getchildren()[0].get('href')
                movie_category = html_td_list_movie[2].text.encode('utf-8').strip()
                movie_location = html_td_list_movie[3].text.encode('utf-8').strip()

                if len(movie_date) > 0:
                    new_movie_date = self.convert_to_datetype(self.fix_movie_date(movie_date))
                    if movie_date is None:
                        logging.error("fix movie date failed for " + movie_name + movie_date)
                        continue

                # (async) create calendar movie event
                if self.create_movie_event(google_calednar_service, movie_date=new_movie_date, movie_name=movie_name,
                                           movie_category=movie_category, movie_location=movie_location,
                                           day_confirmed=self.DAY_CODE in movie_date, total_event=total_movies,
                                           nth_event=success_event):
                    success_event += 1

                movie_url_enqueue("movie", movie_link)

                self.response.write(new_movie_date)
                self.response.write("        ")
                self.response.write(movie_name)
                self.response.write("        ")
                self.response.write(movie_category)
                self.response.write("        ")
                self.response.write(movie_location)
                self.response.write("        ")
                self.response.write(html_td_list_movie[4].text.encode('utf-8').strip())
                self.response.write("<br>")

            if success_event == total_movies:
                logging.info("total created movie event(all success) :%s", total_movies) #TODO
            else:
                logging.warning("total created movie event: %s/%s", total_movies, success_event)

        except BaseException as e:
            logging.error("error to parse movie content from tbody/tr/td\n %s" % e)

        # self.retry_timeout_request() reliability guaranteed by push queue

    # fix movie_date for three sorts of short date string 1202ri/12yue/2015nian01yue

    def fix_movie_date(self, movie_date):
        this_year = str(date.today().year)
        default_day = "15"

        if not self.YEAR_CODE in movie_date and not self.DAY_CODE in movie_date:
            return this_year + self.YEAR_CODE + movie_date + default_day + self.DAY_CODE
        if not self.YEAR_CODE in movie_date:
            return this_year + self.YEAR_CODE + movie_date
        if not self.DAY_CODE in movie_date:
            return movie_date + default_day + self.DAY_CODE

        return movie_date

    # string representation of chinese date 2014nian12yue01ri

    def convert_to_datetype(self, str_date):
        try:
            t = str_date.replace(self.YEAR_CODE, "").replace(self.MONTH_CODE, "").replace(self.DAY_CODE, "")
            return datetime.strptime(t, "%Y%m%d").date()
        except Exception, e:
            logging.error("error to convert str date: %s, %s" % (str_date, e))



    def clear_calendar(self):

        service = get_google_calendar_service()

        nth_event = 0
        total_event = 0
        try:
            calendar = service.calendars().get(calendarId=DOUBAN_CALENDAR_ID).execute()

            # Google calculates a 'page' of events to return, it includes the deleted events in that calculation,
            # and your first page is full of deleted events that you don't see unless your request has "showDeleted = True".
            # Do not works if have too much deleted hidden events!!!!
            # events = service.events().list(calendarId=self.doubanCalendarId, maxResults=250).execute()

            logging.info(
                "Google Calendar API_Calendars:get\n\tcalendarSummary: %s, calendarDesc: %s", calendar['summary'],
                calendar['description'])

            # get all events(deleted events are included too)
            page_token = None
            while True:
                events = service.events().list(calendarId=DOUBAN_CALENDAR_ID, pageToken=page_token,
                                               maxResults=250).execute()
                logging.info("#########Google Calendar API_Events: list   pageToken: %s, pageSize: %s", page_token,
                             len(events['items']))
                total_event += len(events['items'])  # one page

                for event in events['items']:
                    try:
                        taskqueue.add(queue_name='MovieDeleteQueue', url='/calendar/delete',
                                      params={'event': json.dumps(event), "total_event": total_event, "nth_event": nth_event})
                    except BaseException as ex:
                        logging.warning("push %s to [MovieDeleteQueue] failed: %s" % (event['summary'], ex))
                        continue
                    nth_event += 1
                page_token = events.get('nextPageToken')
                if not page_token:
                    break
        except Exception as e:
            logging.error("clear douban movie calendar exception / %s" % e)

        return True

    def create_movie_event(self, google_calendar_service, **kwargs):
        tips = ("_" + u"\u4E0A\u6620\u65E5\u671F\u672A\u5B9A") if not kwargs["day_confirmed"] else ""

        event = {
            'summary': kwargs["movie_name"] + "_" + kwargs["movie_category"] + "_" + kwargs[
                "movie_location"] + tips,
            'location': "created by shawn guo 2015/02/11 Shanghai",
            'start': {'date': str(kwargs["movie_date"])},
            'end': {'date': str(kwargs["movie_date"])}
        }
        try:
            taskqueue.add(queue_name='MovieInsertQueue', url='/calendar/insert',
                          params={'event': json.dumps(event), "total_event": kwargs["total_event"],
                                  "nth_event": kwargs["nth_event"]})
        except BaseException as ex:
            logging.warning("push %s to [MovieInsertQueue] failed: %s" % (event['summary'], ex))
            return False

        return True


class DeleteEventHandler(webapp2.RequestHandler):
    def post(self):
        service = get_google_calendar_service()

        # payload
        event = json.loads(self.request.get('event'))
        total_event = self.request.get('total_event')
        nth_event = int(self.request.get('nth_event')) + 1
        # noinspection PyBroadException
        logging.info("deleting event[total(%s)/(%sth)]: %s_%s", total_event, nth_event,
                     (event['summary'] if 'summary' in event else "(No Title)"), event['id'])
        try:
            service.events().delete(calendarId=DOUBAN_CALENDAR_ID, eventId=event['id']).execute()
            self.response.status = 200  # 200 OK
        except BaseException as e:
            logging.error("DeleteEventHandler excepion: %s" % e)  # TODO
            self.response.status = 500  # 500 Internal Server Error, Retry the task


class InsertEventHandler(webapp2.RequestHandler):
    def post(self):
        google_calednar_service = get_google_calendar_service()

        # payload
        event = json.loads(self.request.get('event'))
        total_event = self.request.get('total_event')
        nth_event = int(self.request.get('nth_event')) + 1

        logging.info("inserting event[total(%s)/(%sth)]: %s", total_event, nth_event, event["summary"])
        # noinspection PyBroadException
        try:
            created_event = google_calednar_service.events().insert(calendarId=DOUBAN_CALENDAR_ID, body=event).execute()
            self.response.status = 200  # 200 OK
        except BaseException as e:
            logging.error("InsertEventHandler excepion: %s" % e)  # TODO The API call urlfetch.Fetch() took too long to respond and was cancelled.
            self.response.status = 500  # 500 Internal Server Error, Retry the task
