from evalunit.evaltree.substitutetable import SubstituteTable

class Node:
	Atom                   = 1
	NegAtom                = 2
	AtAtom                 = 3
	AtNegAtom              = 4
	AtVarAtom              = 5
	AtVarNegAtom           = 6
	BoxAtom                = 7
	BoxNegAtom             = 8
	DiamondAtom            = 9
	DiamondNegAtom         = 10
	TimeWinAtom            = 11
	TimeWinNegAtom         = 12
	TimeWinDiamondAtom     = 13
	TimeWinDiamondNegAtom  = 14
	TimeWinBoxAtom         = 15
	TimeWinBoxNegAtom      = 16
	TimeWinAtVarAtom       = 17
	TimeWinAtVarNegAtom    = 18
	TupleWinAtom           = 19
	TupleWinNegAtom        = 20
	TupleWinDiamondAtom    = 21
	TupleWinDiamondNegAtom = 22
	TupleWinAtVarAtom      = 23
	TupleWinAtVarNegAtom   = 24
	TupleWinBoxAtom        = 25
	TupleWinBoxNegAtom     = 26
	Math                   = 27
	Comp                   = 28
	#########################################
	def registerAcceptRoutines(self):
		self.acceptRoutines = {
			self.Atom    : self.atomAccept,
			self.NegAtom : self.negAtomAccept,
			self.BoxAtom : self.boxAtomAccept,
			self.DiamondAtom : self.diamondAtomAccept,
			self.AtAtom : self.atAtomAccept,
			self.AtNegAtom : self.atNegAtomAccept,
			self.AtVarAtom : self.atVarAtomAccept,
			self.AtVarNegAtom : self.atVarNegAtomAccept,
			self.TimeWinAtom : self.timeWinAtomAccept,
			self.TimeWinBoxAtom : self.timeWinBoxAtomAccept,
			self.TimeWinBoxNegAtom : self.timeWinBoxAtomAccept,
			self.TimeWinDiamondAtom : self.timeWinDiamondAtomAccept,
			self.TimeWinDiamondNegAtom : self.timeWinDiamondAtomAccept,
			self.TimeWinAtVarAtom : self.timeWinAtVarAtomAccept,
			self.TupleWinAtom : self.tupleWinAtomAccept,
			self.TupleWinBoxAtom : self.tupleWinBoxAtomAccept,
			self.TupleWinDiamondAtom: self.tupleWinDiamondAtomAccept,
			self.TupleWinAtVarAtom: self.tupleWinAtVarAtomAccept,
		}
	def registerHoldsRoutines(self):
		self.holdsRoutines = {
			self.Atom    : self.atomHolds,
			self.NegAtom : self.negAtomHolds,
			self.BoxAtom : self.boxAtomHolds,
			self.DiamondAtom : self.diamondAtomHolds,
			self.AtAtom : self.atAtomHolds,
			self.AtNegAtom : self.atNegAtomHolds,
			self.AtVarAtom : self.atVarAtomHolds,
			self.AtVarNegAtom : self.atVarNegAtomHolds,
			self.TimeWinAtom : self.timeWinAtomHolds,
			self.TimeWinBoxAtom : self.timeWinBoxAtomHolds,
			self.TimeWinBoxNegAtom : self.timeWinBoxAtomHolds,
			self.TimeWinDiamondAtom : self.timeWinDiamondAtomHolds,
			self.TimeWinDiamondNegAtom : self.timeWinDiamondAtomHolds,
			self.TimeWinAtVarAtom : self.timeWinAtVarAtomHolds,
			self.TupleWinAtom : self.tupleWinAtomHolds,
			self.TupleWinBoxAtom : self.tupleWinBoxAtomHolds,
			self.TupleWinDiamondAtom : self.tupleWinDiamondAtomHolds,
			self.TupleWinAtVarAtom : self.tupleWinAtVarAtomHolds,
			self.Math : self.mathHolds,
			self.Comp : self.compHolds,
		}
	#########################################
	def __init__(self, n, p, _atomArgs):
		self.nodeType = n
		self.pred     = p
		self.atomArgs     = _atomArgs
		self.oprtParams = {}
		self.forEverResult = None
		self.substitutetable = SubstituteTable()
		self.returnSttt = SubstituteTable()
		self.isNegated = False
		self.alreadyhadInput = False # Only for negated atoms
		for item in self.atomArgs:
			if item.isupper():
				self.substitutetable.add_column_names([item])
				self.returnSttt.add_column_names([item])
		self.registerAcceptRoutines()
		self.registerHoldsRoutines()
	#########################################
	def accept(self, inputTuples, now, tupleCounter, timeline):
		_routine = self.acceptRoutines[self.nodeType]
		_routine(inputTuples, now, tupleCounter, timeline)
	def holdsAt(self, now, timeline):
		_routine = self.holdsRoutines[self.nodeType]
		return _routine(now, timeline)
	#########################################
	def atomAccept(self, inputTuples, now, _, __):
		for row in inputTuples:
			if (row[0] == now) and (len(row) - 4 == len(self.atomArgs)):
				row = list(row)
				row[1] = now
				self.substitutetable.add(tuple(row))
	def negAtomAccept(self, inputTuples, now, tupleCounter, _):
		self.atomAccept(inputTuples, now, tupleCounter, _)
	def boxAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		for row in inputTuples:
			if len(row) - 4 == len(self.atomArgs):
				row = list(row)
				row[1] = min(row[1], min(now + timeline["endTime"] - timeline["startTime"], timeline["endTime"]))
				self.substitutetable.add(tuple(row))
	def diamondAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		self.boxAtomAccept(inputTuples, now, tupleCounter, timeline)
	def atAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		for row in inputTuples:
			if len(row) - 4 == len(self.atomArgs):
				row = list(row)
				row[1] = min(row[1], timeline["endTime"])
				self.substitutetable.add(tuple(row))
	def atVarAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		for row in inputTuples:
			if len(row) - 4 == len(self.atomArgs):
				row = list(row)
				row[1] = min(row[1], timeline["endTime"])
				row.append(now)
				self.substitutetable.add(tuple(row))
	def atNegAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		if self.forEverResult:
			return
		t = self.oprtParams["@"]
		if (now == t) and (inputTuples.size() > 0):
			self.forEverResult = True
			for row in inputTuples:
				if len(row) - 4 == len(self.atomArgs):
					row = list(row)
					row[1] = timeline["endTime"]
					row.append(now)
					self.substitutetable.add(tuple(row))
		elif t > now:
			for row in inputTuples:
				if len(row) - 4 == len(self.atomArgs):
					row = list(row)
					row[1] = t - 1
					row.append(now)
					self.substitutetable.add(tuple(row))
		else:
			if not self.forEverResult:
				self.forEverResult = False
				self.substitutetable.clear()
	def atVarNegAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		self.atVarAtomAccept(inputTuples, now, tupleCounter, timeline)
	def timeWinAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		self.atomAccept(inputTuples, now, tupleCounter, timeline)
	def timeWinBoxAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		winLower = max(now - self.oprtParams["timeWin"][0] * self.oprtParams["timeWin"][2], timeline["startTime"])
		for row in inputTuples:
			if (row[0] >= winLower) and (len(row) - 4 == len(self.atomArgs)):
				row = list(row)
				row[1] = min(row[1], row[0] + self.oprtParams["timeWin"][0] * self.oprtParams["timeWin"][2])
				self.substitutetable.add(tuple(row))
	def timeWinDiamondAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		self.timeWinBoxAtomAccept(inputTuples, now, tupleCounter, timeline)
	def timeWinAtVarAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		winLower = max(now - self.oprtParams["timeWin"][0] * self.oprtParams["timeWin"][2], timeline["startTime"])
		for row in inputTuples:
			if (row[0] >= winLower) and (len(row) - 4 == len(self.atomArgs)):
				row = list(row)
				row[1] = min(row[1], row[0] + self.oprtParams["timeWin"][0] * self.oprtParams["timeWin"][2])
				row.append(row[0])
				self.substitutetable.add(tuple(row))
	def tupleWinAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		for row in inputTuples:
			if (row[0] == now) and (len(row) - 4 == len(self.atomArgs)):
				row = list(row)
				row[1] = now
				row[3] = None#tupleCounter + self.oprtParams["tupleWin"][0]
				self.substitutetable.add(tuple(row))
	def tupleWinBoxAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		for row in inputTuples:
			if (row[0] == now) and (len(row) - 4 == len(self.atomArgs)):
				row = list(row)
				row[1] = min(row[1], timeline["endTime"])
				row[3] = tupleCounter + self.oprtParams["tupleWin"][0]
				self.substitutetable.add(tuple(row))
	def tupleWinDiamondAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		self.tupleWinBoxAtomAccept(inputTuples, now, tupleCounter, timeline)
	def tupleWinAtVarAtomAccept(self, inputTuples, now, tupleCounter, timeline):
		for row in inputTuples:
			if (row[0] == now) and (len(row) - 4 == len(self.atomArgs)):
				row = list(row)
				row[1] = min(row[1], timeline["endTime"])
				row[3] = tupleCounter + self.oprtParams["tupleWin"][0]
				row.append(now)
				self.substitutetable.add(tuple(row))
	#########################################
	def atomHolds(self, now, _):
		self.returnSttt = self.substitutetable
		return len(self.returnSttt.getRowsByCT(now)) > 0
	def atAtomHolds(self, now, _):
		self.returnSttt = self.substitutetable
		return self.returnSttt.size() > 0
	def negAtomHolds(self, now, _):
		return self.atomHolds(now, _)
	def boxAtomHolds(self, now, timeline):
		t2c = {}
		for t, rows in self.substitutetable:
			for row in rows:
				constants = ()
				if len(row) > 4:
					constants = tuple(row[4:])
				if constants not in t2c:
					t2c[constants] = set()
				t2c[constants].add(row[0])
		seen = set()
		lower = timeline["startTime"]
		upper = now + 1
		holds = False
		#self.returnSttt.clear()
		for item, time_points in t2c.items():
			if sorted(time_points) == sorted(set(range(lower, upper))):
				row = [now, now, None, None] + list(item)
				self.returnSttt.add(tuple(row))
				holds = True
		return holds
	def diamondAtomHolds(self, now, timeline):
		self.returnSttt = self.substitutetable
		return self.returnSttt.size() > 0
	def atAtomHolds(self, now, timeline):
		t = self.oprtParams["@"]
		if self.returnSttt.size() == 0:
			for tp, rows in self.substitutetable:
				for row in rows:
					if tp == t:
						self.returnSttt.add(row)
		return self.returnSttt.size() > 0
	def atNegAtomHolds(self, now, timeline):
		self.returnSttt = self.substitutetable
		return self.forEverResult if self.forEverResult is not None else self.returnSttt.size() > 0
	def atVarAtomHolds(self, now, timeline):
		self.returnSttt = self.substitutetable
		return self.returnSttt.size() > 0
	def atVarNegAtomHolds(self, now, timeline):
		return self.atVarAtomHolds(now, timeline)
	def timeWinAtomHolds(self, now, timeline):
		return self.atomHolds(now, timeline)
	def timeWinBoxAtomHolds(self, now, timeline):
		t2c = {}
		for _, rows in self.substitutetable:
			for row in rows:
				constants = ()
				if len(row) > 4:
					constants = tuple(row[4:])
				if constants not in t2c:
					t2c[constants] = set()
				t2c[constants].add(row[0])
		seen = set()
		lower = max(timeline["startTime"], now - self.oprtParams["timeWin"][0] * self.oprtParams["timeWin"][2])
		upper = min(timeline["endTime"] + 1, now + self.oprtParams["timeWin"][1] * self.oprtParams["timeWin"][2] + 1)
		holds = False
		#self.returnSttt.clear()
		for item, time_points in t2c.items():
			if sorted(time_points) == sorted(set(range(lower, upper))):
				row = [now, now, None, None] + list(item)
				self.returnSttt.add(tuple(row))
				holds = True
		return holds
	def timeWinDiamondAtomHolds(self, now, timeline):
		return self.diamondAtomHolds(now, timeline)
	def timeWinAtVarAtomHolds(self, now, timeline):
		return self.diamondAtomHolds(now, timeline)
	def tupleWinAtomHolds(self, now, timeline):
		return self.atomHolds(now, timeline)
	def tupleWinBoxAtomHolds(self, now, timeline):
		t2c = {}
		timepoints = set()
		for _, rows in self.substitutetable:
			for row in rows:
				constants = ()
				if len(row) > 4:
					constants = tuple(row[4:])
				if constants not in t2c:
					t2c[constants] = set()
				t2c[constants].add(row[0])
				timepoints.add(row[0])
		seen = set()
		if len(timepoints) == 0:
			return False
		lower = max(timeline["startTime"], min(timepoints))
		upper = min(timeline["endTime"] + 1, max(timepoints) + 1)
		holds = False
		#self.returnSttt.clear()
		for item, time_points in t2c.items():
			if sorted(time_points) == sorted(set(range(lower, upper))):
				row = [now, now, None, None] + list(item)
				self.returnSttt.add(tuple(row))
				holds = True
		return holds
	def tupleWinDiamondAtomHolds(self, now, timeline):
		return self.diamondAtomHolds(now, timeline)
	def tupleWinAtVarAtomHolds(self, now, timeline):
		return self.diamondAtomHolds(now, timeline)
	def mathHolds(self, _, __):
		return True
	def compHolds(self, _, __):
		return True
	#########################################
	def gc(self, now, tupleCounter):
		if self.substitutetable != self.returnSttt:
			self.returnSttt.remove_outdated_rows(now, tupleCounter)
		self.substitutetable.remove_outdated_rows(now, tupleCounter)
	def copyDerivationsByVarName(self, other, t):
		self.substitutetable._copyRowsFromNowByVarName(other, t)
	def copyDerivationsByPos(self, other, t):
		self.substitutetable._copyRowsFromNowByPos(other, t)
