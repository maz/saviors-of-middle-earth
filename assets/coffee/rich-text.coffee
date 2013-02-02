FONTS=["Arial","Comic Sans MS","Courier New","Georiga","Impact","Times New Roman","Trebuchet","Verdana","Webdings"]

@StyleRuns=(dom)-> []

class RichTextEditor
	constructor:(field)->
		@container=field
		html=field.innerHTML
		field.innerHTML=""
		@toolbar=document.createElement('div')
		@toolbar.className='toolbar'
		@toolbar.tabIndex=0
		@fontName=document.createElement('select')
		for font in FONTS
			opt=document.createElement('option')
			opt.value=font
			opt.textContent=font
			@fontName.appendChild(opt)
		@toolbar.appendChild(@fontName)
		@fontName.addEventListener 'change',=>
			@exec('fontName',FONTS[@fontName.selectedIndex])
		,false
		@bold=document.createElement('input')
		@bold.type='checkbox'
		@bold.addEventListener 'change',=>
			@exec('bold',@bold.checked)
		,false
		@toolbar.appendChild(@bold)
		@toolbar.appendChild(document.createTextNode('B'))
		@italic=document.createElement('input')
		@italic.type='checkbox'
		@italic.addEventListener 'change',=>
			@exec('italic',@italic.checked)
		,false
		@toolbar.appendChild(@italic)
		@toolbar.appendChild(document.createTextNode('I'))
		@underline=document.createElement('input')
		@underline.type='checkbox'
		@underline.addEventListener 'change',=>
			@exec('underline',@underline.checked)
		,false
		@toolbar.appendChild(@underline)
		@toolbar.appendChild(document.createTextNode('U'))
		@container.appendChild(@toolbar)
		for elem in @toolbar.children
			elem.addEventListener 'focus',=>
				@doc.body.focus()
			,false
		@toolbar.addEventListener 'focus',=>
			@doc.body.focus()
		,false
		@iframe=document.createElement('iframe')
		field.appendChild(@iframe)
		@iframe.src="/html/blank.html"
		queryEverythingLater= =>
			setTimeout @queryEverything,0
		@iframe.addEventListener 'load',=>
			@win=@iframe.contentWindow
			@doc=@win.document
			@doc.body.innerHTML=html
			@doc.designMode='on'
			@exec('styleWithCSS',true)
			queryEverythingLater()
			@doc.body.addEventListener 'keydown',queryEverythingLater,false
			@doc.body.addEventListener 'mouseup',queryEverythingLater,false
		,false
	exec:(cmd,arg)->
		@doc.execCommand(cmd,null,arg)
	queryEverything:=>
		@fontName.selectedIndex=FONTS.indexOf(@doc.queryCommandValue('fontName').replace(/'/g,""))
		@bold.checked=@doc.queryCommandState('bold')
		@italic.checked=@doc.queryCommandState('italic')
		@underline.checked=@doc.queryCommandState('underline')

window.addEventListener 'load',->
	for field in document.querySelectorAll('.rich-text')
		new RichTextEditor(field)
,false