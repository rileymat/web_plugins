

class TemplateHandler(object):
	def __init__(self, adapter):
		self.adapter = adapter
	def render(self, *args, **kwargs):
		return self.adapter.render(*args, **kwargs)

import pystache
class PystacheAdapter(object):
	def render(self, template, args, **kwargs):
		return pystache.render(template, args)

class PystacheFileAdapter(object):
	def __init__(self, template_root):
		self.template_root = template_root
	def render(self, template, args, **kwargs):
		renderer = pystache.Renderer()
		return renderer.render_path(self.template_root + '/' + template, args)
