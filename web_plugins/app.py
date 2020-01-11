from web_plugins.request import Request

def application(env, start_response):
	request = Request(env)
	if application.session_handler is not None:
		request.session = application.session_handler.session_from_env(env)
		
	response = application.handler(request)
	try:
		first_pass = True
		for r in response:
			try:
				if first_pass:
					r.start_response = start_response
					if request.session is not None:
						request.session.add_header(r)
					r.send_response_header()
					first_pass = False
				yield r.response_body()
			except Exception as e:
				print(e)
				yield ""
	except Exception as e:
		print(e)
		response.start_response = start_response
		if request.session is not None:
			request.session.add_header(response)
		response.send_response_header()

		yield response.response_body()


application.session_handler = None
application.template_handler = None
