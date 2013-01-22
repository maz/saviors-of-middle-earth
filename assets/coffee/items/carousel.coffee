window.addEventListener 'load',->
	for container in document.querySelectorAll('.carousel-container')
		do (container)->
			left=container.querySelector('.left-arrow')
			right=container.querySelector('.right-arrow')
			contents=container.querySelector('.carousel-contents')
			carousel=container.querySelector('.carousel')
			return if contents.children.length<=1
			extreme_width=contents.children[contents.children.length-2].offsetLeft
			RIGHT_SPEED=5
			LEFT_SPEED=-RIGHT_SPEED
			speed=RIGHT_SPEED
			frame=->
				carousel.scrollLeft=Math.max(Math.min(carousel.scrollLeft+speed,extreme_width-carousel.offsetWidth),0)
			timer=null
			stop_timer=->
				document.body.removeEventListener('mouseup',stop_timer,false)
				clearInterval(timer)
			start_timer=->
				timer=setInterval(frame,10)
				frame()
				document.body.addEventListener('mouseup',stop_timer,false)
			right.addEventListener 'mousedown',->
				speed=RIGHT_SPEED
				start_timer()
			,false
			left.addEventListener 'mousedown',->
				speed=LEFT_SPEED
				start_timer()
			,false
,false