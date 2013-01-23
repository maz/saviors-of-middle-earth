window.addEventListener 'load',->
	flash=document.getElementById('flash')
	if flash
		close_button=flash.querySelector('.close-button')
		close_button.addEventListener 'click',->
			flash.parentNode.removeChild(flash)
		,false
		setTimeout ->
			flash.parentNode.removeChild(flash) if flash.parentNode
		,10000#10 seconds
,false