window.addEventListener 'load',->
	for editor in document.querySelectorAll('.image-editable')
		do (editor)->
			form=editor
			form=document.getElementById(editor.getAttribute('data-form')) if editor.getAttribute('data-form')
			sizes=editor.getAttribute('data-sizes').split(' ').map (x)-> parseInt(x,10)#you can't just use .map parseInt as map gives two arguments, and parseInt's second argument is the base
			field_name=editor.getAttribute('data-field-name')
			editor.addEventListener 'dragover',(evt)->
				evt.stopPropagation()
				evt.preventDefault()
				evt.dataTransfer.dropEffect='copy'
				editor.classList.add('highlight')
			,false
			editor.addEventListener 'dragleave',->
				editor.classList.remove('highlight')
			,false
			scale_image=(img,size)->
				setTimeout ->
					can=document.createElement('canvas')
					can.width=can.height=size
					ctx=can.getContext('2d')
					w=img.width
					h=img.height
					if w>=h
						h=(size*h)/w
						w=size
					else
						w=(w*size)/h
						h=size
					ctx.drawImage(img,(size/2)-(w/2),(size/2)-(h/2),w,h)
					dataUrl=can.toDataURL("image/png")
					input=form.querySelector("input[name=#{field_name}_#{size}]")
					if not input
						input=document.createElement('input')
						input.type='hidden'
						input.name="#{field_name}_#{size}"
						form.appendChild(input)
					input.value=dataUrl.replace('data:image/png;base64,','')
				,0
			processFile=(file)->
				reader=new FileReader
				reader.onload=(evt)->
					img=new Image
					img.onload=->
						editor.style.backgroundImage="url('#{img.src}')"
						for size in sizes
							scale_image(img,size)
						submit=form.querySelector('.image-submit')
						submit.style.display='block' if submit
					img.src=evt.target.result
				reader.readAsDataURL file
			editor.addEventListener 'drop',(evt)->
				evt.stopPropagation()
				evt.preventDefault()
				editor.classList.remove('highlight')
				for file in evt.dataTransfer.files
					if file.type.indexOf('image')==0
						processFile(file)
						break
			,false
,false