FONTS=["Arial","Comic Sans MS","Courier New","Georiga","Impact","Times New Roman","Trebuchet","Verdana","Webdings"]

class RichTextEditor
	constructor:(field)->
		@container=field
		html=field.innerHTML
		field.innerHTML=""
		@toolbar=document.createElement('div')
		@toolbar.className='toolbar'
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
		@container.appendChild(@toolbar)
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

window.addEventListener 'load',->
	for field in document.querySelectorAll('.rich-text')
		new RichTextEditor(field)
,false