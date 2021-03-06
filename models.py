from google.appengine.ext import db
from google.appengine.ext.db import metadata
from google.appengine.api import users
from datetime import timedelta,datetime
import re
from webapp2_extras.security import generate_random_string
from google.appengine.api.channel import send_message
import json
from google.appengine.api import search
from itertools import chain
import json
import os
import hashlib
import logging

ITEM_SEARCH_INDEX_NAME="ITEM_SEARCH_INDEX_NAME"

class Item(db.Model):
    EXPIRATION_DELTA=timedelta(days=16)
    SEARCH_EXPIRATION_DELTA=timedelta(days=16,hours=1)
    
    NON_ALNUM_REGEX=re.compile(r'[^A-Za-z0-9]')
    
    token=db.StringProperty()
    
    name=db.StringProperty()
    price=db.FloatProperty()
    description=db.TextProperty()
    creation_time=db.DateTimeProperty(auto_now_add=True)
    
    rating_count=db.IntegerProperty(default=0)
    avg_rating=db.FloatProperty(default=0.0)
    
    picture=db.BlobProperty()
    
    @classmethod
    def get_by_token(cls,token):
        arr=cls.all().filter('token =',token).fetch(limit=1)
        if arr and len(arr):
            return arr[0]
        else:
            return None
    @staticmethod
    def search_index():
        return search.Index(ITEM_SEARCH_INDEX_NAME)
    @property
    def search_document(self):
        return search.Document(doc_id=str(self.key()),fields=[
            search.TextField(name='name',value=self.name),
            search.NumberField(name='price',value=self.price),
            search.HtmlField(name='description',value=self.description)
        ])
    def put(self):
        if not self.token:
            self.token=generate_random_string(5)
        super(Item,self).put()
        Item.search_index().put(self.search_document)
    def delete(self):
        Item.search_index().delete(str(self.key()))
        for rating in ItemRating.all().filter('item =',self).run(limit=None): rating.delete()
        super(Item,self).delete()
    @staticmethod
    def price_string(x): return "$%s"%(re.sub(r'(\d\d\d)(\d)',lambda match: "%s,%s"%(match.group(1),match.group(2)),("%.2f"%x)[::-1]))[::-1]
    @property
    def communique_title(self):
        return "%s: %s"%(self.name,self.price_string(self.price))
    def viewable_by(self,user):
        return self.creation_time>Item.expiry_cutoff() or (user and (user.admin or user.key()==self.parent_key()))
    def removeable_by(self,user):
        return user and (user.admin or user.key()==self.parent_key())
    def expiration(self):
        return self.creation_time+Item.EXPIRATION_DELTA
    def url_name(self):
        return re.sub(Item.NON_ALNUM_REGEX,'-',self.name)
    def url(self,named=True,action=""):
        if action=="show": action=""
        if action!="" and not action.startswith("/"): action="/%s"%action
        if named:
            return "/items/%s/%s%s"%(self.token,self.url_name(),action)
        else:
            return "/items/%s%s"%(self.token,action)
    @classmethod
    def expiry_cutoff(cls):
        return datetime.now()-cls.EXPIRATION_DELTA
    @classmethod
    def search_expiry_cutoff(cls):
        return datetime.now()-cls.SEARCH_EXPIRATION_DELTA
    @classmethod
    def fresh(cls,base=None):#'fresh' means not expired
        if not base: base=cls.all()
        return base.filter('creation_time >=',cls.expiry_cutoff())
    @classmethod
    def expired(cls,base=None):#'fresh' means not expired
        if not base: base=cls.all()
        return base.filter('creation_time <',cls.expiry_cutoff())

class ItemRating(db.Model):
    contents=db.TextProperty()
    item=db.ReferenceProperty(Item)
    rating=db.RatingProperty()
    time=db.DateTimeProperty(auto_now_add=True)
    def apply(self):
        if self.rating==0: return   #assume zero rating is no numerical rating associated
        self.item.avg_rating=(self.item.avg_rating*float(self.item.rating_count)+float(self.rating))/(float(self.item.rating_count+1))
        self.item.rating_count+=1
        self.item.put()
    def unapply(self):
        if self.rating==0: return
        item=self.item
        item.avg_rating=(float(item.rating_count)*float(item.avg_rating))-float(self.rating)
        item.rating_count-=1
        item.avg_rating/=float(item.rating_count)
        item.put()
    def deletion_memcache_key(self):
        return "rating-deleted-%s"%str(self.key())

class LogEntry(db.Model):
    ip=db.StringProperty(indexed=False)
    time=db.DateTimeProperty(auto_now_add=True)
    user=db.ReferenceProperty(indexed=False)
    msg=db.StringProperty(indexed=False)
    referrer=db.StringProperty(indexed=False)

class StoreUser(db.Model):
    admin=db.BooleanProperty(default=False)
    deactivated=db.BooleanProperty(default=False,indexed=False)
    email=db.StringProperty()
    
    nickname=db.StringProperty(indexed=False)
    description=db.TextProperty(default="")
    
    thumbnail=db.BlobProperty()
    image=db.BlobProperty()
    
    has_unread_messages=db.BooleanProperty(default=False)
    channel_tokens=db.StringListProperty()
    
    def notify_channels(self,action,**kwargs):
        kwargs=dict(kwargs)
        kwargs['action']=action
        encoded=json.dumps(kwargs)
        for token in self.channel_tokens:
            send_message(token,encoded)
    def generate_channel_token_string(self): return "%s_%s"%(str(self.key().id_or_name()),generate_random_string(24))
    def generate_channel_token(self):
        token=self.generate_channel_token_string()
        while token in self.channel_tokens: token=self.generate_channel_token_string()
        return token
    def deactivate(self):
        self.deactivated=True
        self.put()
        self.delete_data()
    def promote(self):
        self.admin=True
        self.put()
    def owned_items(self):
        return Item.all().ancestor(self)
    def url(self,action=None):
        if action:
            return "/users/%s/%s"%(str(self.key().id_or_name()),action)
        else:
            return "/users/%s"%str(self.key().id_or_name())
    @classmethod
    def by_id_or_name(cls, name_or_id):
        try:
            user=cls.get_by_id(int(name_or_id))
            if user is not None: return user
        except ValueError: pass #it's not a number
        return StoreUser.get_by_key_name(name_or_id)  
    @classmethod
    def by_email(cls,email):
        arr=cls.all().filter("email =",email).fetch(limit=1)
        if len(arr):
            return arr[0]
        else:
            return None
    @classmethod
    def current_user(cls):
        user=users.get_current_user()
        if not user: return None
        user_id=hashlib.sha256(user.user_id()).hexdigest()
        model=cls.get_by_key_name(user_id)
        if model is not None:
            if model.email!=user.email():
                model.email=user.email()
                model.put()
            return model
        else:
            model=cls(key_name=user_id,admin=users.is_current_user_admin() or user.email() in ["hardcodetest1@gmail.com","hardcodetest2@gmail.com"],email=user.email())
            model.put()
            model.nickname="User %s"%(model.key().id_or_name()[0:10])
            model.put()
            return model
    def google_user(self):
        return users.User(_user_id=self.userid)
    def delete_data(self):
        #TODO: add other models here, as they get added to the database
        #TODO: what to do with messages?
        for itm in self.owned_items().run(): itm.delete()
        for rating in ItemRating.all().ancestor(self).filter('user =',self).run(limit=None):
            rating.unapply()
            rating.delete()
    def communiques(self):
        return Communique.all().filter('users =',self.key())

class UserCommunique(db.Model):
    time=db.DateTimeProperty(auto_now=True)
    communique=db.ReferenceProperty(collection_name="communique_collection")

class Communique(db.Model):
    EPOCH=datetime.fromtimestamp(0)
    users=db.ListProperty(db.Key)
    last_message_sent=db.DateTimeProperty(auto_now_add=True)
    title=db.StringProperty()
    def add_user_communiques(self):
        for user in self.users:
            UserCommunique(parent=user,communique=self).put()
    def post_message(self,sender,contents):
        Message(communique=self,user=sender,contents=contents).put()
        LogEntry(msg="message posted to communique '%s' with users %s"%(self.title,','.join(map(str,map(db.Key.id,self.users))))).put()
        for user in self.users:
            if user!=sender.key():
                user_obj=StoreUser.get(user)
                user_obj.notify_channels('new_message',user=sender.key().id_or_name(),nickname=sender.nickname,communique=self.key().id_or_name(),contents=contents)
                if not user_obj.has_unread_messages:
                    user_obj.has_unread_messages=True
                    user_obj.put()
    def messages(self):
        return Message.all().filter('communique =',self.key()).order('-time')
    def last_read_by(self,user):
        if isinstance(user,db.Key):
            user=StoreUser.get(user)
        if user.has_unread_messages:
            user.has_unread_messages=False
            user.put()
        arr=UserCommunique.all().ancestor(user).filter('communique =',self).fetch(limit=1,projection=['time'])
        if arr and len(arr):
            return arr[0].time
        else:
            return Communique.EPOCH
    def read_by(self,user):
        arr=UserCommunique.all().ancestor(user).filter('communique =',self).fetch(limit=1)
        if arr and len(arr):
            arr[0].put()
        else:
            UserCommunique(parent=user,communique=self).put()

class Message(db.Model):
    communique=db.ReferenceProperty(Communique,collection_name="messages_collection")
    time=db.DateTimeProperty(auto_now_add=True)
    user=db.ReferenceProperty()
    contents=db.StringProperty()

def QueryEnsuringAncestor(query,ancestor,limit,order=None):
    neg=(order.index('-')==0)
    if neg: order=order.replace('-','')
    class key_comparer(object):
        def __init__(self,obj):
            self.obj=obj
        def __hash__(self):
            return hash(self.obj.key())
        def __eq__(self,obj):
            return self.obj.key()==obj.obj.key()
        def __cmp__(self,obj):
            if self.__eq__(obj): return 0
            return cmp(getattr(self.obj,order),getattr(obj.obj,order))
    return map(lambda x: x.obj,sorted(set(map(key_comparer,chain(query().order(order).run(limit=limit),query().order(order).ancestor(ancestor).run(limit=limit)))),reverse=neg))

class ModelInitializer(object):
    _initialized_state=False
    @staticmethod
    def initialized():
        if not ModelInitializer._initialized_state:
            #let's be atomic here:
            if len(metadata.get_kinds(start='A',end='Z'))!=0:
                ModelInitializer._initialized_state=True
        return ModelInitializer._initialized_state
    @staticmethod
    def initialize():
        f=open(os.path.join(os.path.dirname(__file__),'fixtures.json'),'r')
        all_data=json.load(f)
        f.close()
        data=all_data['users']
        reviews=all_data['reviews']
        items={}
        users={}
        for name in data.keys():
            user=StoreUser(nickname=name,email="%s@example.com"%name.lower())
            user.put()
            users[name]=user.key()
            if not data[name]: continue
            @db.transactional
            def add_products():
                for pdata in data[name]:
                    itm=Item(parent=user,name=pdata['name'],rating_count=pdata['rating_count'],avg_rating=pdata['avg_rating'],description=pdata['description'],price=float(pdata['price']),creation_time=datetime.utcfromtimestamp(pdata['creation']))
                    itm.put()
                    items[pdata['id']]=itm.key()
            add_products()
        for name in reviews.keys():
            user=users[name]
            @db.transactional
            def add_reviews():
                for review in reviews[name]:
                    ItemRating(parent=user,contents=review['text'],item=items[review['product']],rating=review['rating']).put()
            add_reviews()