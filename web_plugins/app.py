from web_plugins.request import Request

def application(env, start_response):
	request = Request(env)
	if application.session_handler is not None:
		request.session = application.session_handler.session_from_env(env)
		
	response = application.handler(request)
	for r in response:
		try:
			r.start_response = start_response

			if request.session is not None:
				request.session.add_header(r)

			r.send_response_header()
			yield r.response_body()
		except Exception:
			yield ""


application.session_handler = None
application.template_handler = None
