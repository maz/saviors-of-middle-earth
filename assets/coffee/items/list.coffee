window.addEventListener 'load',->
	for button in document.querySelectorAll('.item-communicate-button')
		do (button)->
			button.addEventListener 'click',->
				xhr=new XMLHttpRequest
				xhr.open('post',"/items/#{button.getAttribute('data-item')}/communicate",true)
				xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded")
				xhr.onload=->
					id=parseInt(xhr.responseText)
					MessagingLoadCommunique(id)
					MessagingToggle()
				xhr.send("csrf_token=#{encodeURIComponent(document.body.getAttribute('data-csrf-token'))}")
			,false
,false