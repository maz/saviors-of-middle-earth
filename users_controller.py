import webapp2
from handlers import BaseHandler,AdminHandler
import env
from models import StoreUser,Item
from google.appengine.api import users
import base64
import rich_text

class UserLogoutHandler(BaseHandler):
    accessible_by_deactivated_users=True
    def get(self):
        self.session['csrf_token']=''#clear the CSRF token
        self.redirect(users.create_logout_url("/"))

class UserFindingHandler(BaseHandler):
    def inner_dispatch(self):
        self.user=StoreUser.by_name_or_id(self.request.route_args[0])
        if self.user is None:
            self.user=StoreUser.by_email(self.request.route_args[0])
        if self.user is not None:
            super(UserFindingHandler,self).inner_dispatch()
        else:
            self.flash("No user with email '%s' could be found."%self.request.route_args[0])
            self.redirect('/')

class UserProfileHandler(UserFindingHandler):
    def get(self,user_id):
        self.render_template('users/user.html',user=self.user,
            fresh_items=Item.fresh(self.user.owned_items()).order('-creation_time').run(),
            expired_items=Item.expired(self.user.owned_items()).order('-creation_time').run() if self.current_user and (self.current_user.admin or self.current_user.key()==self.user.key()) else []
        )
class UserPictureHandler(UserFindingHandler):
    def get(self,user_id):
        if self.user.image is None:
            return self.redirect('/images/user.svg')
        self.response.headers['Content-Type']='image/png'
        self.cache()
        self.response.out.write(self.user.image)
class UserThumbnailHandler(UserFindingHandler):
    def get(self,user_id):
        if self.user.image is None:
            return self.redirect('/images/user.svg')
        self.response.headers['Content-Type']='image/png'
        self.cache()
        self.response.out.write(self.user.thumbnail)
class UserNicknameHandler(UserFindingHandler):
    def get(self,user_id):
        self.response.headers['Content-Type']='text/plain'
        self.response.out.write(self.user.nickname)
    def post(self,user_id):
        if self.user.key()!=self.current_user.key():
            return self.abort(403)
        if len(self.request.get('nickname').strip()) !=0:
            self.user.nickname=self.request.get('nickname')
            self.user.put()
        self.log('nickname changed')
        self.redirect(self.user.url())
class UserSetPictureHandler(UserFindingHandler):
    def post(self,user_id):
        if self.current_user.key()!=self.user.key(): return self.abort(403)
        self.current_user.image=base64.b64decode(self.request.get('picture_512'))
        self.current_user.thumbnail=base64.b64decode(self.request.get('picture_72'))
        self.current_user.put()
        self.log('user picture changed')
        self.redirect(self.current_user.url())
class UserDeletionHandler(UserFindingHandler):
    def get(self,user_id):
        if self.current_user.key()!=self.user.key(): return self.abort(403)
        self.render_template('users/delete.html')
    def post(self,user_id):
        if self.current_user.key()!=self.user.key(): return self.abort(403)
        self.current_user.delete_data()
        self.current_user.delete()
        self.log('user deleted')
        self.redirect("/users/logout")
class UserDescriptionHandler(UserFindingHandler):
    def post(self,user_id):
        if self.current_user.key()!=self.user.key(): return self.abort(403)
        self.current_user.description=rich_text.from_style_runs(self.request.get('description'))
        self.current_user.put()
        self.log('user description changed')
        self.redirect(self.current_user.url())
class UserPromotionHandler(AdminHandler,UserFindingHandler):
    def post(self,user_id):
        self.user.promote()
        self.log('user promoted')
        self.redirect(self.user.url())
class UserDeactivationHandler(AdminHandler,UserFindingHandler):
    def post(self,user_id):
        self.user.deactivate()
        self.log('user deactivated')
        self.redirect(self.user.url())
app = webapp2.WSGIApplication([
    (r'/users/logout',UserLogoutHandler),
    (r'/users/(.*)/delete',UserDeletionHandler),
    (r'/users/(.*)/picture',UserPictureHandler),
    (r'/users/(.*)/thumbnail',UserThumbnailHandler),
    (r'/users/(.*)/nickname',UserNicknameHandler),
    (r'/users/(.*)/description',UserDescriptionHandler),
    (r'/users/(.*)/set_picture',UserSetPictureHandler),
    (r'/users/(.*)/deactivate',UserDeactivationHandler),
    (r'/users/(.*)/promote',UserPromotionHandler),
    (r'/users/(.*)',UserProfileHandler),
    (r'/users/(.*)/',UserProfileHandler)
], debug=(env.env==env.DEVELOPMENT))
