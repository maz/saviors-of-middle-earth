from google.appengine.ext import db
from google.appengine.api import users

class Item(db.Model):
    name=db.StringProperty()
    owner=db.ReferenceProperty()
    price=db.FloatProperty()
    description=db.StringProperty(multiline=True)
    creation_time=db.DateTimeProperty(auto_now_add=True)

class LogEntry(db.Model):
    ip=db.StringProperty()
    time=db.DateTimeProperty(auto_now_add=True)
    user=db.ReferenceProperty()
    msg=db.StringProperty()

class StoreUser(db.Model):
    userid=db.StringProperty()
    admin=db.BooleanProperty()
    deactivated=db.BooleanProperty(default=False)
    @classmethod
    def current_user(cls):
        user=users.get_current_user()
        if not user: return None
        arr=cls.gql("WHERE userid=:1",user.user_id()).fetch(limit=1)
        if len(arr):
            return arr[0]
        else:
            model=cls(userid=user.user_id(),admin=is_current_user_admin() or user.email() in ["hardcodetest1@gmail.com","hardcodetest2@gmail.com"])
            model.put()
            return model
    def google_user(self):
        return users.User(_user_id=self.userid)