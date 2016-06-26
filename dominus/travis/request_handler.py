__author__ = 'shawguo'

import webapp2
import dominus.travis.security


class TravisHttpPropertiesHandler(webapp2.RequestHandler):
    """
    Basic authentication(user and password defined in travis environement variables) and return confidential properties.
    """

    def get(self):
        user = self.request.get("gae.user")
        password = self.request.get("gae.password")
        if user == dominus.travis.security.user and password == dominus.travis.security.password:
            self.response.write(dominus.travis.security.urlResource)
            self.response.status = 200
        else:
            self.response.write("invalid access")
        return
