document.addEventListener 'keydown',(evt)->
	if evt.ctrlKey and evt.altKey and evt.keyCode==70#F
		document.getElementById('search-field').focus()
, false