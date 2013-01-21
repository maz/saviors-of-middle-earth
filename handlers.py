import webapp2
from webapp2_extras.security import generate_random_string
from webapp2_extras import sessions
from webapp2_extras import jinja2
from jinja2 import Markup
from models import LogEntry,StoreUser

sessions.default_config['secret_key']="2vCmFcbxs4G4D8DiiGMLPQmSm8vun57ffl0lq5Wt"
sessions.default_config['cookie_args']['httponly']=True

jinja2.default_config['template_path']='views'

class BaseHandler(webapp2.RequestHandler):
    def log(self,msg):
        db.put_async(LogEntry(ip=self.request.remote_addr,user=(self.current_user.key() if self.current_user else None),msg=msg))
    def inner_dispatch(self):
        self.current_user=StoreUser.current_user()
        webapp2.RequestHandler.dispatch(self)
    def gmt_offset(self):
        if self.current_user and self.current_user.gmt_offset!=24: return self.current_user.gmt_offset
        if self.request.cookies.get('gmt_offset'): return float(self.request.cookies.get('gmt_offset'))
        return 0
    def convert_datetime(self,dt):
        return dt.astimezone(self.gmt_offset())
    def dispatch(self):
        self.session_store=sessions.get_store(request=self.request)
        try:
            if self.request.method not in ['GET','HEAD']:
                csrf_token=self.session.get('csrf_token')
                if (not csrf_token) or csrf_token!=self.request.get('csrf_token'):
                    self.abort(403)
            elif not self.session.get('csrf_token'):
                self.session['csrf_token']=generate_random_string(48)
            self.inner_dispatch()
        finally:
            self.session_store.save_sessions(self.response)
    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)
    def render_template(self,name,**values):
        values=dict(values)
        values['Markup']=Markup#there is probably a better way to add helper functions
        values['current_user']=self.current_user
        self.response.write(self.jinja2.render_template(name,**values))

class AdminHandler(BaseHandler):
    def inner_dispatch(self):
        user=StoreUser.current_user()
        if not user or not user.admin: self.abort(403)
        BaseHandler.inner_dispatch(self)