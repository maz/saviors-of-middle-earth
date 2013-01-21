import webapp2
from handlers import BaseHandler
import env

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('items/index.html')
class SearchHandler(BaseHandler):
    pass


app = webapp2.WSGIApplication([
    ('/',IndexHandler),
    ('/search',SearchHandler)
], debug=(env.env==env.DEVELOPMENT))