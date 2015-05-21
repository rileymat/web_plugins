import sys
sys.path.append('./../')

import unittest
import web_plugins.htmlpage as hp

class TestAccessByID(unittest.TestCase):
	def test_one_element(self):
		parent = hp.Element()
		child = hp.Element("testID")
		parent.children.append(child)
		self.assertEqual(child, parent["#testID"])
	def test_find_by_class(self):
		parent = hp.Element()
		child = hp.Element()
		child.classes.append("blue")
		parent.children.append(child)
		self.assertEqual([child], parent[".blue"])
	def test_find_by_type(self):
		page = hp.HtmlPage()
		self.assertEqual(1, len(page["body"]))

if __name__ == '__main__':
    unittest.main()
