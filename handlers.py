import webapp2
from webapp2_extras.security import generate_random_string
from webapp2_extras import sessions
from webapp2_extras import jinja2
from jinja2 import Markup
from models import LogEntry,StoreUser
from datetime import tzinfo,timedelta
import logging
from google.appengine.api import users
from google.appengine.ext import db

sessions.default_config['secret_key']="2vCmFcbxs4G4D8DiiGMLPQmSm8vun57ffl0lq5Wt"
sessions.default_config['cookie_args']['httponly']=True

jinja2.default_config['template_path']='views'
jinja2.default_config['filters']={}
jinja2.default_config['filters']['Markup']=Markup
jinja2.default_config['filters']['login_url']=users.create_login_url
jinja2.default_config['filters']['logout_url']=users.create_logout_url
def generate_url(x,*args,**kwargs):
    return x.url(*args,**kwargs)
jinja2.default_config['filters']['url']=generate_url
jinja2.default_config['filters']['date']=lambda x: x.strftime("%m/%d/%y")
jinja2.default_config['filters']['price']=lambda x: "$%.2f"%x

class FixedTimeZone(tzinfo):
    def __init__(self,offset):
        self.__offset=timedelta(hours=offset)
    def utcoffset(self,dt):
        return self.__offset
    def tzname(self,dt):
        return "USER"
    def dst(self,dt):
        return timedelta(0)

UTC=FixedTimeZone(0)

class BaseHandler(webapp2.RequestHandler):
    def log(self,msg):
        db.put_async(LogEntry(ip=self.request.remote_addr,user=(self.current_user.key() if self.current_user else None),msg=msg))
    def handle_exception(self,exception,debug):
        if isinstance(exception,webapp2.HTTPException):
            if exception.code==403:
                #TODO: 403 error page
                self.response.set_status(403)
                self.response.write('403!')
                self.log("Unauthorized attempt to access '%s'"%self.request.path_info)
                return
            elif exception.code==404:
                #TODO: 404 error page
                self.response.set_status(404)
                self.response.write('404!')
                return
        webapp2.RequestHandler.handle_exception(self,exception,debug)
    def inner_dispatch(self):
        self.current_user=StoreUser.current_user()
        webapp2.RequestHandler.dispatch(self)
    def gmt_offset_hours(self):
        if self.current_user and self.current_user.gmt_offset!=24: return self.current_user.gmt_offset
        if self.request.cookies.get('gmt_offset'): return float(self.request.cookies.get('gmt_offset'))
        return 0
    def gmt_offset(self):
        return FixedTimeZone(self.gmt_offset_hours())
    def convert_datetime(self,dt):
        if not dt.tzinfo: dt=dt.replace(tzinfo=UTC)
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
        values['current_user']=self.current_user
        values['path']=self.request.path_info
        values['csrf_token']=self.session['csrf_token']
        def convert_datetime(x):
            return self.convert_datetime(x)
        values['convert_datetime']=convert_datetime#this is bound to self, so it can't be a normal filter
        self.response.headers['Content-Type']="text/html; charset=utf-8"#assume that our templates are for html
        self.response.write(self.jinja2.render_template(name,**values))

class AdminHandler(BaseHandler):
    def inner_dispatch(self):
        user=StoreUser.current_user()
        if not user or not user.admin: self.abort(403)
        BaseHandler.inner_dispatch(self)