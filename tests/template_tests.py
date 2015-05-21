import sys
import unittest

sys.path.append('./../')
import web_plugins.template as t

class TestPystache(unittest.TestCase):
	def test_render(self):
		template = 'hello{{param}}'
		template_handler = t.TemplateHandler(t.PystacheAdapter('.'))
		self.assertEqual('hellothere', template_handler.render(template, {'param':'there'}))
	def test_render_file(self):
		template_handler = t.TemplateHandler(t.PystacheAdapter('.'))
		self.assertEqual('filethere',template_handler.render('template.mustache',{'param':'there'}, file=True))
if __name__ == '__main__':
    unittest.main()
