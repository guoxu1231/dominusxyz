__author__ = 'shawguo'
import os
import jinja2
import webapp2


# jinja_environment = jinja2.Environment(autoescape=True,
# loader=jinja2.FileSystemLoader(
# os.path.join(os.path.dirname(__file__), 'template')))
JINJA_ENVIRONMENT = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader('template'))


class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'name': 'SomeGuy',
            'verb': 'extremely enjoy'
        }
        template = JINJA_ENVIRONMENT.get_template('jinja_template.html')
        self.response.write(template.render(template_values))




