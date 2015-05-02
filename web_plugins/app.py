from web_plugins.request import Request

def application(env, start_response):
	request = Request(env)
	if application.session_handler is not None:
		request.session = application.session_handler.session_from_env(env)

	response = application.handler(request)
	response.start_response = start_response
	
	if request.session is not None:
		request.session.add_header(response)

	response.send_response_header()
	return response.response_body()

application.session_handler = None
