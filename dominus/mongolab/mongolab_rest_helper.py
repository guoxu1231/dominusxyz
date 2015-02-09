__author__ = 'shawguo'

import json

import requests
import logging

# Rest API helper for mongolab http://docs.mongolab.com/restapi/#create-collection


class MongolabRestHelper:
    API_KEY = "oFrccImwDd3wsKmHf4WWdkM9LVRqlRx_"
    HTTP_API_KEY = {"apiKey": API_KEY}
    HTTP_HEADERS = {"Content-Type": "application/json"}

    def __init__(self):
        return

    '''
    Insert document into mongolab via REST API
    docPath = "database.collection"
    doc = python dictionary representation of json-document.
    sample url https://api.mongolab.com/api/1/databases/my-db/collections/my-coll?apiKey=myAPIKey
    '''

    def insert_document(self, docPath, doc):
        assert len(docPath.split(".")) == 2

        rest_url = "https://api.mongolab.com/api/1/databases/%s/collections/%s" % tuple(docPath.split("."))
        logging.debug("insert_document %s to %s", docPath, rest_url)
        response = requests.post(rest_url, params=self.HTTP_API_KEY, headers=self.HTTP_HEADERS, timeout=5,
                                 data=json.dumps(doc))
        print True if response.status_code == 200 else False


def main():
    helper = MongolabRestHelper()
    helper.insert_document("shawguo.movie_event", {"name": "name", "movie_data": "today"})


if __name__ == "__main__":
    main()