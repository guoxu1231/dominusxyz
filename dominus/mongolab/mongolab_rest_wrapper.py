__author__ = 'shawguo'

import json
import requests
import logging
import datetime


class MongolabRestWrapper:
    """
    Rest API Wrapper for mongolab http://docs.mongolab.com/restapi/#create-collection
        Caller should care about the network exception not wrapper.
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
            doc = single json-document (python dict) or multiple documents(python dict list)
        sample url https://api.mongolab.com/api/1/databases/my-db/collections/my-coll?apiKey=myAPIKey
        """
        assert len(doc_path.split(".")) == 2

        rest_url = "https://api.mongolab.com/api/1/databases/%s/collections/%s" % tuple(doc_path.split("."))
        response = requests.post(rest_url, params=self.HTTP_API_KEY,
                                 headers=self.HTTP_HEADERS,
                                 timeout=self.HTTP_TIMIOUT,
                                 data=json.dumps(doc))
        # response text : single document, json document with _id, multiple document: { "n" : 2}
        logging.debug("(insert_document)Response text: %s" % response.text)
        return True if response.status_code == 200 or response.status_code == 201 else False

    def list_documents(self, doc_path, q=None, c=False, f=None, fo=None, s=None, sk=None, l=None):
        """
        Mongolab Rest API Wrapper for List documents
        http://docs.mongolab.com/restapi/#list-documents
        q=<query> - restrict results by the specified JSON query
        c=true - return the result count for this query
        f=<set of fields> - specify the set of fields to include or exclude in each document (1 - include; 0 - exclude)
        fo=true - return a single document from the result set (same as findOne() using the mongo shell
        s=<sort order> - specify the order in which to sort each specified field (1- ascending; -1 - descending)
        sk=<num results to skip> - specify the number of results to skip in the result set; useful for paging
        l=<limit> - specify the limit for the number of results (default is 1000)
        """

        assert len(doc_path.split(".")) == 2

        rest_url = "https://api.mongolab.com/api/1/databases/%s/collections/%s" % tuple(doc_path.split("."))

        # Send the request.
        send_kwargs = {}
        send_kwargs.update(MongolabRestWrapper.HTTP_API_KEY)
        # Note that any dictionary key whose value is None will not be added to the URL's query string.
        send_kwargs['q'] = json.dumps(q) if q else None
        send_kwargs['c'] = json.dumps(c) if c else None
        send_kwargs['f'] = json.dumps(f) if f else None
        send_kwargs['fo'] = json.dumps(fo) if fo else None
        send_kwargs['s'] = json.dumps(s) if s else None
        send_kwargs['sk'] = json.dumps(sk) if sk else None
        send_kwargs['l'] = json.dumps(l) if l else None

        # send_kwargs.
        response = requests.get(rest_url, params=send_kwargs, headers=self.HTTP_HEADERS,
                                timeout=self.HTTP_TIMIOUT)
        logging.debug("(list_documents)Request URL: %s" % response.url)
        logging.debug("(list_documents)Response Text: %s" % response.text)
        # print("Request URL: %s" % response.url)
        return response.json()

    def delete_documents(self, doc_path, q=None):
        """
        Mongolab REST API Wrapper for Delete/replace multiple documents
            http://docs.mongolab.com/restapi/#view-edit-delete-document
        :param doc_path:
        :param q=<query> - only delete the document(s) matching the specified JSON query
        :return: number of removed documents
        """
        assert len(doc_path.split(".")) == 2

        rest_url = "https://api.mongolab.com/api/1/databases/%s/collections/%s" % tuple(doc_path.split("."))
        # send_kwargs.
        send_kwargs = {}
        send_kwargs.update(MongolabRestWrapper.HTTP_API_KEY)
        send_kwargs['q'] = json.dumps(q) if q else None
        # send_kwargs['m'] = True

        # Specifying an empty list in the body is equivalent to deleting the documents
        response = requests.put(rest_url, params=send_kwargs, headers=self.HTTP_HEADERS,
                                timeout=self.HTTP_TIMIOUT, data="[]")
        logging.debug("(delete_documents)Request URL: %s" % response.url)
        # { "n" : 0 , "removed" : 1}
        logging.debug("(delete_documents)Response Text: %s" % response.text)
        # print("Request URL: %s" % response.url)
        return response.json()["removed"]


MONGOLAB_REST_WRAPPER = MongolabRestWrapper()


def main():
    logging.basicConfig(level=logging.DEBUG)

    assert MONGOLAB_REST_WRAPPER.delete_documents("shawguo.testcase", q={"test": 1234}) == 0

    MONGOLAB_REST_WRAPPER.delete_documents("shawguo.testcase", q={"name": "shawguo1"})

    assert MONGOLAB_REST_WRAPPER.insert_document("shawguo.testcase", {"name": "shawguo1", "is_debug": True, "id": 1234,
                                                                      "sysdate": {
                                                                          "$date": datetime.datetime.utcnow().strftime(
                                                                              "%Y-%m-%dT%H:%M:%SZ")}}) == True

    assert MONGOLAB_REST_WRAPPER.insert_document("shawguo.testcase", [{"name": "shawguo1", "is_debug": True, "id": 1235,
                                                                       "sysdate": {
                                                                           "$date": datetime.datetime.utcnow().strftime(
                                                                               "%Y-%m-%dT%H:%M:%SZ")}},
                                                                      {"name": "shawguo1", "is_debug": True, "id": 1236,
                                                                       "sysdate": {
                                                                           "$date": datetime.datetime.utcnow().strftime(
                                                                               "%Y-%m-%dT%H:%M:%SZ")}}]) == True

    assert MONGOLAB_REST_WRAPPER.list_documents("shawguo.testcase", c=True, q={"id": 1234}) == 1

    assert MONGOLAB_REST_WRAPPER.delete_documents("shawguo.testcase", q={"id": 1234}) == 1
    #
    # MONGOLAB_REST_WRAPPER.delete_documents("shawguo.testcase", q={"name": "shawguo1"})
    # print helper.list_documents("shawguo.movie_event",q={"name":"shawguo"},f={"name":1})


if __name__ == "__main__":
    main()