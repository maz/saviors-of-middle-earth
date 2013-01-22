from google.appengine.ext import db
from google.appengine.api import users
from datetime import timedelta,datetime
import re

class Item(db.Model):
    EXPIRATION_DELTA=timedelta(days=16)
    NON_ALNUM_REGEX=re.compile(r'[^A-Za-z0-9]')
    name=db.StringProperty()
    owner=db.ReferenceProperty()
    price=db.FloatProperty()
    description=db.StringProperty(multiline=True)
    creation_time=db.DateTimeProperty(auto_now_add=True)
    def viewable_by(self,user):
        return user.admin or user==self.owner or self.creation_time>=Item.expiry_cutoff()
    def removeable_by(self,user):
        return user.admin or user==self.owner
    def expiration(self):
        return self.creation_time+EXPIRATION_DELTA
    def url_name(self):
        return re.sub(NON_ALNUM_REGEX,'-',self.name)
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
        return base.filter('creation_time <',cls.expiry_cutoff())
    @classmethod
    def expired(cls,base=None):#'fresh' means not expired
        if not base: base=cls.all()
        return base.filter('creation_time >=',cls.expiry_cutoff())

class LogEntry(db.Model):
    ip=db.StringProperty()
    time=db.DateTimeProperty(auto_now_add=True)
    user=db.ReferenceProperty()
    msg=db.StringProperty()

class StoreUser(db.Model):
    userid=db.StringProperty()
    admin=db.BooleanProperty()
    deactivated=db.BooleanProperty(default=False)
    gmt_offset=db.FloatProperty(default=float(24))#24=autodetect
    def owned_items(self):
        return Item.all().filter("owner =",self.key())
    @classmethod
    def current_user(cls):
        user=users.get_current_user()
        if not user: return None
        arr=cls.gql("WHERE userid=:1",user.user_id()).fetch(limit=1)
        if len(arr):
            return arr[0]
        else:
            model=cls(userid=user.user_id(),admin=users.is_current_user_admin() or user.email() in ["hardcodetest1@gmail.com","hardcodetest2@gmail.com"])
            model.put()
            return model
    def google_user(self):
        return users.User(_user_id=self.userid)