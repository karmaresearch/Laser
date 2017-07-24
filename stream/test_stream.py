from evalunit.evaltree.substitutetable import SubstituteTable

class TestStream:
	def __init__(self, speed):
		tuples = open("./stream/temp.stream").readlines()
		tuples = [tpl.split() for tpl in tuples]
		self.items = [tuples[i : i + speed] for i in range(0, len(tuples), speed)]
	def get(self, t):
		return self.items[t]
