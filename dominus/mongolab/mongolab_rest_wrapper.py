__author__ = 'shawguo'

import json
import requests
import logging
import datetime


class MongolabRestWrapper:
    """
    Rest API Wrapper for mongolab http://docs.mongolab.com/restapi/#create-collection
    """

    API_KEY = "oFrccImwDd3wsKmHf4WWdkM9LVRqlRx_"
    HTTP_API_KEY = {"apiKey": API_KEY}
    HTTP_HEADERS = {"Content-Type": "application/json"}
    HTTP_TIMIOUT = 20  # seconds

    def __init__(self):
        return

    def insert_document(self, doc_path, doc):
        """
        Mongolab Rest API Wrapper for insert documents
        docPath = "database.collection"
        doc = python dictionary representation of json-document.
        sample url https://api.mongolab.com/api/1/databases/my-db/collections/my-coll?apiKey=myAPIKey
        """
        assert len(doc_path.split(".")) == 2

        rest_url = "https://api.mongolab.com/api/1/databases/%s/collections/%s" % tuple(doc_path.split("."))
        # TODO network timeout
        response = requests.post(rest_url, params=self.HTTP_API_KEY, headers=self.HTTP_HEADERS,
                                 timeout=self.HTTP_TIMIOUT,
                                 data=json.dumps(doc))
        logging.debug("(insert_document)Request URL: %s" % response.url)
        #  return response.json()
        return True if response.status_code == 200 or response.status_code == 201 else False

    '''
    Mongolab Rest API Wrapper for List documents
        http://docs.mongolab.com/restapi/#list-documents
        q=<query> - restrict results by the specified JSON query
        c=true - return the result count for this query
        f=<set of fields> - specify the set of fields to include or exclude in each document (1 - include; 0 - exclude)
        fo=true - return a single document from the result set (same as findOne() using the mongo shell
        s=<sort order> - specify the order in which to sort each specified field (1- ascending; -1 - descending)
        sk=<num results to skip> - specify the number of results to skip in the result set; useful for paging
        l=<limit> - specify the limit for the number of results (default is 1000)
    '''

    def list_documents(self, doc_path, q=None, c=False, f=None, fo=None, s=None, sk=None, l=None):
        assert len(doc_path.split(".")) == 2

        rest_url = "https://api.mongolab.com/api/1/databases/%s/collections/%s" % tuple(doc_path.split("."))

        # Send the request.
        send_kwargs = {}
        send_kwargs.update(self.HTTP_API_KEY)
        # Note that any dictionary key whose value is None will not be added to the URL's query string.
        send_kwargs['q'] = json.dumps(q) if q else None
        send_kwargs['c'] = json.dumps(c) if c else None
        send_kwargs['f'] = json.dumps(f) if f else None
        send_kwargs['fo'] = json.dumps(fo) if fo else None
        send_kwargs['s'] = json.dumps(s) if s else None
        send_kwargs['sk'] = json.dumps(sk) if sk else None
        send_kwargs['l'] = json.dumps(l) if l else None

        # send_kwargs.
        # TODO network timeout
        response = requests.get(rest_url, params=send_kwargs, headers=self.HTTP_HEADERS, timeout=self.HTTP_TIMIOUT)
        logging.debug("(list_documents)Request URL: %s" % response.url)
        print("Request URL: %s" % response.url)
        return response.json()

     # def delete_document

MONGOLAB_REST_WRAPPER = MongolabRestWrapper()

def main():
    # helper = MongolabRestWrapper()
    print MONGOLAB_REST_WRAPPER.insert_document("shawguo.movie_event", {"name": "shawguo1", "movie_data": "today","sysdate":{"$date":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}})
    # print helper.list_documents("shawguo.movie_event",q={"name":"shawguo"},f={"name":1})

if __name__ == "__main__":
    main()