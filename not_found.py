import webapp2
from handlers import BaseHandler
import env

class NotFoundHandler(BaseHandler):
    def inner_dispatch(self):
        self.abort(404)

app = webapp2.WSGIApplication([
    ('/.*',NotFoundHandler),
], debug=(env.env==env.DEVELOPMENT))