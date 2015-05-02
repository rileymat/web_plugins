
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
		return [self.response_text]

class HtmlOkResponse(Response):
	def __init__(self):
		super(HtmlOkResponse,self).__init__()
		self.status_code = 200
		self.response_text = "OK!"
		self.add_header('Content-Type', 'text/html')
