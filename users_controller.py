import webapp2
from handlers import BaseHandler,AdminHandler
import env
from models import StoreUser,Item

class UserFindingHandler(BaseHandler):
    def inner_dispatch(self):
        try:
            self.user=StoreUser.get_by_id(int(self.request.route_args[0]))
        except ValueError:
            self.user=StoreUser.get_by_email(self.request.route_args[0])
        if self.user:
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
class UserDeletionHandler(UserFindingHandler):
    def get(self,user_id):
        if self.current_user.key()!=self.user.key(): return self.abort(403)
        self.render_template('users/delete.html')
    def post(self,user_id):
        if self.current_user.key()!=self.user.key(): return self.abort(403)
        self.current_user.delete_data()
        self.current_user.delete()
        self.log('user deleted')
        self.redirect(users.create_logout_url('/'))
class UserDeactivationHandler(AdminHandler,UserFindingHandler):
    pass
app = webapp2.WSGIApplication([
    (r'/users/(.*)/delete',UserDeletionHandler),
    (r'/users/(.*)',UserProfileHandler),
    (r'/users/(.*)/',UserProfileHandler)
], debug=(env.env==env.DEVELOPMENT))
