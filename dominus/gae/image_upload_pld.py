__author__ = 'shawguo'

import webapp2
import os
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from jinja_test import JINJA_ENVIRONMENT


# new image upload module, suppoted by Plupload http://www.plupload.com/
class FileUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'form_url': blobstore.create_upload_url('/gae/image_upload_pld')
        }
        template = JINJA_ENVIRONMENT.get_template('upload_pld.html')
        self.response.write(template.render(template_values))

# for multiple upload
class GenerateUploadUrlHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(blobstore.create_upload_url('/gae/image_upload_pld'))


class FileUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        blob_info = self.get_uploads()[0]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write('{"jsonrpc":"2.0", "result":null, "id":%s,"OK":1}' % ('111',))
        # self.redirect("/gae/file/%s/success" % (blob_info.key(),))

class AjaxSuccessHandler(webapp2.RequestHandler):
    def get(self, file_id):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write('{"jsonrpc":"2.0", "result":null, "id":%s,"OK":1}' % (file_id,))


