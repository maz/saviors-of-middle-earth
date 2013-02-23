import webapp2
from handlers import BaseHandler
import env

app = webapp2.WSGIApplication([], debug=(env.env==env.DEVELOPMENT))