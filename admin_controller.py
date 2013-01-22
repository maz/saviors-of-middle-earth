import webapp2
from handlers import AdminHandler
import env
from google.appengine.api import users

class AdminIndex(AdminHandler):
    def get(self):
        self.render_template("admin/index.html")

app = webapp2.WSGIApplication([
    ('/admin',AdminIndex),
    ('/admin/',AdminIndex)
], debug=(env.env==env.DEVELOPMENT))
