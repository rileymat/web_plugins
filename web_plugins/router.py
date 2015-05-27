
class FirstMatchRouter(object):
	def __init__(self):
		self.routes = []
	def __call__(self, request):
		return self.route(request)
	def route(self, request):
		for route in self.routes:
			if route.matches(request):
				return route.route(request)

class Route(object):
	def __init__(self, handler):
		self.handler = handler
	def __call__(self, request):
		return self.route(request)
	def matches(self, request):
		return True
	def route(self, request):
		return self.handler(request)

class LambdaRoute(Route):
	def __init__(self, func, handler):
		self.func = func
		super(LambdaRoute, self).__init__(handler)
	def matches(self, request):
		return self.func(request)

class ExactRoute(LambdaRoute):
	def __init__(self, url, handler):
		super(ExactRoute, self).__init__((lambda request: url==request.path), handler)

class MethodRoute(LambdaRoute):
	def __init__(self, method, handler):
		super(MethodRoute, self).__init__((lambda request: method.lower() == request.method.lower()), handler)

