from web_plugins.app import application
from web_plugins.response import HtmlTemplateResponse, HtmlResponse, Redirect, OriginRedirect
import web_plugins.template as t
import web_plugins.router as r
from web_plugins.session import InMemorySessionHandler


def logged_out_get(request):
	response = HtmlTemplateResponse('login_app_loggedin.mustache')
	response.arguments = {}
	return response

def logged_out_post(request):
	if request.form_data["password"] == "mytestpass":
		request.session["logged_in"] = True
		return OriginRedirect(request, '/success.html')
	else:
		return Redirect('/login.html')

def logged_in(request):
	response = HtmlResponse()
	response.response_text = "You are logged in."
	return response

is_logged_in = lambda request: "logged_in" in request.session 
is_logged_out = lambda request: logged_in(request)

#Lots of bad ideas below.  Routers are the same as the response pages and can be stacked.
#Interestingly it can route by lambda function, url and method.

loginhtml_router  = r.FirstMatchRouter()
loginhtml_router.routes.extend([r.MethodRoute("post", logged_out_post), r.MethodRoute("get", logged_out_get)])

logged_out_router = r.FirstMatchRouter()
logged_out_router.routes.extend([r.ExactRoute('/login.html', loginhtml_router),  
								 r.Route(lambda request: Redirect('/login.html', request.path))])

router = r.FirstMatchRouter()
router.routes.extend([r.LambdaRoute(is_logged_in, logged_in), r.LambdaRoute(is_logged_out, logged_out_router)])

application.handler = router

application.session_handler = InMemorySessionHandler()
HtmlTemplateResponse.default_template_handler = t.TemplateHandler(t.PystacheFileAdapter('./'))
