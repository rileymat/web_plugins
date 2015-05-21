import sys
sys.path.append('./../')


import web_plugins.app
from web_plugins.app import application
from web_plugins.response import HtmlTemplateResponse
import web_plugins.htmlpage as wp
import web_plugins.template as t

def email_app(request):
	response = HtmlTemplateResponse('email_template.mustache')
	response.arguments = {}
	return response

application.handler = email_app
HtmlTemplateResponse.default_template_handler = t.TemplateHandler(t.PystacheFileAdapter('./examples'))
