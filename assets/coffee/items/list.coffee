window.addEventListener 'load',->
	for button in document.querySelectorAll('.item-communicate-button')
		do (button)->
			button.addEventListner 'click',->
				xhr=new XMLHttpRequest
				xhr.open('post',"/items/#{button.getAttribute('data-item')}/communicate",true)
				xhr.onload=->
					id=parseInt(xhr.responseText)
				xhr.send("csrf_token=#{encodeURIComponent(document.body.getAttribute('data-csrf-token'))}")
			,false
,false