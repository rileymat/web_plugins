import Cookie
import uuid

class Session(object):
	def __init__(self, key):
		self.key = key
	def add_header(self, response):
		cookie = Cookie.SimpleCookie()
		cookie['session'] = str(self.key)
		response.add_header('Set-Cookie', cookie['session'].OutputString())

class InMemorySession(Session):
	def __init__(self, key):
		super(InMemorySession,self).__init__(key)
		self.data={}
		pass
	def __getitem__(self, key):
		return self.data[key]
	def __delitem__(self, key):
		try:
			del self.data[key]
		except:
			pass
	def __setitem__(self, key, value):
		self.data[key] = value
	def __contains__(self, key):
		return key in self.data


class SessionHandler(object):
	def __init__(self):
		pass
	def session_key(self, env):
		cookie = Cookie.SimpleCookie()
		if "HTTP_COOKIE" in env:
			cookie.load(env["HTTP_COOKIE"])
			if "session" in cookie:
				return cookie["session"].value
		return None
	def session_from_env(self, env):
		return self.session(self.session_key(env))

class InMemorySessionHandler(SessionHandler):
	def __init__(self):
		self.sessions = {}
	def session(self, key):
		if key is None or key not in self.sessions:
			new_key = str(uuid.uuid4().hex)
			self.sessions[new_key] = InMemorySession(new_key)
			return self.sessions[new_key]
		return self.sessions[key]
