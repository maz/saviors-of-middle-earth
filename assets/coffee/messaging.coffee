socket=null

message_audio=null
play_message_notification=->
	message_audio.currentTime=0
	message_audio.play()

focused=true

#we want to know whether our window is currently active, hence the use of focus/blur instead of the page visibility API
window.addEventListener 'focus',-> focused=true
window.addEventListener 'blur',-> focused=false

$=(id)->document.getElementById(id)

overlay=null
loading=null
sidebar=null

overlay.show=-> overlay.style.display='block'
overlay.hide=-> overlay.style.display='none'
loading.show=->
	overlay.show()
	loading.style.display='block'
loading.hide=-> loading.style.display='none'

communique_cache=null

#TODO: property handle xhr onerror(s)

class Communique
	constructor:(data)->
		communique_cache[data.id]=this
		@unread=data.unread
		@id=data.id
		@users=data.users
		
		@dom=document.createElement('div')
		@dom.setAttribute('data-id',data.id)
		@dom.classList.add('communique')
		@dom.classList.add('unread') if data.unread
		@dom.textContent=data.users.join(', ')
		if sidebar.childNodes[0] then sidebar.insertBefore(@dom,sidebar.childNodes[0]) else sidebar.appendChild(@dom)

window.addEventListener 'load',->
	message_audio=new Audio
	message_audio.src="/sounds/message.wav"
	message_audio.load()
	
	channel=new goog.appengine.Channel(document.body.getAttribute('data-channel-token'))
	socket=channel.open()
	socket.onmessage=(evt)->
		msg=JSON.parse(evt.data)
		if msg.action is 'new_message'
			play_message_notification() if not focused
			if messages_panel.classList.contains('active')
				null
			else
				messages_opener.classList.add('attn')
	socket.onerror=socket.onclose=->
		null
	messages_panel=$('messages-panel')
	messages_opener=messages_panel.querySelector('.messages-opener')
	messages_opener.addEventListener 'click',->
		messages_panel.classList.toggle('active')
		messages_opener.textContent=if messages_panel.classList.contains('active') then "Close" else "Messages"
		messages_opener.classList.remove('attn')
		if messages_panel.classList.contains('active') and not communique_cache
			communique_cache={}
			loading.show()
			op=new XMLHttpRequest
			op.open 'get','/messaging/list',true
			op.responeType='json'
			op.onload=->
				for communique in op.response
					create_communique_dom(communique)
				loading.hide()
	,false
	overlay=messages_panel.querySelector('.overlay')
	loading=messages_panel.querySelector('.loading')
	sidebar=messages_panel.querySelector('.sidebar')
,false