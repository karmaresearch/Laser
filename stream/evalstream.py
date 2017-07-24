from stream import Stream
from random import randint

class EvalStream(Stream):
	def __init__(self, pred, nTriples, maxRand=10000):
		super(EvalStream, self).__init__()
		self.randUpperBound = maxRand
		self.rows= dict()
		self.streamTimeToSize = dict()
		self.timeLine = {
			"startTime": 0,
			"endTime"  : 999999999,
		}
		## --------------------------
		self.predicates = {
			pred : (nTriples, 1),
		}
		## --------------------------
		self.tuplesPerSec = 0
		for p, i in self.predicates.items():
			self.tuplesPerSec += i[0]
		self.tupleCounter = 0
	def getNumberOfTuplesAt(self, t):
		return self.tuplesPerSec
	def getTimeLine(self):
		return self.timeLine
	def hasTimePoint(self, t):
		return True
	def get(self, t):
		r = dict()
		for p, i in self.predicates.items():
			r[p] = set()
			for c in range(0, i[0]):
				row = [t, self.timeLine["endTime"], self.tupleCounter, None]
				for j in range(0, i[1]):
					row.append(randint(0, self.randUpperBound))
				r[p].add(tuple(row))
				self.tupleCounter += 1
		return r


