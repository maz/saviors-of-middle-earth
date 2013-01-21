offset_in_seconds= ->
	Math.round((new Date()).getTimezoneOffset()*100)/-100
if document.cookie.indexOf("gmt_offset")<0
	document.cookie="gmt_offset="+offset_in_seconds()/60