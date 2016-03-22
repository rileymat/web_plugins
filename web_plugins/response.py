import Cookie

default_template_handler = None

class Response(object):
	def __init__(self, *args, **kwargs):
		self.headers=[]
		self.status_code = None
		self.start_response = None
		self.response_text = ""
	def add_header(self, name, content):
		self.headers.append((name, content))
	def set_header(self, name, content):
		self.remove_header(name)
		self.add_header(name, content)
	def remove_header(self, name):
		self.headers = [x for x in self.headers if x[0] != name]
	def send_response_header(self):
		self.start_response(str(self.status_code), [x for x in self.headers])
	def response_body(self):
		#Need to figure out how to do this correctly
		#I suspect I need to correctly convert to bytes.
		if isinstance(self.response_text, unicode):
			return [self.response_text.encode("ascii","ignore")]
		return self.response_text

class HtmlResponse(Response):
	def __init__(self, *args, **kwargs):
		super(HtmlResponse, self).__init__(*args, **kwargs)
		self.status_code = 200
		self.set_header('Content-Type', 'text/html')

class Redirect(Response):
	def __init__(self, addr, origin=False):
		super(Redirect, self).__init__()
		self.status_code = 302
		self.add_header('Location', addr)
		if origin:
			cookie = Cookie.SimpleCookie()
			cookie['origin_location'] = origin
			self.add_header('Set-Cookie', cookie['origin_location'].OutputString())

class OriginRedirect(Redirect):
	def __init__(self, request, addr=''):
		if 'origin_location' in request.cookies:
			addr = request.cookies["origin_location"]
		super(OriginRedirect, self).__init__(addr)

class HtmlTemplateResponse(HtmlResponse):
	default_template_handler = None
	def __init__(self, template, template_handler=None):
		super(HtmlTemplateResponse, self).__init__()
		if template_handler is not None:
			self.template_handler = template_handler
		else:
			if HtmlTemplateResponse.default_template_handler is not None:
				self.template_handler = HtmlTemplateResponse.default_template_handler
		self.template = template
	def arguments():
		def fget(self):
			return self._template
		def fset(self, value):
			self._template = value
			self.response_text = self.template_handler.render(self.template, value)
		def fdel(self):
			del self._template
		return locals()
	arguments = property(**arguments())

def detect_content_type(filename):
	suffix_content_type = [('.html','text/html'),('.css', 'text/css'), ('.gif','image/gif'), ('.png','image/png')]
	for t in suffix_content_type:
		if filename.endswith(t[0]):
			return t[1]
	return 'text/html'

class FileResponse(Response):
	def __init__(self, filename, status_code, *args, **kwargs):
		super(FileResponse, self).__init__(*args, **kwargs)
		self.status_code = status_code
		with open(filename) as f:
			self.response_text = f.read()
		self.add_header('Content-Type', detect_content_type(filename))

#class HtmlFileResponse(HtmlResponse, FileResponse):
#	def __init__(self, filename, status_code=200):
#		super(HtmlFileResponse, self).__init__(filename, status_code)
