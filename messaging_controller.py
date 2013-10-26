import webapp2
import env
from wsgi import wsgi
from models import StoreUser,Communique,UserCommunique
from handlers import BaseHandler
import logging
import json

def generate_user_map(com):
    d=dict()
    for user in com.users:
        d[user.id_or_name()]=StoreUser.get(user).nickname
    return d

class ChannelConnectedHandler(webapp2.RequestHandler):
    def post(self):
        user=StoreUser.by_id_or_name(self.request.get('from').split('_')[0])
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
        self.communique.post_message(sender=self.current_user,contents=self.request.get('contents'))
class MessagingReadByHandler(CommuniqueFindingHandler):
    def post(self,communique_id):
        self.communique.read_by(self.current_user)
class MessagingListAllHandler(BaseHandler):
    def get(self):
        self.response.headers['Content-Type']='application/json'
        self.response.write(json.dumps(map(lambda com:dict(title=com.title
            ,unread=com.last_message_sent>=com.last_read_by(self.current_user),
            id=com.key().id_or_name(),
            user_map=generate_user_map(com),
            users=map(lambda user_id: StoreUser.get(user_id).nickname,com.users)),sorted(map(lambda uc:uc.communique,UserCommunique.all().ancestor(self.current_user).run()),key=lambda com_x: com_x.last_message_sent,reverse=True))))
class MessagingListHandler(CommuniqueFindingHandler):
    MESSAGES_PER_PAGE=50
    def get(self,communique_id):
        self.response.headers['Content-Type']='application/json'
        out={}
        off=int(self.request.get('offset') or 0)
        out['more_messages']=self.communique.messages().count(limit=1,offset=off+MessagingListHandler.MESSAGES_PER_PAGE+1)
        out['messages']=map(lambda x: dict(user=x.user.key().id_or_name(),contents=x.contents,time=x.time.isoformat()),self.communique.messages().run(limit=MessagingListHandler.MESSAGES_PER_PAGE,offset=off))
        out['messages'].reverse()
        if not self.request.get('onlymessages'):
            out['user_map']=generate_user_map(self.communique)
            out['id']=int(communique_id)
            out['unread']=self.communique.last_message_sent>=self.communique.last_read_by(self.current_user)
            out['title']=self.communique.title
            #TODO: nicer way to do the following:
            for key in out['users'].keys():
                outs['users'][key]=StoreUser.by_id_or_name(key).nickname
        self.response.write(json.dumps(out))
class MessagingAddHandler(CommuniqueFindingHandler):
    def post(self,communique_id):
        self.response.headers['Content-Type']='text/plain'
        u=StoreUser.by_id_or_name(self.request.get('user'))
        if u.key() in self.communique.users:
            return halt(400)
        self.communique.users.append(u.key())
        self.communique.put()
        UserCommunique(parent=u,communique=self.communique).put()
app = wsgi([
    (r'/_ah/channel/connected/',ChannelConnectedHandler),
    (r'/_ah/channel/disconnected/',ChannelDisconnectedHandler),
    (r'/messaging/(\d+)/read_by',MessagingReadByHandler),
    (r'/messaging/(\d+)/post',MessagingPostHandler),
    (r'/messaging/list',MessagingListAllHandler),
    (r'/messaging/(\d+)/add',MessagingAddHandler),
    (r'/messaging/(\d+)',MessagingListHandler)
])
