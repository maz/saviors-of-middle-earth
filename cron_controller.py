from models import Item
import webapp2
from handlers import BaseHandler
import env

class RemoveExpiredHandler(webapp2.RequestHandler):
    def get(self):
        index=Item.search_index()
        for itm in Item.expired().run(limit=None):
            index.delete(str(itm.key()))

app = webapp2.WSGIApplication([
    ('/cron/remove-expired-from-search',RemoveExpiredHandler),
], debug=(env.env==env.DEVELOPMENT))
