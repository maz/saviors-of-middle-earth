window.addEventListener 'load',->
	for form in document.querySelectorAll('.delete-form')
		form.addEventListener 'submit',(evt)->
			if !confirm('Do you really want to delete?')
				evt.stop() if evt.stop
				evt.preventDefault() if evt.preventDefault
		,false
,false