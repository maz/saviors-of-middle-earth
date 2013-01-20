import webapp2
from handlers import BaseHandler,AdminHandler

class MainPage(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.render_template("index.html",test_str="<b>Str</b>")
    def post(self):
        self.response.headers['Content-Type']='text/plain'
        self.response.write('you have arrived!')

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)