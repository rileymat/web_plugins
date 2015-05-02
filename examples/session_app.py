import sys
sys.path.append('./../')


import web_plugins.app
from web_plugins.app import application
from web_plugins.response import HtmlOkResponse
from web_plugins.session import InMemorySessionHandler

def session_app(request):
	response = HtmlOkResponse()
	response.response_text = "Session Key" + str(request.session.key)
	try:
		cur_number = request.session["number"]
	except:
		cur_number = 0
	request.session["number"] = cur_number + 1

	response.response_text = response.response_text + " Hit count: " + str(cur_number)
	return response


application.session_handler = InMemorySessionHandler()
application.handler = session_app
