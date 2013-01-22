window.addEventListener 'load',->
	for form in document.querySelectorAll('form')
		do (form)->
			form.addEventListener 'submit',(evt)->
				if (form.classList.contains('delete-form') and !confirm('Do you really want to delete?')) or (form.getAttribute('data-confirmation-message') and !confirm(form.getAttribute('data-confirmation-message')))
					evt.stop() if evt.stop
					evt.preventDefault() if evt.preventDefault
					return false
				if form.getAttribute('data-completing-label')
					button=form.querySelector('input[type=submit]')
					if button
						button.disabled=true
						button.value=form.getAttribute('data-completing-label')
			,false
,false