import sys
sys.path.append('./../')


import web_plugins.app
from web_plugins.app import application
from web_plugins.response import HtmlOkResponse


def basic_app(request):
	response = HtmlOkResponse()
	response.response_text = "Everything is Fine"
	return response

application.handler = basic_ap
