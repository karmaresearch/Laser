class Stack:
	def __init__(self):
		self.items = list()
	def push(self, item):
		self.items.append(item)
	def pop(self):
		item = self.items[-1]
		del self.items[-1]
		return item
	def top(self):
		return self.items[-1]
	def empty(self):
		return len(self.items) == 0
	def size(self):
		return len(self.items)
	def show(self):
		print(self.items)
