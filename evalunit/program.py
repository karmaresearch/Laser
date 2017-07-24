from rule import Rule
import time
from evaltree.substitutetable import SubstituteTable
from evaltree.innernode import InnerNode
from evaltree.leafnode  import LeafNode
from time import sleep
import sys
import json

class Program:
	def __init__(self, rules_string, stream):
		self.rules = list()
		self.activated_leaves = dict() # map from predicate to leaf nodes
		self.activated_rules  = dict() # map from predicate to rules
		self.deactivated_leaves = dict() # map from predicate to neg leaf nodes
		self.deactivated_rules  = dict() # map from predicate to neg rules
		self.currentTime = -1
		self.tupleCounter = 0
		self.headHoldStat = set()
		self.head_pred_to_rule = dict()
		self.stream = stream
		self.gcOverHead = list()
		self.ruleEvaluationTime = list()
		self.headGenerationCost = list()
		for rule_string in rules_string:
			self.rules.append(Rule(rule_string))
		#self.extract_rule_activated_leaves()
		self.map_head_pred_to_rule()
		#for pred,rules in self.head_pred_to_rule.items():
		#	print("Pred %s ==> %s" % (pred, str(rules)))
		self.programStratas = self.stratify()
		#exit(0)
		#deps = self.get_rule_neg_dependencies()
		#rList = list()
		#self.order_rules(deps, rList)
		#self.remove_rList_dups(rList)
		#self.rules = rList
		#self.propagateStreamTimeLine(stream.getTimeLine())
	############################################
	def map_head_pred_to_rule(self):
		for rule in self.rules:
			if rule.head.pred not in self.head_pred_to_rule:
				self.head_pred_to_rule[rule.head.pred] = list()
			self.head_pred_to_rule[rule.head.pred].append(rule)
	############################################
	def stratify(self):
		strataList = [list()]
		strataIdx = 0
		for rule in self.rules:
			self.follow_rule_dependencies(rule, strataList, strataIdx)
			strataList[strataIdx].append((rule.head.pred, [rule.head], True, rule))
		strataList = list(reversed([strata for strata in strataList if len(strata) > 0]))
		self.deduplicate_stratas(strataList, 0)
		return strataList
	def follow_rule_dependencies(self, rule, strataList, strataIdx):
		for p in rule.get_predicate_to_pos_node_map():
			if p in self.head_pred_to_rule:
				for r in self.head_pred_to_rule[p]:
					self.follow_rule_dependencies(r, strataList, strataIdx)
					strataList[strataIdx].append((p, [r.head], True, r))
			strataList[strataIdx].append((p, rule.get_predicate_to_pos_node_map()[p], False, True))
		if len(rule.get_predicate_to_neg_node_map()) > 0:
			strataIdx += 1
			strataList.append(list())
			for p in rule.get_predicate_to_neg_node_map():
				if p in self.head_pred_to_rule:
					for r in self.head_pred_to_rule[p]:
						self.follow_rule_dependencies(r, strataList, strataIdx)
						strataList[strataIdx].append((p, [r.head], True, r))
				strataList[strataIdx].append((p, rule.get_predicate_to_neg_node_map()[p], False, False))
	def deDup(self, strata):
		seen = set()
		for x in list(strata):
			if tuple(x[1]) not in seen:
				seen.add(tuple(x[1]))
			else:
				strata.remove(x)
	def deduplicate_stratas(self, strataList, idx):
		if idx == len(strataList):
			return
		for pInfo in strataList[idx]:
			self.removeFromHigherStratas(pInfo, strataList, idx + 1)
		self.deDup(strataList[idx])
		self.deduplicate_stratas(strataList, idx + 1)
	def removeFromHigherStratas(self, pInfo, strataList, idx):
		if idx == len(strataList):
			return
		for item in list(strataList[idx]):
			if item == pInfo:
				strataList[idx].remove(pInfo)
		self.removeFromHigherStratas(pInfo, strataList, idx + 1)
	############################################
	def extract_activated_rules_by_predicate(self):
		assert len(self.activated_leaves) > 0, "You must first call extract_rule_activated_leaves"
	############################################
	def runRulesOnInputData(self):
		res = []
		for rule in self.rules:
			res.append(self.distributed_input_stream(rule))
		return res
	############################################
	def remove_rList_dups(self, rList):
		dups = dict()
		for rule in rList:
			if rule not in dups:
				dups[rule] = 1
			else:
				dups[rule] += 1
		for rule in dups:
			if dups[rule] > 1:
				for n in range(1, dups[rule]):
					rList.remove(rule)
	############################################
	def order_rules(self, deps, rList):
		for rule in deps:
			rList.append(rule)
			self.order_rules(deps[rule], rList)
	def get_rule_neg_dependencies(self):
		ruleDeps = dict()
		for rule in self.rules:
			ruleDeps[rule] = self.order_rules_recursive(rule)
		self.remove_dups(ruleDeps)
		return ruleDeps
	def order_rules_recursive(self, rule):
		headPred = rule.head.pred
		ret = {}
		for r in self.rules:
			if (headPred in r.get_predicate_to_neg_node_map()) or \
			   (headPred in r.get_predicate_to_pos_node_map()):
				ret[r] = self.order_rules_recursive(r)
		return ret
	def find_recursive(self, d, item):
		if item in d:
			return True
		for _,v in d.items():
			if item in v:
				return True
			return self.find_recursive(v, item)
		return False
	def remove_dups(self, d):
		unique = {}
		for k in d.keys():
			for kk in d.keys():
				if k not in d:
					continue
				if self.find_recursive(d[k], kk):
					del d[kk]
	############################################
	def extract_rule_activated_leaves(self):
		for rule in self.rules:
			for pred, leaves in rule.get_predicate_to_pos_node_map().items():
				if pred not in self.activated_leaves:
					self.activated_leaves[pred] = set()
				if pred not in self.activated_rules:
					self.activated_rules[pred] = set()
				for leaf in leaves:
					self.activated_leaves[pred].add(leaf)
				self.activated_rules[pred].add(rule)
			for pred, leaves in rule.get_predicate_to_neg_node_map().items():
				if pred not in self.deactivated_leaves:
					self.deactivated_leaves[pred] = set()
				if pred not in self.deactivated_rules:
					self.deactivated_rules[pred] = set()
				for leaf in leaves:
					self.deactivated_leaves[pred].add(leaf)
				self.deactivated_rules[pred].add(rule)
	############################################
	def getDerivations(self, now):
		derivations = dict()
		for rule in self.rules:
			ruleAtoms = rule.getCurrentDerivedAtoms(now)
			for t, atoms in ruleAtoms.items():
				if t not in derivations:
					derivations[t] = set()
				for atom in atoms:
					derivations[t].add(atom)
		return derivations
	############################################
	def recursiveEvaluation(self, rule, now):
		_activated_rules = set()

		head_predicate = rule.head.pred

		if head_predicate in self.activated_rules:
			for r in self.activated_rules[head_predicate]:
				_activated_rules.add(r)

		if head_predicate in self.activated_leaves:
			for n in self.activated_leaves[head_predicate]:
				#leaf.copyDerivationsByPos(head, now)
				n.accept(rule.head.substitutetable.getRecentlyAddedRows(), now, self.tupleCounter, self.stream.timeLine)

		res = list()
		for r in _activated_rules:
			res.append(self.fire_rule(r))
		#self.recursiveEvaluation(holding_rules, streams, new_res, now)
	def exec_strata(self, strata):
		now = self.currentTime
		_stream = self.stream.get(now)
		for p_info in strata:
			pred = p_info[0]
			n    = p_info[1]
			if pred in _stream:
				assert pred != r.head.pred, \
				"Intentional predicate must not appear in extensional predicates"
				n.accept(_stream[predicate], now, self.tupleCounter, self.stream.timeLine)
			else:
				assert len(self.head_pred_to_rule[pred]) == 1, \
				"Cannot execute programs where more than one rule derive the same tuple"
				#------------------
				r = self.head_pred_to_rule[pred][0]
				self.fire_rule(r)
				n.accept(r.head.substitutetable.getRecentlyAddedRows(), \
					         now, self.tupleCounter, self.stream.timeLine)
	def distributed_input_stream(self, rule):
		now = self.currentTime
		_stream = self.stream.get(now)
		for predicate, leaf_list in rule.get_predicate_to_pos_node_map().items():
			if predicate not in _stream:
				continue
			for n in leaf_list:
				n.accept(_stream[predicate], now, self.tupleCounter, self.stream.timeLine)

		for predicate, leaf_list in rule.get_predicate_to_neg_node_map().items():
			# XXX: here we have BUG in cases tuples with the same predicate have various number of constants
			if predicate in self.headHoldStat:
				continue
			rows = set()
			rows.add((self.currentTime, self.currentTime, None, None))
			if predicate not in _stream:
				for leaf in leaf_list:
					assert len(leaf.atomArgs) == 0, "Negation with arguments is not supported yet"
					leaf.accept(rows, now, self.tupleCounter, self.stream.timeLine)
		return self.fire_rule(rule)
	############################################
	def cleanUp(self, now, tupleCounter):
		self.headHoldStat.clear()
		for rule in self.rules:
			rule.gc(now, tupleCounter)
	############################################
	def evaluate(self, now):
		assert now == self.currentTime + 1, "Program must be executed in sequential time order"
		self.currentTime = now

		ret = False
		tuples = {}
		if self.stream.hasTimePoint(now):
			self.cleanUp(now, self.tupleCounter)
			for strata in self.programStratas:
				ret |= self.evaluate_strata(strata)
			#res = self.runRulesOnInputData()
			#self.recursiveEvaluation(self.rules, self.stream, res, now)

			tuples = self.getDerivations(now) if ret else {}
			#tuples = {}
			self.tupleCounter += self.stream.getNumberOfTuplesAt(now)

			return ret, tuples
		return False, {}
	############################################
	def fire_rule(self, rule):
		res = rule.holdsAt(self.currentTime, self.tupleCounter, self.stream.timeLine)
		if res == True:
			rule.evaluate_head(self.currentTime, self.tupleCounter)
			#self.recursiveEvaluation(rule, self.currentTime)
		#if rule.head.substitutetable.size() > 0:
		#	self.headHoldStat.add(rule.head.pred)
		return res
	############################################
	def acceptNegAtom(self, node):
		assert False, "Not implemented yet"
	############################################
	def evaluate_strata(self, strata):
		now = self.currentTime
		_stream = self.stream.get(now)
		res = False
		for predInfo in strata:
			pred = predInfo[0]
			isHead = predInfo[2]
			if isHead:
				rule = predInfo[3]
				if self.fire_rule(rule):
					res = True
				continue
			isPositive = predInfo[3]
			for node in predInfo[1]:
				if pred in _stream:
					if isPositive:
						node.accept(_stream[pred], now, self.tupleCounter, self.stream.timeLine)
					else:
						assert node.isNegated, "expected negated atom"
						node.alreadyhadInput= True
				# if the predicate is not in the stream, but it is the head of another rule
				elif pred in self.head_pred_to_rule:
					for rule in self.head_pred_to_rule[pred]:
						head = rule.head
						if isPositive:
							node.accept(head.substitutetable.getRecentlyAddedRows(), now, self.tupleCounter, self.stream.timeLine)
						else:
							assert node.isNegated, "expected negated atom"
							if head.substitutetable.size() != 0:
								node.alreadyhadInput = True
				else:
					if not isPositive:
						assert node.isNegated, "expected negated atom"
						node.seenPositiveInstance = False
		return res
