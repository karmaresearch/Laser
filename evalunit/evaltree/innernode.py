from evalunit.evaltree.node import Node
from evalunit.evaltree.substitutetable import SubstituteTable
from evalunit.evaltree.leafnode  import LeafNode
import evalunit.operators as operators

class InnerNode(Node):
	def __init__(self, n):
		Node.__init__(self, n)
		self.ret = SubstituteTable()
		self.scope = {
			"TimeWinSize" : None,
			"TimeWinSizeUnit" : None,
			"TupleWinSize" : None,
		}
		self.operator = None
		self.children = list()
	def gc(self, now, tupleCounter):
		self.substitutetable.remove_outdated_rows(now, tupleCounter)
		for ch in self.children:
			ch.gc(now, tupleCounter)
	def getSubstituteTable(self):
		return self.substitutetable
	def getRetStt(self):
		return self.ret
	def setScope(self,new_scope):
		self.scope = new_scope
	#def setWinType(newWinType):
	#	self.scope["winType"] = newWinType
	def setWinSize(newWinSize):
		self.scope["winSize"] = newWinSize
	def setWinSizeUnit(newWinSizeUnit):
		self.scope["winSizeUnit"] = newWinSizwUnit
	def setChildren(self,ch):
		for child in ch:
			self.substitutetable.add_column_names(child.substitutetable.get_column_names())
			self.ret.add_column_names(child.substitutetable.get_column_names())
		self.children = ch
	def getChildren(self):
		return self.children
	def setOperator(self, oprt):
		self.operator = oprt
	def getOperator(self):
		return self.operator
	def getMathChild(self, children):
		for ch in children:
			if ch.__class__ == LeafNode:
				name = ch.getFormula().getPredicate()
				if ((name == "MUL") or (name == "SUM") or (name == "SUB")):
					return ch
		assert False, "No Math child was found"
	def hasMathFunctions(self, children):
		for ch in children:
			if ch.__class__ == LeafNode:
				name = ch.getFormula().getPredicate()
				if ((name == "MUL") or (name == "SUM") or (name == "SUB")):
					return True
		return False

	##########################################################
	def isChildStatefull(self, ch):
		return (ch.__class__ == InnerNode and \
			(ch.getOperator().getName() == "Box" or\
			 ch.getOperator().getName() == "Diamond") \
		)
	def pull(self, ch, chret, now, tupleCounter):
		oprt_name = self.operator.getName()

		res = False

		if oprt_name == "diamond":
			res = operators.diamond(self, chret, now)
		elif oprt_name == "@":
			res = operators.at(self, chret, now)
		elif oprt_name == "box":
			res = operators.box(self, chret, now)
		elif oprt_name == "and":
			if not self.hasMathFunctions(self.children):

				res = operators.hashJoin(self.scope, \
						  self.substitutetable,   \
						  self.getChildren()[0].getSubstituteTable(),   \
						  self.getChildren()[1].getSubstituteTable(),   \
						  self.isChildStatefull(self.getChildren()[0]), \
						  self.isChildStatefull(self.getChildren()[1]), \
						  now)
			else:
				mathChild = self.getMathChild(self.children)
				otherChild = ch
				params   = mathChild.getFormula().getArgs()
				oprt     = mathChild.getFormula().getPredicate()
				newVar   = params[0]
				timeVar  = params[1]
				constant = params[2]
				#if newVar in otherChild.getSubstituteTable().get_column_names():
				#	print("CHILD = %s" % (str(otherChild.getSubstituteTable().get_column_names())))
				#	print("SELF = %s" % (str(self.getSubstituteTable().get_column_names())))
				#	print("NEW VAR = %s" % (newVar))
				#	print("Function \"%s\" expect a new variable as the first argument" % str(oprt))
				#	exit(1)
				if ((oprt == "MUL") or (oprt == "SUM") or (oprt == "SUB")):
					res = operators._math(oprt, self.substitutetable, otherChild.getSubstituteTable(), timeVar, newVar, constant)
				else:
					print("Unsupported function \"%s\"!" % (str(oprt)))
					exit(1)


		#if not res:
		#	return False

		#return True if self.parent == None else self.parent.pull(self, now)
		#print("InnerNode Box %d %s" % (res, self.parent))
		return res if self.parent == None else self.parent.pull(self, res, now)
