class Formula:
	def __init__(self):
		self.predicate = None
		self.args      = None
	def getPredicate(self):
		return self.predicate
	def setPredicate(self, pred):
		self.predicate = pred
	def getArgs(self):
		return self.args
	def setArgs(self, args):
		self.args = args
