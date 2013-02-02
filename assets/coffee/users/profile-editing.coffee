window.addEventListener 'load',->
	form=document.getElementById('nickname-form')
	form.addEventListener 'submit',(evt)->
		if input.value.trim()==""
			evt.preventDefault()
			evt.stopPropagation()
	,false
	input=form.querySelector('input[type=text]')
	input.addEventListener 'blur',->
		form.submit() unless input.value.trim()==""
	,false
	mtxt=document.createElement('span')
	mtxt.style.position='absolute'
	mtxt.style.opacity=0
	mtxt.style.left="-6666px"
	mtxt.style.top="-6666px"
	mtxt.style.font=window.getComputedStyle(input).font
	document.body.insertBefore(mtxt,document.body.children[0])
	MARGIN=10
	recalc_width=->
		mtxt.textContent=input.value
		input.style.width="#{mtxt.offsetWidth+MARGIN}px"
	recalc_width()
	input.addEventListener 'keypress',->
		setTimeout recalc_width,0
	,false
,false

window.addEventListener 'load',->
	form=document.getElementById('description')
	form.addEventListener 'submit',->
		form.querySelector('textarea').value=JSON.stringify(StyleRuns(form.querySelector('iframe').contentWindow.document.body))
	,false
,false