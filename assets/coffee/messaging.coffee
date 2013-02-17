socket=null

message_audio=null
play_message_notification=->
	message_audio.currentTime=0
	message_audio.play()

notifications=@webkitNotifications ? @notifications

notify_new_message=(msg)->
	play_message_notification()
	return unless notifications?
	notifications.createNotification("/users/#{msg.user}/thumbnail",
		"Message from '#{msg.nickname}'",
		msg.contents).show() if notifications.checkPermission()==0

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
selected_communique=null
messages=null
ta=null
message_group_template=null
messaging_title=null

communique_cache=null

#TODO: property handle xhr onerror(s)

empty_function= -> null

last= (arr)-> return arr[arr.length-1]

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
		@user_map=data.user_map
		
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
	newMessage:(msg)->
		if sidebar.childNodes[0] then sidebar.insertBefore(@dom,sidebar.childNodes[0]) else sidebar.appendChild(@dom)
		if selected_communique==this
			@render_message(msg)
			@read()
		else
			@dom.classList.add('unread')
	loadMessages:(cb)->
		cb?=empty_function
		return cb() unless @more_messages
		op=new XMLHttpRequest
		op.open('get',"/messaging/#{@id}?onlymessages=1&offset=#{if @messages then @messages.length else 0}")
		loading.show()
		op.onload= =>
			resp=JSON.parse(op.responseText)
			@more_mesages=resp.more_messages
			if @messages then @messages=resp.messages.concat(@messages) else @messages=resp.messages
			cb()
			loading.hide()
		op.send(null)
	read:->
		return unless unread
		@dom.classList.remove('unread')
		xhr=new XMLHttpRequest
		xhr.open('post',"/messaging/#{@id}/read_by",true)
		xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded")
		xhr.send(post_data())#we don't care about the result
	post:(msg)->
		@render_message(
			user: parseInt(document.body.getAttribute('data-current-user')),
			contents: msg
		)
		xhr=new XMLHttpRequest
		xhr.open('post',"/messaging/#{@id}/post",true)
		xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded")
		xhr.send(post_data(contents: msg))#TODO: what happens if this fails?
	render_message:(msg)->
		div=document.createElement('div')
		div.className='message'
		div.textContent=msg.contents
		if @last_rendered_group_user==msg.user
			group=last(messages.children)
		else
			@last_rendered_group_user=msg.user
			group=document.createElement('div')
			group.className='message-group'
			group.innerHTML=message_group_template.innerHTML
			pic=group.querySelector('.pic')
			pic.href="/users/#{msg.user}"
			pic.style.backgroundImage="url('/users/#{msg.user}/thumbnail')"
			group.querySelector('.name').textContent=@user_map[msg.user]
			messages.appendChild(group)
		#This is a nasty solution...
		div.style.top=group.style.minHeight
		group.insertBefore(div,group.querySelector('.clearer'))
		if group.style.minHeight
			group.style.minHeight="#{parseFloat(group.style.minHeight)+div.offsetHeight}px"
		else
			group.style.minHeight="#{div.offsetHeight}px"
	renderMessages:=>
		@last_rendered_group_user=null
		messages.innerHTML=""
		if @more_mesages
			button=document.createElement("input")
			button.type="button"
			button.value="Load More Messages"
			button.className="load-more-messages-button"
			button.addEventListener 'click',=>
				@loadMessages(@renderMessages)
			,false
			messages.appendChild(button)
		for msg in @messages
			@render_message(msg)
		overlay.hide()
		ta.focus()
	select:=>
		return if selected_communique==this
		selected_communique.dom.classList.remove('selected') if selected_communique
		@dom.classList.add('selected')
		@read()
		messaging_title.textContent=@title
		selected_communique=this
		ta.value=""
		if @messages then @renderMessages() else @loadMessages(@renderMessages)

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
	document.body.style.overflow=if messages_panel.classList.contains('active') then "hidden" else ""
	notifications.requestPermission() if notifications? and notifications.checkPermission()!=0 and messages_panel.classList.contains('active')
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
			
			notify_new_message(msg) if not focused
			if messages_panel.classList.contains('active')
				com=communique_cache[msg.communique]
				com.newMessage(msg) if com
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
	messages=messages_panel.querySelector('.messages')
	message_group_template=messages_panel.querySelector('.template[data-name=message-group]')
	messaging_title=messages_panel.querySelector('.title')
	ta=messages_panel.querySelector('textarea')
	ta.addEventListener 'keydown',(evt)->
		if !evt.shiftKey and evt.keyCode==13#enter key
			evt.preventDefault()
			selected_communique.post(ta.value) if selected_communique
			ta.value=""
	,false
	overlay.show=-> overlay.style.display='block'
	overlay.hide=-> overlay.style.display='none'
	loading.show=->
		overlay.show()
		loading.style.display='block'
	loading.hide=-> loading.style.display='none'
,false