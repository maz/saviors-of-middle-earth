import webapp2
from handlers import BaseHandler
import env
from models import Item

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('items/index.html',recently_added=Item.fresh().order('-creation_time').run(limit=10))
class SearchHandler(BaseHandler):
    pass
class ItemListHandler(BaseHandler):
    def get(self):
        self.render_template('items/list.html')

app = webapp2.WSGIApplication([
    ('/',IndexHandler),
    ('/search',SearchHandler),
    ('/items/',ItemListHandler),
    ('/items',ItemListHandler)
], debug=(env.env==env.DEVELOPMENT))