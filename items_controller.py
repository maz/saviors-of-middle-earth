import webapp2
from handlers import BaseHandler
import env
from models import Item, Communique,ItemRating,QueryEnsuringAncestor
from datetime import datetime
import base64
import logging
import rich_text
from google.appengine.ext.db import Key
from google.appengine.api import search

class IndexHandler(BaseHandler):
    def get(self):
        self.render_template('items/index.html',**self.memcache("homepage-contents",lambda: dict(recently_added=Item.fresh().order('-creation_time').fetch(limit=10,projection=('name','price','token')),about_to_expire=Item.fresh().order('creation_time').fetch(projection=('name','price','token'),limit=10)),expiration=5))
class SearchHandler(BaseHandler):
    PER_PAGE=10
    def get(self):
        condition=True
        page=int(self.request.get('page')) if self.request.get('page') else 0
        while condition:
            condition=False# I want my do-while loops back!
            off=int(self.request.get('page'))*SearchHandler.PER_PAGE if self.request.get('page') else 0
            query=search.Query(query_string=self.request.get('q'),options=search.QueryOptions(
                limit=SearchHandler.PER_PAGE,
                ids_only=True,
                number_found_accuracy=SearchHandler.PER_PAGE+1,
                offset=off
            ))
            results=Item.search_index().search(query)
            arr=map(lambda x: Item.get(Key(x.doc_id)),results.results)
            for result in arr:
                if result.creation_time<Item.search_expiry_cutoff():
                    condition=True
                    Item.search_index().delete(str(result.key()))   
        self.render_template('items/search.html',q=self.request.get('q'),results=arr,more_pages=((results.number_found-off)>SearchHandler.PER_PAGE),fewer_pages=(page!=0),per_page=SearchHandler.PER_PAGE,page=page)
class AddItemHandler(BaseHandler):
    def get(self):
        self.render_template('items/form.html',title="Add an Item",item_expiry=datetime.now()+Item.EXPIRATION_DELTA)
    def commit_item_changes(self,item=None):
        creation=not(item)
        if not item: item=Item(parent=self.current_user.key())
        item_name=self.request.get('name')
        item_price=self.request.get('price')
        item_description=rich_text.from_style_runs(self.request.get('description'))
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
            self.render_template('items/form.html',title="Add an Item",item_picture_data=item_picture,item_picture=("data:image/png;base64,%s"%item_picture if item_picture or creation else item.url(named=False,action="picture")),errors=errors,item_expiry=datetime.now()+Item.EXPIRATION_DELTA,item_name=item_name,item_description=item_description,item_price=item_price)
        else:
            item.name=item_name
            item.price=item_price
            item.description=item_description
            if item_picture: item.picture=base64.b64decode(item_picture)
            item.put()
            self.log("item %s"%("created" if creation else "edited"))
            self.flash("'%s' was %s!"%(item_name,"created" if creation else "edited"))
            self.redirect(self.current_user.url())
    def post(self):
        self.commit_item_changes()
def my_item_from_ident(handler,ident,allow_admin=False):
    try:
        item=Item.get_by_token(ident)
    except:
        handler.abort(404)
    if not item: handler.abort(404)
    if item.parent_key()!=handler.current_user.key() and not (allow_admin and handler.current_user.admin): handler.abort(404)
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
            item=Item.get_by_token(ident)
        except:
            self.abort(404)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user): self.abort(403)
        if item.picture is None:
            return self.redirect('/images/item.svg')
        self.response.headers['Content-Type']='image/png'
        self.cache()
        self.response.out.write(item.picture)
class ShowItemHandler(BaseHandler):
    def get(self,ident):
        try:
            item=Item.get_by_token(ident)
        except:
            self.abort(404)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user): self.abort(403)
        query=lambda: ItemRating.all().filter('item =',item)
        if self.current_user:
            ratings=QueryEnsuringAncestor(query=query,ancestor=self.current_user,limit=50,order='-time')
        else:
            ratings=query().order('-time').run(limit=50)
        self.render_template('items/show.html',item=item,ratings=ratings)
class RateItemHandler(BaseHandler):
    def post(self,ident):
        item=Item.get_by_token(ident)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user) or self.current_user.key()==item.parent_key(): self.abort(403)
        try:
            rating=(int(self.request.get('rating'))/20)*20
        except:
            rating=0
        if rating or self.request.get('contents')!='null':
            r=ItemRating(parent=self.current_user,contents=rich_text.from_style_runs(self.request.get('contents')),item=item,rating=rating)
            r.put()
            r.apply()
            self.log('rating created')
            self.flash("Rating added!")
        else:
            self.flash("You must include either a message or a numerical rating in order for it to be submitted.")
        self.redirect(item.url())
    
class CommunicateItemHandler(BaseHandler):
    def post(self,ident):
        try:
            item=Item.get_by_token(ident)
        except:
            self.abort(404)
        if not item: self.abort(404)
        if not item.viewable_by(self.current_user): self.abort(403)
        c=Communique(users=[self.current_user.key(),item.parent_key()],title=item.communique_title)
        c.put()
        c.add_user_communiques()
        self.response.out.write(str(c.key().id_or_name()))
class DeleteRatingHandler(BaseHandler):
    def post(self):
        if not self.current_user.admin: return self.abort(403)
        rating=ItemRating.get(Key(self.request.get('rating')))
        item=rating.item
        rating.unapply()
        rating.delete()
        self.log("rating deleted")
        self.redirect(item.url())
    
app = webapp2.WSGIApplication([
    ('/',IndexHandler),
    ('/search',SearchHandler),
    ('/items/add',AddItemHandler),
    (r'/items/delete-rating',DeleteRatingHandler),
    (r'/items/([A-Za-z0-9]+)/.*/edit',EditItemHandler),
    (r'/items/([A-Za-z0-9]+)/edit',EditItemHandler),
    (r'/items/([A-Za-z0-9]+)/.*/rate',RateItemHandler),
    (r'/items/([A-Za-z0-9]+)/rate',RateItemHandler),
    (r'/items/([A-Za-z0-9]+)/.*/picture',ItemPictureHandler),
    (r'/items/([A-Za-z0-9]+)/picture',ItemPictureHandler),
    (r'/items/([A-Za-z0-9]+)/.*/delete',DeleteItemHandler),
    (r'/items/([A-Za-z0-9]+)/delete',DeleteItemHandler),
    (r'/items/([A-Za-z0-9]+)/.*/communicate',CommunicateItemHandler),
    (r'/items/([A-Za-z0-9]+)/communicate',CommunicateItemHandler),
    (r'/items/([A-Za-z0-9]+)/.*',ShowItemHandler),
    (r'/items/([A-Za-z0-9]+)',ShowItemHandler),
], debug=(env.env==env.DEVELOPMENT))