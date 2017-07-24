from evalunit.evaltree.node import Node
import copy

class LeafNode(Node):
	def __init__(self, n, f, isNeg=False):
		Node.__init__(self, n)
		self.formula   = f
		self.isNegated = isNeg
		self.predicate = f.getPredicate()
		self.args      = f.getArgs()
		self.scope = {
			"TimeWinSize" : None,
			"TimeWinSizeUnit" : None,
			"TupleWinSize" : None,
		}
		if ((self.predicate == "MUL") or (self.predicate == "SUM") or (self.predicate == "SUB")):
			assert len(self.args) == 3, "%s expects three arguments"
			self.substitutetable.add_column_names([self.args[0], self.args[1]])
		else:
			self.substitutetable.set_column_names(self.formula.getArgs())
	def setFormula(self, f):
		self.formula = f
		self.substitutetable.set_column_names(self.formula.getArgs())
	def setNegatedStat(self, isNeg):
		self.isNegated = isNeg
	def getNegatedStat(self):
		return self.isNegated
	def getRetStt(self):
		return self.substitutetable
	def getFormula(self):
		return self.formula
	def setScope(self,new_scope):
		self.scope = new_scope
	def copyFrom(self, other, otherArgs, now):
		self.substitutetable._copyRowsToNow(other.getSubstituteTable(), \
			self.getFormula().getArgs(), \
			otherArgs, \
			now, \
		)
#	def accept(self, _tuple, now):
#		if len(_tuple) - 1 != len(self.formula.getArgs()):
#			return
#
#		predicate = self.formula.getPredicate()
#		row = [now, now]
#
#		row = row + _tuple[1:]
#
#		if _tuple[0] == predicate:
#			self.substitutetable.add(tuple(row))

	############################################
	def __repr__(self):
		return "%s(%s)" % (self.formula.getPredicate(), self.formula.getArgs())
	def __str__(self):
		return "%s(%s)" % (self.formula.getPredicate(), self.formula.getArgs())
	############################################
	#def setStreamTimeLine(self, timeLine):
	#	self.substitutetable.setStreamTimeLine(timeLine)
	############################################
	def calcRowScope(self, row, now, tupleCounter):
		assert self.scope["TimeWinSize"] is not None, "Time scope cannot be None"
		row[0] = now
		row[1] = now + (self.scope["TimeWinSize"] * self.scope["TimeWinSizeUnit"])
		if self.scope["TupleWinSize"] is not None:
			row[2] = tupleCounter
			row[3] = tupleCounter + self.scope["TupleWinSize"]
		return tuple(row)
	############################################
	def accept(self, _sttt, now, tupleCounter):
		print("_STTT = %s" % (str(_sttt)))
		assert len(_sttt.get_column_names()) == 0, "input data sttt should not have any column name"
		if self.scope["TupleWinSize"] is not None:
			assert self.scope["TimeWinSizeUnit"] == 1, "TimeWinSizeUnit expected to be 1"
			for row in _sttt:
				if row[1] >= tupleCounter + self.scope["TupleWinSize"]:
					break
				print("%d ROW[1] = %s" % (tupleCounter, str(row)))
				c = row[1] # the tuple number
				if len(row) - 4 == len(self.formula.getArgs()):
					newrow = list(row)
					newrow[0] = now
					newrow[1] = None
					newrow[2] = c
					newrow[3] = c + self.scope["TupleWinSize"]
					#newrow = self.calcRowScope(newrow, now, tupleCounter + c)
					self.substitutetable.add(tuple(newrow))
				c += 1
		else:
			for row in _sttt:
				if len(row) - 4 == len(self.formula.getArgs()):
					newrow = list(row)
					newrow = self.calcRowScope(newrow, now, tupleCounter)
					self.substitutetable.add(newrow)
		print("STTT = %s" % (str(self.substitutetable)))
	############################################
	def getSubstituteTable(self):
		return self.substitutetable
	############################################
	def gc(self, now, tupleCounter):
		self.substitutetable.remove_outdated_rows(now, tupleCounter)
	############################################
	def push_to_parent(self, now, tupleCounter):
		holds = any(row[0] == now for row in self.substitutetable)
		if self.parent:
			return self.parent.pull(self, self.substitutetable, now, tupleCounter)
		else:
			return True if holds else False
