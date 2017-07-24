import parser.parser as parser
from evaltree.node      import Node
from evaltree.substitutetable import SubstituteTable

class Rule:
	def __init__(self, _rule_string):
		self.string_representation = _rule_string
		self.parsed = parser.parse(_rule_string)
		self.bodyRetSttt = SubstituteTable()
		self.body = self.parsed["body"]
		self.head = self.parsed["head"]
		self.predicate_to_pos_node_idx, self.predicate_to_neg_node_idx = self.index_leafnodes()
		self.negatedAtoms = self.getNegatedAtoms()
		self.hasNegatedAtom = (len(self.negatedAtoms) > 0)
		self.predicate_to_node_idx = dict()
		self.lastSuccessfulJoin = -1
		self.var2atoms = self.createVarToAtomMap()
		# -----------------------------------------
		#self.joinFunc = self.hashJoin # Join function
		self.joinFunc = self.fastHashJoin # Join function
		# -----------------------------------------
		for pred, leaves in self.predicate_to_pos_node_idx.items():
			if pred not in self.predicate_to_node_idx:
				self.predicate_to_node_idx[pred] = leaves
			else:
				self.predicate_to_node_idx[pred] += leaves
		for pred, leaves in self.predicate_to_neg_node_idx.items():
			if pred not in self.predicate_to_node_idx:
				self.predicate_to_node_idx[pred] = leaves
			else:
				self.predicate_to_node_idx[pred] += leaves
	############################################
	def createVarToAtomMap(self):
		_map = dict()
		for atom in self.body:
			for var in atom.substitutetable.get_column_names():
				if var not in _map:
					_map[var] = set()
				_map[var].add(atom)
		return _map
	############################################
	def getNegatedAtoms(self):
		negatedAtoms = list()
		for atom in self.body:
			if atom.isNegated:
				negatedAtoms.append(atom)
		return negatedAtoms
	############################################
	def hashJoin(self, l, r, now):
		assert l.__class__ == SubstituteTable, "The left side of a join must be SubstitutionTable"
		if r.nodeType == Node.Math:
			return self.doMathSlow(l,r,now)
		if r.nodeType == Node.Comp:
			return self.doCompSlow(l,r,now)
		##############################
		lchStt = l
		rchStt = r.substitutetable
		##############################
		def key_gen(row, common_vars, column_idx):
			k = ""
			for v in common_vars:
				k += (row[column_idx[v]] if type(row[column_idx[v]]) is str else str(row[column_idx[v]]))

			return k
		##############################
		retStt = SubstituteTable()
		lch_vars = lchStt.get_column_names().keys()
		rch_vars = rchStt.get_column_names().keys()
		retStt.add_column_names(lch_vars)
		retStt.add_column_names(rch_vars)

		lch_vars_idx = lchStt.get_column_names()
		rch_vars_idx = rchStt.get_column_names()
		vars_idx = retStt.get_column_names()

		common_vars = list(set(lch_vars) & set(rch_vars))

		#print("================= %s ===================" % (str(common_vars)))
		#print("Return Var Idx = %s" % (str(vars_idx)))
		#print("xh1: %s" % (str(lchStt.get_column_names())))
		#print("xh2: %s" % (str(rchStt.get_column_names())))
		#print("CH1 STT = %s" % (str(lchStt)))
		#print("CH2 STT = %s" % (str(rchStt)))

		idx = dict()
		for t, rows in lchStt:
			for row in rows:
				k = key_gen(row, common_vars, lchStt.get_column_names())
				if k not in idx:
					idx[k] = [row]
				else:
					idx[k].append(row)

		for t, rows in rchStt:
			for row in rows:
				k = key_gen(row, common_vars, rchStt.get_column_names())
				if k in idx:
					for item in idx[k]:
						ct  = now
						ht = min(row[1], item[1])
						cc = None
						if (row[3] is not None) and (item[3] is not None):
							hc = min(row[3], item[3])
						elif row[3] is not None:
							hc = row[3]
						elif item[3] is not None:
							hc = item[3]
						else:
							hc = None

						new_row = [ct, ht, cc, hc] + [None] * (len(retStt.get_column_names()))
						for var,var_idx in vars_idx.items():
							if var in lch_vars_idx:
								new_row[var_idx] = item[lch_vars_idx[var]]
							elif var in rchStt.get_column_names():
								new_row[var_idx] = row[rch_vars_idx[var]]
							else:
								assert False, "This should never happen"
						#print("Adding Join row = %s" % (str(new_row)))
						retStt.add(tuple(new_row))

		return retStt
	############################################
	def fastHashJoin(self, l, r, now):
		assert l.__class__ == SubstituteTable, "The left side of a join must be SubstitutionTable"
		if r.nodeType == Node.Math:
			return self.doMathFast(l,r,now)
		if r.nodeType == Node.Comp:
			return self.doCompFast(l,r,now)
		##############################
		lchStt = l
		rchStt = r.substitutetable
		##############################
		def key_gen(row, common_vars, column_idx):
			k = ""
			for v in common_vars:
				k += (row[column_idx[v]] if type(row[column_idx[v]]) is str else str(row[column_idx[v]]))

			return k
		##############################
		retStt = SubstituteTable()
		lch_vars = lchStt.get_column_names().keys()
		rch_vars = rchStt.get_column_names().keys()
		retStt.add_column_names(lch_vars)
		retStt.add_column_names(rch_vars)

		lch_vars_idx = lchStt.get_column_names()
		rch_vars_idx = rchStt.get_column_names()
		vars_idx = retStt.get_column_names()

		common_vars = list(set(lch_vars) & set(rch_vars))

		#print("================= %s ===================" % (str(common_vars)))
		#print("Return Var Idx = %s" % (str(vars_idx)))
		#print("xh1: %s" % (str(lchStt.get_column_names())))
		#print("xh2: %s" % (str(rchStt.get_column_names())))
		#print("ret: %s" % (str(retStt.get_column_names())))
		#print("CH1 STT = %s" % (str(lchStt)))
		#print("CH2 STT = %s" % (str(rchStt)))

		idx = dict()
		for t in range(self.lastSuccessfulJoin, now + 1):
			for row in lchStt.getRowsByCT(t):
				k = key_gen(row, common_vars, lchStt.get_column_names())
				if k not in idx:
					idx[k] = [row]
				else:
					idx[k].append(row)

		for t, rows in rchStt:
			for row in rows:
				k = key_gen(row, common_vars, rchStt.get_column_names())
				if k in idx:
					for item in idx[k]:
						ct  = now
						ht = min(row[1], item[1])
						cc = None
						if (row[3] is not None) and (item[3] is not None):
							hc = min(row[3], item[3])
						elif row[3] is not None:
							hc = row[3]
						elif item[3] is not None:
							hc = item[3]
						else:
							hc = None

						new_row = [ct, ht, cc, hc] + [None] * (len(retStt.get_column_names()))
						for var,var_idx in vars_idx.items():
							if var in lch_vars_idx:
								new_row[var_idx] = item[lch_vars_idx[var]]
							elif var in rchStt.get_column_names():
								new_row[var_idx] = row[rch_vars_idx[var]]
							else:
								assert False, "This should never happen"
						#print("Adding Join row = %s" % (str(new_row)))
						retStt.add(tuple(new_row))
		idx = dict()
		for t in range(self.lastSuccessfulJoin, now + 1):
			for row in rchStt.getRowsByCT(t):
				k = key_gen(row, common_vars, rchStt.get_column_names())
				if k not in idx:
					idx[k] = [row]
				else:
					idx[k].append(row)

		for t, rows in lchStt:
			for row in rows:
				k = key_gen(row, common_vars, lchStt.get_column_names())
				if k in idx:
					for item in idx[k]:
						ct  = now
						ht = min(row[1], item[1])
						cc = None
						if (row[3] is not None) and (item[3] is not None):
							hc = min(row[3], item[3])
						elif row[3] is not None:
							hc = row[3]
						elif item[3] is not None:
							hc = item[3]
						else:
							hc = None

						new_row = [ct, ht, cc, hc] + [None] * (len(retStt.get_column_names()))
						for var,var_idx in vars_idx.items():
							if var in rch_vars_idx:
								new_row[var_idx] = item[rch_vars_idx[var]]
							elif var in lchStt.get_column_names():
								new_row[var_idx] = row[lch_vars_idx[var]]
							else:
								print("Var = %s" % (var))
								assert False, "This should never happen"
						#print("Adding Join row = %s" % (str(new_row)))
						retStt.add(tuple(new_row))

		return retStt
	############################################
	#def join(self, l, r, now):
	#	return self.hashJoin(l, r, now)
	############################################
	def doMathSlow(self, l, r, _):
		assert l.__class__ == SubstituteTable, "Left side of a join must be a SubstituteTable"
		assert r.__class__ == Node, "Right side of a join must be a Node"
		# ----------------------------------------
		_oprt = {
			"+": lambda x,y : int(x) + int(y),
			"-": lambda x,y : int(x) - int(y),
		}
		# ----------------------------------------
		mathNode = r
		lStt = l
		# ----------------------------------------
		lSttVars  = lStt.get_column_names()
		oprt = mathNode.pred
		oprtVars  = mathNode.atomArgs[:2]
		oprtConst = mathNode.atomArgs[2]

		retStt = SubstituteTable()
		#XXX: The order of the following two three lines MATTER
		for v in lSttVars:
			retStt.add_column_names([v])
		retStt.add_column_names(oprtVars)

		for t, rows in lStt:
			for row in rows:
				newRow = list(row)
				for v, vIdx in lSttVars.items():
					newRow[retStt.get_column_names()[v]] = row[vIdx]
				op = _oprt[oprt]
				newRow.append(op(row[lSttVars[oprtVars[1]]], oprtConst))
				retStt.add(tuple(newRow))
		return retStt
	############################################
	def doCompSlow(self, l, r, _):
		assert l.__class__ == SubstituteTable, "Left side of a join must be a SubstituteTable"
		assert r.__class__ == Node, "Right side of a join must be a Node"
		# ----------------------------------------
		_oprt = {
			">": lambda x,y  : int(x) > int(y),
			"<": lambda x,y  : int(x) < int(y),
			"<=": lambda x,y : int(x) <= int(y),
			">=": lambda x,y : int(x) >= int(y),
			"=": lambda x,y : int(x) == int(y),
		}
		# ----------------------------------------
		compNode = r
		lStt = l
		# ----------------------------------------
		oprt = compNode.pred
		lOprndIsVar = compNode.atomArgs[0].isupper()
		if lOprndIsVar:
			lVar = compNode.atomArgs[0]
		else:
			lConstant = int(compNode.atomArgs[0])
		# ----------------------------------------
		rOprndIsVar = compNode.atomArgs[1].isupper()
		if rOprndIsVar:
			rVar = compNode.atomArgs[1]
		else:
			rConstant = int(compNode.atomArgs[1])
		# ----------------------------------------
		lSttVars = lStt.get_column_names()
		retStt = SubstituteTable()
		for v in lSttVars:
			retStt.add_column_names([v])
		# ----------------------------------------
		for t, rows in lStt:
			for row in rows:
				lValue = row[lSttVars[lVar]] if lOprndIsVar else lConstant
				rValue = row[lSttVars[rVar]] if rOprndIsVar else rConstant
				if _oprt[oprt](lValue, rValue):
					newRow = list(row)
					for v, vIdx in lSttVars.items():
						newRow[retStt.get_column_names()[v]] = row[vIdx]
					retStt.add(tuple(newRow))
		return retStt
	############################################
	def doMathFast(self, l, r, now):
		assert l.__class__ == SubstituteTable, "Left side of a join must be a SubstituteTable"
		assert r.__class__ == Node, "Right side of a join must be a Node"
		# ----------------------------------------
		_oprt = {
			"+": lambda x,y : int(x) + int(y),
			"-": lambda x,y : int(x) - int(y),
		}
		# ----------------------------------------
		mathNode = r
		lStt = l
		# ----------------------------------------
		lSttVars  = lStt.get_column_names()
		oprt = mathNode.pred
		oprtVars  = mathNode.atomArgs[:2]
		oprtConst = mathNode.atomArgs[2]

		retStt = SubstituteTable()
		#XXX: The order of the following two three lines MATTER
		for v in lSttVars:
			retStt.add_column_names([v])
		retStt.add_column_names(oprtVars)

		for t in range(self.lastSuccessfulJoin + 1, now + 1):
			for row in lStt.getRowsByCT(t):
				newRow = list(row)
				for v, vIdx in lSttVars.items():
					newRow[retStt.get_column_names()[v]] = row[vIdx]
				op = _oprt[oprt]
				newRow.append(op(row[lSttVars[oprtVars[1]]], oprtConst))
				retStt.add(tuple(newRow))

		return retStt
	############################################
	def doCompFast(self, l, r, now):
		assert l.__class__ == SubstituteTable, "Left side of a join must be a SubstituteTable"
		assert r.__class__ == Node, "Right side of a join must be a Node"

		# ----------------------------------------
		_oprt = {
			">": lambda x,y  : int(x) > int(y),
			"<": lambda x,y  : int(x) < int(y),
			"<=": lambda x,y : int(x) <= int(y),
			">=": lambda x,y : int(x) >= int(y),
			"=": lambda x,y : int(x) == int(y),
		}
		# ----------------------------------------
		compNode = r
		rStt = l
		# ----------------------------------------
		oprt = compNode.pred
		lOprndIsVar = compNode.atomArgs[0].isupper()
		if lOprndIsVar:
			lVar = compNode.atomArgs[0]
		else:
			lConstant = int(compNode.atomArgs[0])
		# ----------------------------------------
		rOprndIsVar = compNode.atomArgs[1].isupper()
		if rOprndIsVar:
			rVar = compNode.atomArgs[1]
		else:
			rConstant = int(compNode.atomArgs[1])
		# ----------------------------------------
		rSttVars = rStt.get_column_names()
		retStt = SubstituteTable()
		for v in rSttVars:
			retStt.add_column_names([v])
		# ----------------------------------------
		for t in range(self.lastSuccessfulJoin + 1, now + 1):
			for row in rStt.getRowsByCT(t):
				lValue = row[rSttVars[lVar]] if lOprndIsVar else lConstant
				rValue = row[rSttVars[rVar]] if rOprndIsVar else rConstant
				if _oprt[oprt](lValue, rValue):
					newRow = list(row)
					for v, vIdx in rSttVars.items():
						newRow[retStt.get_column_names()[v]] = row[vIdx]
					retStt.add(tuple(newRow))
		return retStt
	############################################
	def getVarSubstitutions(self, var, atom):
		var2pos = atom.substitutetable.get_column_names()
		ret = set()
		for t,rows in atom.substitutetable:
			for row in rows:
				ret.add(row[var2pos[var]])
		return ret
#	############################################
	def acceptNegatedSubstitution(self, atom, t, tc, timeline):
		var2pos = atom.substitutetable.get_column_names()
		varValues = dict()
		# --------------------------
		for var in var2pos:
			varValues[var]= set()
			for a in self.var2atoms[var]:
				varValues[var] = varValues[var].union(self.getVarSubstitutions(var, a))
		# --------------------------
		row = [t, 999999999, tc, None] + [None] * len(var2pos)
		substitutions = set()
		substitutions.add(tuple(row))
		for var, values in varValues.items():
			tmp = set()
			for row in substitutions:
				for val in values:
					newrow = list(row)
					newrow[var2pos[var]] = val
					tmp.add(tuple(newrow))
			substitutions = tmp
		atom.accept(substitutions, t, tc, timeline)
	############################################
	def holdsAt(self, t, tc, timeline):
		if len(self.body) == 1:
			atom = self.body[0]
			if (atom.isNegated and (not atom.alreadyhadInput)):
				self.acceptNegatedSubstitution(atom, t, tc, timeline)
			holds = atom.holdsAt(t, timeline)
			if holds:
				self.bodyRetSttt = self.body[0].returnSttt
			return holds
		else:
			for atom in self.negatedAtoms:
				if not atom.alreadyhadInput:
					self.acceptNegatedSubstitution(atom, t, tc, timeline)

			for node in self.body:
				if not node.holdsAt(t, timeline):
					return False

			# XXX: Optimization:
			#      if body contains only two atoms, and one of them
			# is negated, join is unnecessary.
			ret = self.joinFunc(self.body[0].substitutetable, self.body[1], t)
			for n in self.body[2:]:
				ret = self.joinFunc(ret, n, t)
			if ret.size() > 0:
				self.lastSuccessfulJoin = t
				self.bodyRetSttt = ret

			return self.bodyRetSttt.size() > 0
	############################################
	def evaluate_head(self, now, tupleCounter):
		if self.head.nodeType == Node.Atom:
			self.head.copyDerivationsByVarName(self.bodyRetSttt, now)
			#print("-------------- %d ---------------" % (now))
			#print("bodyRet STT = %s" % (str(self.bodyRetSttt)))
			#print("HEAD %s STT = %s" % (self.head.pred, str(self.head.substitutetable)))
			#print("recently added = %s" % (str(self.head.substitutetable.getRecentlyAddedRows())))
			#self.head.substitutetable = bodyNode.returnSttt
		else:
			self.evaluate_head_at(now)
	############################################
	def evaluate_head_at(self, now):
		timepoint = self.head.oprtParams["@"]

		if timepoint.isdigit():
			timepoint = int(timepoint)
		else:
			assert timepoint.isupper(), "\"%s\" is not a variable in the head of rule \"%s\"" % (timepoint, _rule_string)

			var = timepoint
			bodySttt     = self.bodyRetSttt
			bodyStttVars = bodySttt.get_column_names()
			assert var in bodyStttVars, "Variable \"%s\" not among the body variables" % (var)


			self.head.substitutetable._copyRowsFromNowToTimeVarByVarName(bodySttt, var, now)
	############################################
	def __repr__(self):
		return self.string_representation
	def __str__(self):
		return self.string_representation
	############################################
	def get_head(self):
		return self.head
	############################################
	def get_body(self):
		return self.body
	############################################
	def get_predicate_to_pos_node_map(self):
		return self.predicate_to_pos_node_idx
	############################################
	def get_predicate_to_neg_node_map(self):
		return self.predicate_to_neg_node_idx
	############################################
	def get_predicate_to_node_map(self):
		return self.predicate_to_node_idx
	############################################
	def isNegNode(self, n):
		return n.isNegated
	############################################
	def index_leafnodes(self):
		pos_idx = dict()
		neg_idx = dict()
		for node in self.body:
			if ((node.nodeType == Node.Math) or (node.nodeType == Node.Comp)):
				continue
			if self.isNegNode(node):
				if node.pred not in neg_idx:
					neg_idx[node.pred] = [node]
				else:
					neg_idx[node.pred].append(node)
			if not self.isNegNode(node):
				if node.pred not in pos_idx:
					pos_idx[node.pred] = [node]
				else:
					pos_idx[node.pred].append(node)

		#self.index_leafnodes_recursive(self.body, pos_idx, neg_idx)
		return pos_idx, neg_idx
	############################################
	def rowToAtomString(self, row):
		columnToVarMap = self.head.substitutetable.get_column_names()

		atom = self.head.pred
		headLeafVars = self.head.atomArgs
		hasVars = len(headLeafVars) > 0
		if hasVars:
			atom += "("
			for var in headLeafVars:
				atom += str(row[columnToVarMap[var]])
				atom += ","
			atom = atom[:-1]
			atom += ")"

		return atom
	############################################
	def gc(self, t, tc):
		for atom in self.negatedAtoms:
			atom.alreadyhadInput = False
		self.head.gc(t, tc)
		self.bodyRetSttt.remove_outdated_rows(t, tc)
		for n in self.body:
			n.gc(t, tc)
	############################################
	def getCurrentDerivedAtoms(self, now):
		if self.head.nodeType == Node.Atom:
			atoms = {now:set()}
			for t, rows in self.head.substitutetable:
				for row in rows:
					assert t == row[0], "Expected time point \"%d\" to be equal to now \"%d\"" % (t, now)
					atoms[now].add(self.rowToAtomString(row))
			return atoms
		else:
			atoms = {}
			for t, rows in self.head.substitutetable:
				if t not in atoms:
					atoms[t] = set()
				for row in rows:
					atoms[t].add(self.rowToAtomString(row))
			return atoms
