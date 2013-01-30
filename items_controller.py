import webapp2
from handlers import BaseHandler
import env
from models import Item, Communique
from datetime import datetime
import base64

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('items/index.html',recently_added=Item.fresh().order('-creation_time').run(limit=10),about_to_expire=Item.fresh().order('creation_time').run(limit=10))
class SearchHandler(BaseHandler):
    def get(self):
        def generate_ctx():
            return Item.all() if self.current_user and self.current_user.admin else Item.fresh()
        per_page=10
        off=int(self.request.get('offset')) if self.request.get('offset') else 0
        if off<0: off=0
        total=generate_ctx().count(limit=per_page,offset=off)
        results=generate_ctx().run(limit=per_page,offset=off)
        #TODO: how do we actually search this stuff?
        self.render_template('items/search.html',q=self.request.get('q'),results=results,total=total,offset=off,per_page=per_page)
class AddItemHandler(BaseHandler):
    def get(self):
        self.render_template('items/form.html',title="Add an Item",item_expiry=datetime.now()+Item.EXPIRATION_DELTA)
    def commit_item_changes(self,item=None):
        creation=not(item)
        if not item: item=Item()
        item_name=self.request.get('name')
        item_price=self.request.get('price')
        item_description=self.request.get('description')
        item_picture=self.request.get('picture_512')
        errors=[]
        if item_name=="": errors.append("The item name must not be blank.")
        if item_description=="": errors.append("The item description must not be blank.")
        try:
            item_price=float(item_price)
        except ValueError:
            errors.append("The price must be a number.")
        if item_price <=0: errors.append("The price must be greater than zero.")
        if len(errors):
            self.render_template('items/form.html',title="Add an Item",item_picture_data=item_picture,item_picture=("data:image/png;base64,%s"%item_picture if item_picture else item.url(named=False,action="picture")),errors=errors,item_expiry=datetime.now()+Item.EXPIRATION_DELTA,item_name=item_name,item_description=item_description,item_price=item_price)
        else:
            item.name=item_name
            item.owner=self.current_user.key()
            item.price=item_price
            item.description=item_description
            item.picture=base64.b64decode(item_picture)
            item.put()
            self.log("item %s"%("created" if creation else "edited"))
            self.flash("'%s' was %s!"%(item_name,"created" if creation else "edited"))
            self.redirect(self.current_user.url())
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
        self.render_template('items/form.html',item_picture=item.url(named=False,action="picture"),item_price=item.price,item_name=item.name,item_description=item.description,title="Edit '%s'"%item.name,item_expiry=datetime.now()+Item.EXPIRATION_DELTA)
    def post(self,ident):
        self.commit_item_changes(my_item_from_ident(self,ident))
class DeleteItemHandler(BaseHandler):
    def post(self,ident):
        item=my_item_from_ident(self,ident,allow_admin=True)
        self.flash("'%s' was deleted!"%item.name)
        item.delete()
        self.log('item deleted')
        self.redirect(self.current_user.url())
class ItemPictureHandler(BaseHandler):
    def get(self,ident):
        try:
            item=Item.get_by_id(int(ident))
        except:
            self.abort(404)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user): self.abort(403)
        self.response.headers['Content-Type']='image/png'
        self.response.out.write(item.picture)
class ShowItemHandler(BaseHandler):
    def get(self,ident):
        try:
            item=Item.get_by_id(int(ident))
        except:
            self.abort(404)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user): self.abort(403)
        self.render_template('items/show.html',item=item)
class CommunicateItemHandler(BaseHandler):
    def post(self,ident):
        try:
            item=Item.get_by_id(int(ident))
        except:
            self.abort(404)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user): self.abort(403)
        c=Communique(users=[self.current_user.key(),item.owner.key().id()],title=item.communique_title)
app = webapp2.WSGIApplication([
    ('/',IndexHandler),
    ('/search',SearchHandler),
    ('/items/add',AddItemHandler),
    (r'/items/(\d+)/.*/edit',EditItemHandler),
    (r'/items/(\d+)/edit',EditItemHandler),
    (r'/items/(\d+)/.*/picture',ItemPictureHandler),
    (r'/items/(\d+)/picture',ItemPictureHandler),
    (r'/items/(\d+)/.*/delete',DeleteItemHandler),
    (r'/items/(\d+)/delete',DeleteItemHandler),
    (r'/items/(\d+)/.*/communicate',CommunicateItemHandler),
    (r'/items/(\d+)/communicate',CommunicateItemHandler),
    (r'/items/(\d+)/.*',ShowItemHandler),
    (r'/items/(\d+)',ShowItemHandler),
], debug=(env.env==env.DEVELOPMENT))