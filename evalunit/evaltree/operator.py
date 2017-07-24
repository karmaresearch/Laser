class Operator:
	def __init__(self, name, params):
		self.name = name
		self.params = params
		assert self.isBinaryOperator() or self.isUnaryOperator(), ("%s is not an operator" % (name))
	def getName(self):
		return self.name
	def setName(self, name):
		self.name = name
	def getParams(self):
		return self.params
	def setParams(self,params):
		self.params = params
	def isBinaryOperator(self):
		return ((self.name == "and") or \
			(self.name == "or")  or \
			(self.name == ",")
		)
	def isUnaryOperator(self):
		return ((self.name == "@")             or \
			(self.name == "not")           or \
			(self.name == "time_win")      or \
			(self.name == "tuple_win")     or \
			(self.name == "box")           or \
			(self.name == "diamond")       or \
			(self.name == "predicate_win")
		)
