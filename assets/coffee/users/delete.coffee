window.addEventListener 'load',->
	confirm_field=document.getElementById('confirm-field')
	delete_button=document.getElementById('delete-button')
	confirm_field.addEventListener 'keydown',(evt)->
		if evt.keyCode==13#enter
			evt.stopPropagation() if evt.stopPropagation
			evt.preventDefault() if evt.preventDefault
		setTimeout ->
			delete_button.disabled=(confirm_field.value!="unrecoverable")
		,10
	,false
,false