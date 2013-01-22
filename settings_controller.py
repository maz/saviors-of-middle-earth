import webapp2
from handlers import BaseHandler
import env
from google.appengine.api import users

class SettingsIndex(BaseHandler):
    def get(self):
        self.render_template('settings/index.html')
class SettingsDelete(BaseHandler):
    def get(self):
        self.render_template('settings/delete.html')
    def post(self):
        self.current_user.delete_data()
        self.log('user deleted')
        self.redirect(users.create_logout_url('/'))
app = webapp2.WSGIApplication([
    ('/settings',SettingsIndex),
    ('/settings/',SettingsIndex),
    ('/settings/delete',SettingsDelete)
], debug=(env.env==env.DEVELOPMENT))
