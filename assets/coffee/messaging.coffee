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
messages_panel=null
messages_opener=null

communique_cache=null

#TODO: property handle xhr onerror(s)

empty_function= -> null

post_data=(dict)->
	arr=["csrf_token=#{encodeURIComponent(document.body.getAttribute('data-csrf-token'))}"]
	for own k,v of dict
		arr.push "#{encodeURIComponent(k)}=#{encodeURIComponent(v)}"
	return arr.join('&')

class Communique
	constructor:(data)->
		communique_cache[data.id]=this
		@unread=data.unread
		@id=data.id
		@users=data.users
		@messages=data.messages
		@more_messages=data.more_messages ? true
		@title=data.title
		
		@dom=document.createElement('div')
		@dom.setAttribute('data-id',data.id)
		@dom.classList.add('communique')
		@dom.classList.add('unread') if data.unread
		title=document.createElement('div')
		title.textContent=@title
		title.classList.add('title')
		@dom.appendChild(title)
		users=document.createElement('div')
		users.classList.add('users')
		users.textContent=data.users.join(', ')
		@dom.appendChild(users)
		@dom.addEventListener 'click',@select,false
		if sidebar.childNodes[0] then sidebar.insertBefore(@dom,sidebar.childNodes[0]) else sidebar.appendChild(@dom)
	loadMessages:(cb)->
		cb?=empty_function
		return cb() unless @more_messages
		op=new XMLHttpRequest
		op.open('get',"/messaging/#{@id}?onlymessages=1&offset=#{if @messages then @messages.length else 0}")
		loading.show()
		op.onload= =>
			resp=JSON.parse(op.responseText)
			@more_mesages=resp.more_messages
			@messages=resp.messages.concat(@messages)
			cb()
			loading.hide()
		op.send(null)
	loadMoreMessages:->
		@loadMessages()
	read:->
		@dom.classList.remove('unread')
		xhr=new XMLHttpRequest
		xhr.open('post',"/messaging/#{@id}/read_by",true)
		xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded")
		xhr.send(post_data())#we don't care about the result
	select:=>
		for com in sidebar.querySelectorAll('.communique.selected')
			com.classList.remove('selected')
		@dom.classList.add('selected')
		@read()

Communique.load_new=(id,cb)->
	cb?=empty_function
	op=new XMLHttpRequest
	op.open('get',"/messaging/#{id}",true)
	op.onload=->
		cb(new Communique(JSON.parse(op.responseText)))
		loading.hide()
	op.send(null)
	loading.show()
@MessagingLoadCommunique=(id,cb)->
	cb?=empty_function
	func=->
		Communique.load_new(id,cb)
	if communique_cache then func() else MessagingForceReload(cb)
@MessagingToggle=->
	messages_panel.classList.toggle('active')
	messages_opener.textContent=if messages_panel.classList.contains('active') then "Close" else "Messages"
	messages_opener.classList.remove('attn')
	if messages_panel.classList.contains('active') and not communique_cache
		MessagingForceReload()
MessagingForceReload=(cb)->
	cb?=empty_function
	communique_cache={}
	loading.show()
	op=new XMLHttpRequest
	op.open 'get','/messaging/list',true
	op.onload=->
		for communique in JSON.parse(op.responseText)
			new Communique(communique)
		loading.hide()
	op.send(null)
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
		MessagingToggle()
	,false
	overlay=messages_panel.querySelector('.overlay')
	loading=messages_panel.querySelector('.loading')
	sidebar=messages_panel.querySelector('.sidebar')
	overlay.show=-> overlay.style.display='block'
	overlay.hide=-> overlay.style.display='none'
	loading.show=->
		overlay.show()
		loading.style.display='block'
	loading.hide=-> loading.style.display='none'
,false