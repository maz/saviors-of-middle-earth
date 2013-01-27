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

window.addEventListener 'load',->
	message_audio=new Audio
	message_audio.src="/sounds/message.wav"
	
	channel=new goog.appengine.Channel(document.body.getAttribute('data-channel-token'))
	socket=channel.open()
	socket.onmessage=(evt)->
		msg=JSON.parse(evt.data)
		if msg.action is 'new_message'
			play_message_notification() if not focused
	socket.onerror=socket.onclose=->
		null
	messages_panel=$('messages-panel')
	messages_panel.querySelector('.messages-opener').addEventListener 'click',->
		messages_panel.classList.toggle('active')
	,false
,false