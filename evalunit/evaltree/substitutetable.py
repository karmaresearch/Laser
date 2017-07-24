import json
class SubstituteTable:
	def __init__(self, var2columnMap=None):
		self.streamTimeLine = None
		self.columns = var2columnMap if var2columnMap is not None else dict()
		self.ctTable = dict()
		self.htTable = dict()
		self.hcTable = dict()
		self.recent  = set()
		self.rows    = 0
	def set_column_names(self, names):
		print("set_column_names %s" % (str(names)))
		self.columns = dict()
		self.rows = set()
		self.add_column_names(names)
	def add_column_names(self, names):
		if names == None:
			return

		assert type(names) == list, "Expected a list of variables"
		assert all(name[0].isupper() == True for name in names)

		idx = len(self.columns) + 4 # because of CT and HT, CC, HC
		for name in names:
			if name not in self.columns:
				self.columns[name] = idx
				idx += 1
	def remove_outdated_rows(self, t, tuple_counter):
		t = max(t - 1, 0)
		tuple_counter = tuple_counter - 1
		#print("-------------- %d -- %d ---------------" % (t, tuple_counter))
		#print("ctTable = %s" % (str(self.ctTable)))
		#print("hcTable = %s" % (str(self.hcTable)))
		if t in self.htTable:
			for row in self.htTable[t]:
				ct = row[0]
				self.ctTable[ct].remove(row)
				self.rows -= 1
				assert self.rows >= 0, "number substitution rows cannot be a negative number"
				if len(self.ctTable[ct]) == 0:
					del self.ctTable[ct]
				if row[3] is not None:
					hc = row[3]
					self.hcTable[hc].remove(row)
					if len(self.hcTable[hc]) == 0:
						del self.hcTable[hc]
			del self.htTable[t]

		hcList = list(sorted(self.hcTable.keys()))
		for hc in hcList:
			if hc > tuple_counter:
				break
			for row in self.hcTable[hc]:
				ct = row[0]
				ht = row[1]
				self.ctTable[ct].remove(row)
				self.rows -= 1
				assert self.rows >= 0, "number substitution rows cannot be a negative number"
				if len(self.ctTable[ct]) == 0:
					del self.ctTable[ct]
				self.htTable[ht].remove(row)
				if len(self.htTable[ht]) == 0:
					del self.htTable[ht]
			del self.hcTable[hc]

		self.recent.clear()
	def remove_rows_of_timepoint(self, t):
		if t not in self.ctTable:
			return
		for row in self.ctTable[t]:
			ht = row[1]
			hc = row[3]

			self.htTable[ht].remove(row)
			self.hcTable[hc].remove(row)

			if len(self.htTable[ht]) == 0:
				del self.htTable[ht]
			if len(self.hcTable[hc]) == 0:
				del self.hcTable[hc]

			self.rows -= 1

			self.recent.remove(row)
		del self.ctTable[t]
	def _copyRowsFromNowByVarName(self, other, now):
		posMap = {}

		for var, idx in self.columns.items():
			posMap[idx] = other.get_column_names()[var]
		for row in other.getRowsByCT(now):
			newRow = [None] * (len(self.columns) + 4)
			newRow[0] = row[0]
			newRow[1] = row[1]
			newRow[2] = row[2]
			newRow[3] = row[3]

			for selfIdx, otherIdx in posMap.items():
				newRow[selfIdx] = row[otherIdx]

			newRow = tuple(newRow)
			ct = newRow[0]
			ht = newRow[1]
			hc = newRow[3]
			if ct not in self.ctTable:
				self.ctTable[ct] = set()
			if ht not in self.htTable:
				self.htTable[ht] = set()
			lb = len(self.ctTable[ct])
			self.ctTable[ct].add(newRow)
			la = len(self.ctTable[ct])
			self.htTable[ht].add(newRow)
			if hc is not None:
				if hc not in self.hcTable:
					self.hcTable[hc] = set()
				self.hcTable[hc].add(newRow)
			self.recent.add(newRow)
			self.rows += (la - lb)
	def _copyRowsFromNowToTimeVarByVarName(self, other, timeVar, now):
		posMap = {}

		for var, idx in self.columns.items():
			posMap[idx] = other.get_column_names()[var]
		for row in other.getRowsByCT(now):
			newRow = [None] * (len(self.columns) + 4)
			newRow[0] = row[other.get_column_names()[timeVar]]
			newRow[1] = row[1]
			newRow[2] = row[2]
			newRow[3] = row[3]

			for selfIdx, otherIdx in posMap.items():
				newRow[selfIdx] = row[otherIdx]

			newRow = tuple(newRow)
			ct = newRow[0]
			ht = newRow[1]
			hc = newRow[3]
			if ct not in self.ctTable:
				self.ctTable[ct] = set()
			if ht not in self.htTable:
				self.htTable[ht] = set()
			lb = len(self.ctTable[ct])
			self.ctTable[ct].add(newRow)
			la = len(self.ctTable[ct])
			self.htTable[ht].add(newRow)
			if hc is not None:
				if hc not in self.hcTable:
					self.hcTable[hc] = set()
				self.hcTable[hc].add(newRow)

			self.recent.add(newRow)
			self.rows += (la - lb)

	def get_column_names(self):
		return self.columns
	def add(self, row):
		ct = row[0]
		ht = row[1]
		hc = row[3]
		if ct not in self.ctTable:
			self.ctTable[ct] = set()
		if ht not in self.htTable:
			self.htTable[ht] = set()
		lb = len(self.ctTable[ct])
		self.ctTable[ct].add(row)
		la = len(self.ctTable[ct])
		self.htTable[ht].add(row)
		if hc is not None:
			if hc not in self.hcTable:
				self.hcTable[hc] = set()
			self.hcTable[hc].add(row)
		self.recent.add(row)
		self.rows += (la - lb)
	def getRowsByCT(self, t):
		return self.ctTable[t] if t in self.ctTable else {}
	def getRecentlyAddedRows(self):
		return self.recent
	def __iter__(self):
		return iter(self.ctTable.items())
	#def copy(self):
	#	return self.rows.copy()
	#def get_items(self):
	#	return self.rows
	#def delete_row(self,row):
	#	self.rows.remove(row)
	def size(self):
		return self.rows
	def __repr__(self):
		return str(self.ctTable)
	def __str__(self):
		return str(self.ctTable)
	def show(self):
		print(json.dumps(list(self.rows), indent=4))
	def clear(self):
		self.rows.clear()
