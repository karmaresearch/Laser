##########################################################
def set_scope_parameters(row, ct, ht, cc, hc):
	assert ct is not None, "CT must not be None"
	row[0] = ct
	row[1] = ht
	row[2] = cc
	row[3] = hc
##########################################################
def create_empty_row(rowlen):
	return [None, None, None, None] + [None] * (rowlen)
##########################################################
def copy_row_items(newrow, row, ch_var_pos, var_pos):
	for var in ch_var_pos:
		newrow[var_pos[var]] = row[ch_var_pos[var]]
##########################################################
def copy_row(stt, chstt, row, ct, ht, cc, hc):
	newrow = create_empty_row(len(stt.get_column_names()))
	set_scope_parameters(newrow, ct, ht, cc, hc)
	copy_row_items(newrow, row, chstt.get_column_names(), stt.get_column_names())
	return newrow
##########################################################
def insert_stt_with_timevar(stt, chstt, row, timevar, ct, ht, cc, hc):
	newrow = copy_row(stt, chstt, row, ct, ht, cc, hc)
	newrow[stt.get_column_names()[timevar]] = row[0]
	stt.add(tuple(newrow))
##########################################################
def insert_stt_row(stt, chstt, row, ct, ht, cc, hc):
	newrow = copy_row(stt, chstt, row, ct, ht, cc, hc)
	stt.add(tuple(newrow))
##########################################################
def box_ret(ret, chret, now):
	for row in chret:
		ct = now
		ht = now
		cc = row[2]
		hc = row[3]
		insert_stt_row(ret, chret, row, ct, ht, cc, hc)
##########################################################
def diamond_ret(ret, chret, now):
	box_ret(ret, chret, now)
##########################################################
def update_box_diamond_stt(scope, stt, chstt, isChildStatefull, now):
	for row in chstt:
		ct = now
		ht = row[1]
		cc = row[2]
		hc = row[3]
		insert_stt_row(stt, chstt, row, ct, ht, cc, hc)
##########################################################
def at_fixtime_ret(ret, chret, timepoint, now):
	for row in chret:
		if row[0] == timepoint:
			ct = now
			ht = row[1]
			cc = row[2]
			hc = row[3]
			insert_stt_row(ret, chret, row, ct, ht, cc, hc)
##########################################################
def at_vartime_ret(ret, chret, timevar, now):
	for row in chret:
		ct = now
		ht = row[1]
		cc = row[2]
		hc = row[3]
		insert_stt_with_timevar(ret, chret, row, timevar, ct, ht, cc, hc)
##########################################################
def _math(oprt, stt, chstt, timevar, newvar, constant):
	_oprt = {
		"SUB": lambda x,y : x - y,
		"SUM": lambda x,y : x + y,
		"MUL": lambda x,y : x * y,
	}
	#if newvar not in stt.get_column_names():
	#	stt.add_column_names(newvar)

	#stt.setStreamTimeLine(chstt.getStreamTimeLine())

	stt_size_before = stt.size()
	for row in chstt:
		newrow = copy_row(stt, chstt, row[0], row[1], row[2], row[3])
		newrow[stt.get_column_names()[newvar]] = int(_oprt[oprt](row[chstt.get_column_names()[timevar]], int(constant)))
		stt.add(tuple(newrow))
	stt_size_after = stt.size()
	return stt_size_after > stt_size_before
##########################################################
#def isWithinWindow(scope, now, tupleCounter, row):
#	ct, ht, cc, hc  = row
#	return ((ct <= now + scope["TimeWinSize"] * scope["TimeWinSizeUnit"]))
#	       or \
#	       ((cc is not None) and \
#	       (hc <= tupleCounter + scope["TupleWinSize"])))
##########################################################
def at(n, chret, now):
	params = n.getOperator().getParams()
	assert len(params) == 1, "@ operator expects one parameter"

	timepoint = params[0]

	if timepoint.isdigit():
		timepoint = int(timepoint)
		holds = (chret.size() > 0 and any(row[0] == timepoint for row in chret))
		if holds:
			n.ret.clear()
			at_fixtime_ret(n.ret, chret, timepoint, now)
	else:
		assert timepoint.isupper(), "Time variables must be uppercase!"
		n.ret.clear()

		timevar = timepoint
		if timevar not in n.ret.get_column_names():
			n.ret.add_column_names([timevar])
		at_vartime_ret(n.ret, chret, timevar, now)

		holds = n.ret.size() > 0
		print("n.ret = %s" % (str(n.ret)))
	return holds
##########################################################
def generate_box_diamond_output(stt, ret_stt, now):
	for row in stt:
		newrow = list(row)
		newrow[0] = now
		newrow[1] = now
		ret_stt.add(tuple(newrow))
##########################################################
def diamond(n, chret, now):
	if n.scope["TupleWinSize"] is None:
		holds = False
		for row in chret:
			if (now >= row[0] and now <= row[1]):
				holds = True
				break
	else:
		l = [row[0] for row in chret]
		holds = len(l) > 0
	if holds:
		n.ret.clear()
		diamond_ret(n.ret, chret, now)
	print("HOLDS = %s" % (str(holds)))
	return holds
##########################################################
def box(n, chret, now):
	streamStartTime = n.scope["startTime"]
	streamEndTime = n.scope["endTime"]

	if n.scope["TupleWinSize"] is None:
		higherBound = now + 1 if (now + 1 <= streamEndTime) else streamEndTime + 1
		lowerBound  = now - (n.scope["TimeWinSize"] * n.scope["TimeWinSizeUnit"]) \
			      if (now - n.scope["TimeWinSize"] * n.scope["TimeWinSizeUnit"]) > \
				      streamStartTime else streamStartTime
		if higherBound != lowerBound:
			held_time_points = set([ row[0] for row in chret ])
			holds = all(t in held_time_points for t in range(lowerBound, higherBound))
		else:
			holds = False
	else:
		l = sorted([row[0] for row in chret])
		if now in l:
			s = set([idx - num for idx, num in enumerate(l)])
			holds = len(s) == 1
		else:
			holds = False
	if holds:
		n.ret.clear()
		box_ret(n.ret, chret, now)
	return holds
############################################
def intersect(list1, list2):
	return list(set(list1) & set(list2))
##########################################################
def key_gen(row, common_vars, column_idx):
	k = ""
	for v in common_vars:
		k += row[column_idx[v]]

	return k
##########################################################
def hashJoin(scope, stt, ch1stt, ch2stt, isCh1Statefull, isCh2Statefull, now):
	ch1_vars = ch1stt.get_column_names().keys()
	ch2_vars = ch2stt.get_column_names().keys()

	ch1_vars_idx = ch1stt.get_column_names()
	ch2_vars_idx = ch2stt.get_column_names()
	vars_idx = stt.get_column_names()


	common_vars = intersect(ch1_vars, ch2_vars)

	print("================= %s ===================" % (str(common_vars)))
	print("xh1: %s" % (str(ch1stt.get_column_names())))
	print("xh2: %s" % (str(ch2stt.get_column_names())))
	print("CH1 STT = %s" % (str(ch1stt)))
	print("CH2 STT = %s" % (str(ch2stt)))
	idx = dict()
	for row in ch1stt:
		k = key_gen(row, common_vars, ch1stt.get_column_names())
		if k not in idx:
			idx[k] = [row]
		else:
			idx[k].append(row)


	stt_size_before = stt.size()
	for row in ch2stt:
		k = key_gen(row, common_vars, ch2stt.get_column_names())
		if k in idx:
			for item in idx[k]:
				ct  = now
				if (row[1] is None) and (item[1] is None):
					ht = None
				else:
					print("We are HERE")
					ht = now if (row[1] is None) or (item[1] is None) else min(row[1], item[1])
				#ht = self.calcStatelessHorizonTime(scope, isCh1Statefull or isCh2Statefull, ct, _ht)
				new_row = [ct, ht] + [None] * (len(stt.get_column_names()))
				for var,var_idx in vars_idx.items():
					if var in ch1_vars_idx:
						new_row[var_idx] = item[ch1_vars_idx[var]]
					elif var in ch2stt.get_column_names():
						new_row[var_idx] = row[ch2_vars_idx[var]]
					else:
						assert False, "This should never happen"
				stt.add(tuple(new_row))

	stt_size_after = stt.size()
	return stt_size_after > stt_size_before
