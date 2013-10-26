import env
import webapp2
from handlers import BaseHandler

class FourOhFourHandler(BaseHandler):
    def inner_dispatch(self):
        self.render_template('404.html')

class ErrorHandlerAdapter(webapp2.Webapp2HandlerAdapter):
    def __call__(self, *args):
        return super(ErrorHandlerAdapter, self).__call__(*args[0:2])

def wsgi(handlers):
    app=webapp2.WSGIApplication(handlers, debug=(env.env==env.DEVELOPMENT))
    app.error_handlers[404]=ErrorHandlerAdapter(FourOhFourHandler)
    return app       