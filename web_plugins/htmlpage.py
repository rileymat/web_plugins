
#This entire file is a really bad idea. And should never be used.

class Attribute(object):
	def  __init__(self, name, value):
		self.name = name
		self.value = value
	def __str__(self):
		return self.name + '=' + '"' + self.value + '"'

class Element(object):
	def __init__(self, id="",name=None):
		self.children = []
		self.attributes = []
		self.id = id
		self.classes = []
		if name is not None: self.name = name
	def render(self):
		space = " " if len(self.attributes) > 0 else ""
		return "<" + self.name + space  + " ".join([str(x) for x in self.attributes]) +">" + \
               "".join([str(x) for x in self.children])  +"</" + self.name + ">" 
	def add_attr(self, name, value):
		self.attributes.append(Attribute(name, value))
		return self
	def add_el(self, element):
		self.children.append(element)
		return self
	def __str__(self):
		return self.render()

	def __getitem__(self, attr):
		if attr[0] == '#':
			found = None
			if str.lower(self.id) == attr[1:].lower(): 
				found = self
			else:
				for c in self.children:
					found = c[attr]
					if found is not None:
						break
			return found
		if attr[0] == ".":
			found = []
			classname = attr[1:].lower()
			if classname in self.classes: found.append(self)
			for c in self.children:
				found.extend(c[attr])
			return found
		found = []
		if self.name.lower() == attr.lower():
			found.append(self)
		for c in self.children:
			try:
				found.extend(c[attr])
			except:
				pass
		return found


class HtmlPage(Element):
	def __init__(self):
		super(HtmlPage, self).__init__()
		self.name = "html"
		self.children.append(Head())
		self.children.append(Body())

class Head(Element):
	def __init__(self):
		self.name = "head"
		super(Head,self).__init__()

class Form(Element):
	def __init__(self):
		self.name = "form"
		super(Form, self).__init__()

class Input(Element):
	def __init__(self):
		self.name = "input"
		super(Input, self).__init__()

class Body(Element):
	def __init__(self):
		self.name = "body"
		super(Body,self).__init__()

class Br(Element):
	def __init__(self):
		self.name = "br"
		super(Br,self).__init__()
	def render(self):
		return "<br />"

class Text(Element):
	def __init__(self, value):
		self.name = "text"
		self.value = value
		super(Text, self).__init__()
	def render(self):
		return value
