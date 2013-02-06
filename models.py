from google.appengine.ext import db
from google.appengine.api import users
from datetime import timedelta,datetime
import re
from webapp2_extras.security import generate_random_string
from google.appengine.api.channel import send_message
import json

class Item(db.Model):
    EXPIRATION_DELTA=timedelta(days=16)
    NON_ALNUM_REGEX=re.compile(r'[^A-Za-z0-9]')
    
    name=db.StringProperty()
    owner=db.ReferenceProperty()
    price=db.FloatProperty()
    description=db.TextProperty()
    creation_time=db.DateTimeProperty(auto_now_add=True)
    
    rating_count=db.IntegerProperty(default=0)
    avg_rating=db.FloatProperty(default=0.0)
    
    picture=db.BlobProperty()
    
    @staticmethod
    def price_string(x): return "$%s"%(re.sub(r'(\d\d\d)(\d)',lambda match: "%s,%s"%(match.group(1),match.group(2)),("%.2f"%x)[::-1]))[::-1]
    @property
    def communique_title(self):
        return "%s: %s"%(self.name,self.price_string(self.price))
    @property
    def expired(self):
    	return self.creation_time>=Item.expiry_cutoff()
    def viewable_by(self,user):
        return self.expired or (user and (user.admin or user.key()==self.owner.key()))
    def removeable_by(self,user):
        return user and (user.admin or user.key()==self.owner.key())
    def expiration(self):
        return self.creation_time+Item.EXPIRATION_DELTA
    def url_name(self):
        return re.sub(Item.NON_ALNUM_REGEX,'-',self.name)
    def url(self,named=True,action=""):
        if action=="show": action=""
        if action!="" and not action.startswith("/"): action="/%s"%action
        if named:
            return "/items/%d/%s%s"%(self.key().id(),self.url_name(),action)
        else:
            return "/items/%d%s"%(self.key().id(),action)
    @classmethod
    def expiry_cutoff(cls):
        return datetime.now()-cls.EXPIRATION_DELTA
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
    user=db.ReferenceProperty()
    rating=db.RatingProperty()
    time=db.DateTimeProperty(auto_now_add=True)
    def apply_rating(self):
        if self.rating==0: return#assume zero rating is no numerical rating associated
        self.item.avg_rating=(self.item.avg_rating*float(self.item.rating_count)+float(self.rating))/(float(self.item.rating_count+1))
        self.item.rating_count+=1
        self.item.put()

class LogEntry(db.Model):
    ip=db.StringProperty(indexed=False)
    time=db.DateTimeProperty(auto_now_add=True)
    user=db.ReferenceProperty(indexed=False)
    msg=db.StringProperty(indexed=False)
    referrer=db.StringProperty(indexed=False)

class StoreUser(db.Model):
    userid=db.StringProperty()
    admin=db.BooleanProperty()
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
    def generate_channel_token_string(self): return "%d_%s"%(self.key().id(),generate_random_string(24))
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
        return Item.all().filter("owner =",self.key())
    def url(self,action=None):
        if action:
            return "/users/%d/%s"%(self.key().id(),action)
        else:
            return "/users/%d"%self.key().id()
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
        arr=cls.gql("WHERE userid=:1",user.user_id()).fetch(limit=1)
        if len(arr):
            model=arr[0]
            if model.email!=user.email():
                model.email=user.email()
                model.put()
            return model
        else:
            model=cls(userid=user.user_id(),admin=users.is_current_user_admin() or user.email() in ["hardcodetest1@gmail.com","hardcodetest2@gmail.com"],email=user.email())
            model.put()
            model.nickname="User %d"%model.key().id()
            model.put()
            return model
    def google_user(self):
        return users.User(_user_id=self.userid)
    def delete_data(self):
        #TODO: add other models here, as they get added to the database
        #TODO: what to do with messages?
        for itm in self.owned_items().run(): itm.delete()
    def communiques(self):
        return Communique.all().filter('users =',self.key())

class UserLastRead(db.Model):
    time=db.DateTimeProperty(auto_now=True)
    user=db.ReferenceProperty(StoreUser,collection_name="user_collection")
    communique=db.ReferenceProperty(collection_name="communique_collection")

class Communique(db.Model):
    EPOCH=datetime.fromtimestamp(0)
    users=db.ListProperty(db.Key)
    last_message_sent=db.DateTimeProperty(auto_now_add=True)
    title=db.StringProperty()
    def post_message(self,sender,contents):
        Message(communique=self,user=sender,contents=contents).put()
        LogEntry(msg="message posted to communique '%s' with users %s"%(self.title,','.join(map(str,map(db.Key.id,self.users))))).put()
        for user in self.users:
            if user!=sender.key():
                user_obj=StoreUser.get(user)
                user_obj.notify_channels('new_message',user=sender.key().id(),communique=self.key().id(),contents=contents)
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
        arr=UserLastRead.all().filter('user =',user).filter('communique =',self).fetch(limit=1)
        if arr and len(arr):
            return arr[0].time
        else:
            return Communique.EPOCH
    def read_by(self,user):
        arr=UserLastRead.all().filter('user =',user).filter('communique =',self).fetch(limit=1)
        if arr and len(arr):
            arr[0].put()
        else:
            UserLastRead(user=user,communique=self).put()

class Message(db.Model):
    communique=db.ReferenceProperty(Communique,collection_name="messages_collection")
    time=db.DateTimeProperty(auto_now_add=True)
    user=db.ReferenceProperty()
    contents=db.StringProperty()