from stream import Stream

class TestStream(Stream):
	def __init__(self, data, startTime, endTime):
		super(TestStream, self).__init__()
		self.rows= dict()
		self.streamTimeToSize = dict()
		self.timeLine = {
			"startTime": startTime,
			"endTime"  : endTime
		}

		c = 0
		for t, tuples in data.items():
			if t < startTime:
				continue
			if t > endTime:
				continue
			self.parse_tuples(tuples, t, c)
			self.streamTimeToSize[t] = len(tuples)
			c += len(tuples)
	def getNumberOfTuplesAt(self, t):
		return self.streamTimeToSize[t]
	def parse_tuples(self, tuples, t, c):
		self.rows[t] = dict()
		for _tuple in tuples:
			pred, instances = self.parse_tuple(_tuple, t, c)
			if pred not in self.rows[t]:
				self.rows[t][pred] = set()
			self.rows[t][pred].add(instances)

	def getTimeLine(self):
		return self.timeLine
	def parse_tuple(self, _tuple, t, c):
		_tuple = _tuple.replace(' ', '')
		instances = [t, 999999999, c, None] # None means that must be calculated by the operator
		if "(" in _tuple:
			if ")" not in _tuple:
				print("Missing \")\"")
				exit(1)
		if ")" in _tuple:
			if "(" not in _tuple:
				print("Missing \"(\"")
				exit(1)
		if "(" in _tuple:
			if _tuple[-1:] != ')':
				print("Missing ')'")
				exit(1)
			_tuple = _tuple[:-1]

			pred, args = _tuple.split("(")
			for arg in args.split(","):
				instances.append(arg)
			return pred, tuple(instances)
		return _tuple, tuple(instances)

	def hasTimePoint(self, t):
		return t in self.rows
	def get(self, t):
		return self.rows[t]
