import webapp2
from handlers import AdminHandler
import env
from models import LogEntry

class IndexHandler(AdminHandler):
    def get(self):
        self.render_template("admin/index.html")
class LogsHandler(AdminHandler):
    PER_PAGE=20
    def get(self):
        page=int(self.request.get('page')) if self.request.get('page') else 0
        offset=page*LogsHandler.PER_PAGE
        def generate_ctx():
            return LogEntry.all().order('-time')
        entries=generate_ctx().run(offset=offset,limit=LogsHandler.PER_PAGE)
        more_pages=generate_ctx().count(offset=offset+LogsHandler.PER_PAGE,limit=1)
        self.render_template("admin/logs.html",entries=entries,page=page,more_pages=more_pages)

app = webapp2.WSGIApplication([
    ('/admin',IndexHandler),
    ('/admin/',IndexHandler),
    ('/admin/logs',LogsHandler)
], debug=(env.env==env.DEVELOPMENT))
