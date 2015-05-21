
default_template_handler = None

class Response(object):
	def __init__(self):
		self.headers=[]
		self.status_code = None
		self.response_text = ""
		self.start_response = None
	
	def add_header(self, name, content):
		self.headers.append((name, content))
	def send_response_header(self):
		self.start_response(str(self.status_code), [x for x in self.headers])
	def response_body(self):
		#Need to figure out how to do this correctly
		#I suspect I need to correctly convert to bytes.
		if isinstance(self.response_text, unicode):
			return [self.response_text.encode("ascii","ignore")]
		return self.response_text

class HtmlResponse(Response):
	def __init__(self):
		super(HtmlResponse,self).__init__()
		self.status_code = 200
		self.response_text = "OK!"
		self.add_header('Content-Type', 'text/html')

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
