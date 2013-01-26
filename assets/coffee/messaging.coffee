socket=null

window.addEventListener 'load',->
	channel=new goog.appengine.Channel(document.body.getAttribute('data-channel-token'))
	socket=channel.open()
	socket.onmessage=(evt)->
		msg=JSON.parse(evt.data)
		
	socket.onerror=socket.onclose=->
		null
,false