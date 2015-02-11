#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from dominus.coming_movie import ComingMovieHandler
from dominus.coming_movie_v2 import DeleteEventHandler
from dominus.coming_movie_v2 import InsertEventHandler
from dominus.coming_movie_v2 import ComingMovieV2Handler
from dominus.gae.image_upload import UploadForm
from dominus.gae.image_upload import ServeHandler
from dominus.gae.image_upload_pld import FileUploadFormHandler
from dominus.gae.image_upload_pld import AjaxSuccessHandler
from dominus.gae.image_upload_pld import GenerateUploadUrlHandler
from dominus.gae.image_upload_pld import FileUploadHandler
from dominus.gae.jinja_test import MainPage
import dominus.gae.image_upload_jfu
import dominus.gae.image_upload
from dominus.mongolab.mongolab_heartbeat import MongolabHeartbeatHandler


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/coming_movie_v2', ComingMovieV2Handler),
    ('/coming_movie_v2/delete', DeleteEventHandler),
    ('/coming_movie_v2/insert', InsertEventHandler),
    ('/mongolab_heartbeat', MongolabHeartbeatHandler),
    ('/coming_movie', ComingMovieHandler),
    ('/gae/upload_form', UploadForm),
    ('/gae/upload', dominus.gae.image_upload.UploadHandler),
    ('/gae/upload_jfu', dominus.gae.image_upload_jfu.UploadHandler),
    ('/gae/serve/([^/]+)?', ServeHandler),  # basic upload
    ('/gae/jinja', MainPage),               # jinja templating
    ('/gae/upload_form_pld', FileUploadFormHandler),
    ('/gae/image_upload_pld', FileUploadHandler),
    ('/gae/file/([0-9]+)/success', AjaxSuccessHandler),
    ('/gae/generate_upload_url', GenerateUploadUrlHandler)  # plupload
], debug=True)