from web_plugins.app import application
from web_plugins.response import HtmlFileResponse

import web_plugins.router as r

static_router = r.FirstMatchRouter()
static_router = r.FileRoute('/', './examples/static_app/static')
application.handler = static_router
