__author__ = 'shawguo'

import sys
import webapp2
from google.appengine.api import urlfetch
from lxml import etree
from lxml import html
import lxml
import traceback
from datetime import date
from datetime import datetime
import logging
import urllib2
from dominus.google_api import get_google_calendar_service
import json


reload(sys)
sys.setdefaultencoding('utf-8')


class ComingMovieHandler(webapp2.RequestHandler):
    def get(self):

        douban_url = "http://movie.douban.com/coming"

        # proxy //Issue 544: urlfetch cannot be used behind a proxy
        # enable_proxy = True
        # proxy_handler = urllib2.ProxyHandler({"http": 'www-proxy.us.oracle.com:80'})
        # null_proxy_handler = urllib2.ProxyHandler({})
        # if enable_proxy:
        # opener = urllib2.build_opener(proxy_handler)
        # else:
        # opener = urllib2.build_opener(null_proxy_handler)
        # urllib2.install_opener(opener)
        #
        # print urllib2.getproxies()

        # mock-user
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36'}
        # req=urllib2.Request(url,headers=headers)
        try:
            # response = urllib2.urlopen(douban_url, timeout=15).read()

            # prevent error "Deadline exceeded while waiting for HTTP response from URL"
            urlfetch.set_default_fetch_deadline(120)
            response = urlfetch.fetch(douban_url)
        except Exception:
            logging.error("error to open url http://movie.douban.com/coming by urllib2\n" + traceback.format_exc())
            return

        logging.info(douban_url + " fetch success\n" + response.content[0:100])

        try:
            # parse html page
            encoding = "utf-8"
            parser = etree.HTMLParser(recover=True, encoding=encoding)
            tree = etree.fromstring(response.content, parser)

            # xpath query
            html_tbody = tree.xpath(
                "/html/body/div[@id='wrapper']/div[@id='content']/div[@class='grid-16-8 clearfix']/div[@class='article']/table[@class='coming_list']/tbody")
            assert len(html_tbody) == 1 and html_tbody[0].tag == "tbody"

        except Exception:
            logging.error(
                "error to parse the html content from http://movie.douban.com/coming via lxml.HTMLParser\n" + traceback.format_exc())
            return

        html_tr_movies = html_tbody[0].getchildren()
        assert len(html_tr_movies) > 0 and html_tr_movies[0].tag == "tr"
        logging.info("total coming movies: " + str(len(html_tr_movies)))

        # httplib2.Http().

        # clear all events in target calendar
        self.clear_calendar()

        google_calednar_service = get_google_calendar_service()
        success_event = 0
        total_movies = len(html_tr_movies)
        try:
            for movie_tr in html_tr_movies:
                # print "td count: "+str(len(movie_tr.getchildren()))
                html_td_list_movie = movie_tr.getchildren()
                movie_date = html_td_list_movie[0].text.encode('utf-8').strip()
                movie_name = html_td_list_movie[1].getchildren()[0].text.encode('utf-8').strip()
                movie_category = html_td_list_movie[2].text.encode('utf-8').strip()
                movie_location = html_td_list_movie[3].text.encode('utf-8').strip()

                if len(movie_date) > 0:
                    new_movie_date = self.convert_to_dateType(self.fix_movie_date(movie_date))
                    if movie_date is None:
                        logging.error("fix movie date failed for " + movie_name + movie_date)
                        continue

                print new_movie_date
                print movie_name
                print movie_category
                print movie_location
                print html_td_list_movie[4].text.encode('utf-8').strip()

                # create calendar movie event

                if self.create_movie_event(google_calednar_service, movie_date=new_movie_date, movie_name=movie_name,
                                           movie_category=movie_category, movie_location=movie_location,
                                           day_confirmed=self.day_code in movie_date):
                    success_event = success_event + 1

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
                logging.info("total created movie event(all success) :%s", total_movies)
            else:
                logging.warning("total created movie event: %s/%s", total_movies, success_event)

        except Exception:
            logging.error("error to parse movie content from tbody/tr/td\n" + traceback.format_exc())

        self.response.write("")


    year_code = u"\u5e74"
    day_code = u"\u65e5"
    month_code = u"\u6708"
    # fix movie_date for three sorts of short date string 1202ri/12yue/2015nian01yue
    def fix_movie_date(self, movie_date):
        this_year = str(date.today().year)
        default_day = "15"

        if not self.year_code in movie_date and not self.day_code in movie_date: return this_year + self.year_code + movie_date + default_day + self.day_code
        if not self.year_code in movie_date: return this_year + self.year_code + movie_date
        if not self.day_code in movie_date: return movie_date + default_day + self.day_code

        return movie_date

    # string representation of chinese date 2014nian12yue01ri
    def convert_to_dateType(self, str_date):
        try:
            t = str_date.replace(self.year_code, "").replace(self.month_code, "").replace(self.day_code, "")
            return datetime.strptime(t, "%Y%m%d").date()
        except Exception, e:
            print("error to convert str date: " + str_date)
            print e
            print traceback.format_exc()


    # vcl68tom0updk2nfnf8pjqce0c@group.calendar.google.com
    doubanCalendarId = "vcl68tom0updk2nfnf8pjqce0c@group.calendar.google.com"

    def clear_calendar(self):

        service = get_google_calendar_service()
        if service is None: return False

        clear_count = 0
        total_event = 0
        try:
            calendar = service.calendars().get(calendarId=self.doubanCalendarId).execute()

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
                events = service.events().list(calendarId=self.doubanCalendarId, pageToken=page_token,
                                               maxResults=250).execute()
                logging.info("#########Google Calendar API_Events: list   pageToken: %s, pageSize: %s", page_token,
                             len(events['items']))

                total_event += len(events['items'])  # one page
                for event in events['items']:
                    logging.debug("deleting event: %s_%s", (event['summary'] if 'summary' in event else "(No Title)"),
                                  event['id'])
                    try:
                        service.events().delete(calendarId=self.doubanCalendarId, eventId=event['id']).execute()
                    except:
                        logging.warning("clear movie event failed: %s \n" + traceback.format_exc(), event['summary'])
                        continue
                    clear_count += 1
                page_token = events.get('nextPageToken')
                if not page_token:
                    break
        except:
            logging.error("clear douban movie calendar exception\n" + traceback.format_exc())

        logging.info("clear douban movie calendar done: total(%s)/deleted(%s)", total_event, clear_count)

        return True

    def create_movie_event(self, google_calendar_service, **kwargs):

        tips = ("_" + u"\u4E0A\u6620\u65E5\u671F\u672A\u5B9A") if not kwargs["day_confirmed"] else ""

        event = {
            'summary': kwargs["movie_name"] + "_" + kwargs["movie_category"] + "_" + kwargs[
                "movie_location"] + tips,
            'location': "created by shawn guo 2014/12/01 Shanghai",
            'start': {'date': str(kwargs["movie_date"])},
            'end': {'date': str(kwargs["movie_date"])}
        }
        try:
            created_event = google_calendar_service.events().insert(calendarId=self.doubanCalendarId,
                                                                    body=event).execute()
            logging.debug("creating movie calendar event success: " + created_event['id'] + "_" + kwargs["movie_name"])
        except:
            logging.error("creating movie calendar event failed\n %s\n" + traceback.format_exc(), kwargs["movie_name"])
            return False

        return True