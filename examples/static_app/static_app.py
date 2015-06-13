from web_plugins.app import application
from web_plugins.response import HtmlFileResponse

import web_plugins.router as r

static_router = r.PathRoute('/static', lambda request: HtmlFileResponse('./examples/static_app' + request.path))

application.handler = static_router
