from stream import Stream
from random import randint

class RDFStream1(Stream):
	def __init__(self, nTriples):
		super(RDFStream1, self).__init__()
		self.timeLine = {
			"startTime": 0,
			"endTime"  : 999999999,
		}
		## --------------------------
		self.predicates = {
			"http://example.org/stream/predicate#p" : (nTriples, 2),
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
				const = t * i[0] + c
				#for j in range(0, i[1]):
				row.append("http://example.org/stream/subject#s" + str(const))
				row.append("http://example.org/stream/object#o" + str(const))
				r[p].add(tuple(row))
				#print("%s %s %s" % (row[4], p , row[5]))
				self.tupleCounter += 1
		return r


