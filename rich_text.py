import json
from cgi import escape
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

def from_style_runs(runs):
    ACCEPTABLE_CSS_KEYS=["font-family","font-size","font-weight","font-style","text-decoration"]
    if isinstance(runs,basestring):
        runs=json.loads(runs)
    io=StringIO()
    
    for run in runs:
        if 'close' in run:
            io.write("</span>")
        elif 'newline' in run:
            io.write("<br/>")
        elif 'text' in run:
            io.write(escape(run['text']).replace(u'\xa0',u'&nbsp;'))
        else:
            css=";".join(map(lambda pair:"%s:%s"%pair,filter(lambda pair:pair[0] in ACCEPTABLE_CSS_KEYS,run.iteritems())))
            io.write("<span style=\"%s\">"%css)
    
    contents=io.getvalue()
    io.close()
    return contents