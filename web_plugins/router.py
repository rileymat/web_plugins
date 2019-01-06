import os
from response import FileResponse

class Route(object):
	def __init__(self, handler):
		self.handler = handler
		self.pre_route = []
		self.post_route = []
	def __call__(self, request):
		if self.matches(request):
			return self.route(request)
	def matches(self, request):
		return True
	def route(self, request):
		response = None
		for m in self.pre_route:
			response = m(request)
			if response is not None: break
		if response is None:
			response =  self.handler(request)
		for m in self.post_route:
			m(request, response)
		return response

class FirstMatchRouter(Route):
	def __init__(self):
		self.routes = []
		super(FirstMatchRouter, self).__init__(self.route)
	def __call__(self, request):
		return self.route(request)
	def route(self, request):
		response = None
		for m in self.pre_route:
			response = m(request)
			if response is not None: break
		if response is None:
			route = self.matches(request)
			if route:
				response = route.route(request)
		for m in self.post_route:
			m(request, response)
		return response

	def matches(self, request):
		for route in self.routes:
			if route.matches(request):
				return route
		return False

class PriorityRouter(FirstMatchRouter):
	def __init__(self):
		super(PriorityRouter, self).__init__()
	def add_route(self, route):
		self.routes.append(route)
		#sort the routes.

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

class PathRoute(LambdaRoute):
	def __init__(self, path, handler):
		super(PathRoute, self).__init__((lambda request: request.path.lower().startswith(path.lower())), handler)

class FileRoute(PathRoute):
	def __init__(self, url_path_prefix, local_file_location):
		self.url_path_prefix = url_path_prefix
		self.local_file_location = local_file_location
		def serve_file(url_path_prefix, local_file_location):
			def serve_file_func(request):
				file_path = local_file_location + '/' + request.path[len(url_path_prefix):]
				file_response = FileResponse(file_path, 200)
				yield file_response
			return serve_file_func
		super(FileRoute, self).__init__(url_path_prefix,  serve_file(url_path_prefix, local_file_location))

	def matches(self, request):
		if super(FileRoute, self).matches(request):
			file_path = self.local_file_location + '/' + request.path[len(self.url_path_prefix):]
			return os.path.isfile(file_path)
		return False

import re

class RegexRoute(Route):
	def __init__(self, expression, handler):
		self.expression = re.compile(expression)
		super(RegexRoute, self).__init__(handler)
	def matches(self, request):
		match = self.expression.match(request.path)
		if match:
			request.params = match.groupdict()
			return True
		else:
			return False
