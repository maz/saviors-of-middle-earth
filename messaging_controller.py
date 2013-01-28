import webapp2
import env
from models import StoreUser,Communique
from handlers import BaseHandler
import logging
import json

class ChannelConnectedHandler(webapp2.RequestHandler):
    def post(self):
        user=StoreUser.get_by_id(int(self.request.get('from').split('_')[0]))
        user.channel_tokens.append(self.request.get('from'))
        user.put()
class ChannelDisconnectedHandler(webapp2.RequestHandler):
    def post(self):
        results=StoreUser.all().filter('channel_tokens =',self.request.get('from')).fetch(limit=1)
        if results and len(results):
            user=results[0]
            user.channel_tokens.remove(self.request.get('from'))
            user.put()

class CommuniqueFindingHandler(BaseHandler):
    def inner_dispatch(self):
        try:
            self.communique=Communique.get_by_id(int(self.request.route_args[0]))
        except:
            self.communique=None
        if not self.communique: self.abort(404)
        if self.current_user.key() not in self.communique.users: self.abort(403)
        super(CommuniqueFindingHandler,self).inner_dispatch()

class MessagingPostHandler(CommuniqueFindingHandler):
    def post(self,communique_id):
        self.communique.post_message(sender=self.current_user,contents=self.request.get('message'))
class MessaingReadByHandler(CommuniqueFindingHandler):
    def post(self,communique_id):
        self.communique.read_by(self.current_user)
class MessagingListAllHandler(BaseHandler):
    def get(self):
        self.response.headers['Content-Type']='application/json'
        self.response.write(json.dumps(map(lambda com:dict(unread=com.last_message_sent>=com.last_read_by(self.current_user),id=com.key().id(),users=map(lambda user_id: StoreUser.get(user_id).nickname,com.users)),json.dumps(self.current_user.communiques().order('-last_message_sent').run()))))
class MessagingListHandler(CommuniqueFindingHandler):
    MESSAGES_PER_PAGE=50
    def get(self,communique_id):
        self.response.headers['Content-Type']='application/json'
        out={}
        referenced_users=set()
        def user_referenced(x):
            referenced_users.add(x)
            return x
        off=int(self.request.get('offset') or 0)
        out['messages']=map(lambda x: dict(more_pages=self.communique.messages().count(limit=1,offset=off+MessagingListHandler.MESSAGES_PER_PAGE+1),user=user_referenced(x.user.key().id()),contents=x.contents,time=x.time.isoformat()),self.communique.messages().run(limit=MessagingListHandler.MESSAGES_PER_PAGE,offset=off))
        out['users']=dict.fromkeys(referenced_users)
        #TODO: nicer way to do the following:
        for key in out['users'].keys():
            outs['users'][key]=StoreUser.by_id(key).nickname
        self.response.write(json.dumps(out))

app = webapp2.WSGIApplication([
    (r'/_ah/channel/connected/',ChannelConnectedHandler),
    (r'/_ah/channel/disconnected/',ChannelDisconnectedHandler),
    (r'/messaging/(\d+)/read_by',MessagingReadByHandler),
    (r'/messaging/(\d+)/post',MessagingPostHandler),
    (r'/messaging/list',MessagingListAllHandler),
    (r'/messaging/(\d+)',MessagingListHandler)
], debug=(env.env==env.DEVELOPMENT))
