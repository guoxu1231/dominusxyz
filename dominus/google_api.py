__author__ = 'shawguo'

import httplib2
import pprint
import sys
from oauth2client import crypt

from googleapiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
import logging
import traceback

# google api

# Load the key in PKCS 12 format that you downloaded from the Google API
# Console when you created your Service account.
f = file('dominusxyz-ca68cf724727.pem', 'rb')
key = f.read()
f.close()

# Create an httplib2.Http object to handle our HTTP requests and authorize it
# with the Credentials. Note that the first parameter, service_account_name,
# is the Email address created for the Service account. It must be the email
# address associated with the key that was created.
credentials = SignedJwtAssertionCredentials(
    '729313260996-tlhkhmc5mk9b02la7a5vnae548tobl8m@developer.gserviceaccount.com',
    key,
    scope='https://www.googleapis.com/auth/calendar')
http = httplib2.Http(timeout=5)
http = credentials.authorize(http)


def get_google_calendar_service():
    # Build a service object for interacting with the API. Visit
    # the Google Developers Console
    # to get a developerKey for your own application.
    try:
        service = build(serviceName='calendar', version='v3', http=http)
        google_calendar_service = service
    except:
        logging.error("get google calendar service api failed\n" + traceback.format_exc())
    logging.info("get google calendar service api success")
    return service