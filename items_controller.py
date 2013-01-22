import webapp2
from handlers import BaseHandler
import env
from models import Item
from datetime import datetime
import logging

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('items/index.html',recently_added=Item.fresh().order('-creation_time').run(limit=10),about_to_expire=Item.fresh().order('creation_time').run(limit=10))
class SearchHandler(BaseHandler):
    pass
class ItemListHandler(BaseHandler):
    def get(self):
        itms=self.current_user.owned_items().order('-creation_time')
        self.render_template('items/list.html',active_items=Item.fresh(itms).run(),expired_items=Item.expired(self.current_user.owned_items().order('-creation_time')).run())
class AddItemHandler(BaseHandler):
    def get(self):
        self.render_template('items/form.html',title="Add an Item",item_expiry=datetime.now()+Item.EXPIRATION_DELTA)
    def commit_item_changes(self,item=None):
        creation=not(not(item))
        if not item: item=Item()
        item_name=self.request.get('name')
        item_price=self.request.get('price')
        item_description=self.request.get('description')
        errors=[]
        if item_name=="": errors.append("The item name must not be blank.")
        if item_description=="": errors.append("The item description must not be blank.")
        try:
            item_price=float(item_price)
        except ValueError:
            errors.append("The price must be a number.")
        if item_price <=0: errors.append("The price must be greater than zero.")
        if len(errors):
            self.render_template('items/form.html',title="Add an Item",errors=errors,item_expiry=datetime.now()+Item.EXPIRATION_DELTA,item_name=item_name,item_description=item_description,item_price=item_price)
        else:
            item.name=item_name
            item.owner=self.current_user.key()
            item.price=item_price
            item.description=item_description
            item.put()
            self.log("item %s"%"created" if creation else "edited")
            self.redirect('/items')
    def post(self):
        self.commit_item_changes()
def my_item_from_ident(handler,ident,allow_admin=False):
    try:
        item=Item.get_by_id(int(ident))
    except:
        handler.abort(404)
    if not item: handler.abort(404)
    if item.owner.key()!=handler.current_user.key() and not (allow_admin and handler.current_user.admin): handler.abort(404)
    return item
class EditItemHandler(AddItemHandler):
    def get(self,ident):
        item=my_item_from_ident(self,ident)
        self.render_template('items/form.html',item_price=item.price,item_name=item.name,item_description=item.description,title="Edit '%s'"%item.name,item_expiry=datetime.now()+Item.EXPIRATION_DELTA)
    def post(self,ident):
        self.commit_item_changes(my_item_from_ident(self,ident))
class DeleteItemHandler(BaseHandler):
    def post(self,ident):
        item=my_item_from_ident(self,ident,allow_admin=True)
        item.delete()
        self.log('item deleted')
        self.redirect('/items/')
class ShowItemHandler(BaseHandler):
    def get(self,ident):
        try:
            item=Item.get_by_id(int(ident))
        except:
            self.abort(404)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user): self.abort(403)
        self.render_template('items/show.html',item=item)
app = webapp2.WSGIApplication([
    ('/',IndexHandler),
    ('/search',SearchHandler),
    ('/items/',ItemListHandler),
    ('/items',ItemListHandler),
    ('/items/add',AddItemHandler),
    (r'/items/(\d+)/.*/edit',EditItemHandler),
    (r'/items/(\d+)/edit',EditItemHandler),
    (r'/items/(\d+)/.*/delete',DeleteItemHandler),
    (r'/items/(\d+)/delete',DeleteItemHandler),
    (r'/items/(\d+)/.*',ShowItemHandler),
    (r'/items/(\d+)',ShowItemHandler),
], debug=(env.env==env.DEVELOPMENT))