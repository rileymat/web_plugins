import Cookie
import pprint
from urlparse import parse_qs
pp = pprint.PrettyPrinter()

class FormData(object):
	def __init__(self, form_dict):
		self.form_dict = form_dict
	def __getitem__(self, key):
		return self.item(key)
	def item(self, key, default = None):
		try:
			return self.list(key)[0]
		except (IndexError):
			return default
	def list(self, key, default = []):
		default = []
		return self.form_dict.get(key, default)

class Cookies(object):
	def __init__(self, cookie_string):
		self.cookie_dict = {}
		cookies = Cookie.SimpleCookie()
		cookies.load(cookie_string)
		for key in cookies:
			self.cookie_dict[key] = cookies[key].value 
	def __getitem__(self, key):
		return self.cookie_dict[key]
	def __contains__(self, key):
		return key in self.cookie_dict


class Request(object):
	def __init__(self, env):
		#pp.pprint(env)
		self.path = env['PATH_INFO']
		self.method = env['REQUEST_METHOD']
		self._env = env
		self.session = None
		self._form_data = None
		self.cookies = Cookies(env["HTTP_COOKIE"] if "HTTP_COOKIE" in env else "")
			
	def form_data():
		def fget(self):
			if self._form_data is None:
				request_body_size = int(self._env.get('CONTENT_LENGTH', 0)) #May want to check value error.
				request_body = self._env['wsgi.input'].read(request_body_size)
				form_dict = parse_qs(request_body)
				self._form_data = FormData(form_dict)
				return self._form_data
			else:
				return self._form_data
		return locals()
	form_data = property(**form_data())


