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
        itms=self.current_user.owned_items().order('-creation_time')
        self.render_template('items/list.html',active_items=Item.fresh(itms).run(),expired_items=Item.expired(itms).run())
class AddItemHandler(BaseHandler):
    def get(self):
        self.render_template('items/form.html',title="Add an Item")
app = webapp2.WSGIApplication([
    ('/',IndexHandler),
    ('/search',SearchHandler),
    ('/items/',ItemListHandler),
    ('/items',ItemListHandler),
    ('/items/add',AddItemHandler)
], debug=(env.env==env.DEVELOPMENT))