import json
from jinja2.utils import escape

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

def escape_css(x):
    if x.isalnum(): return x
    return "'%s'"%x.replace("\\","\\\\")

def from_style_runs(runs):
    ACCEPTABLE_CSS_KEYS=["font-family","font-size","font-weight","font-style","text-decoration"]
    if isinstance(runs,basestring):
        runs=json.loads(runs)
    
    if not runs: return ""
    io=StringIO()
    
    for run in runs:
        if not run: continue
        if 'end' in run:
            io.write("</span>")
        elif 'newline' in run:
            io.write("<br/>")
        elif 'text' in run:
            io.write(unicode((escape(run['text']))).replace(u'\xa0',u'&nbsp;').encode('ascii','xmlcharrefreplace'))
        else:
            css=";".join(map(lambda pair:"%s:%s"%(pair[0],escape_css(pair[1])),filter(lambda pair:pair[0] in ACCEPTABLE_CSS_KEYS,run.iteritems())))
            io.write("<span style=\"%s\">"%css)
    
    contents=io.getvalue()
    io.close()
    return contents