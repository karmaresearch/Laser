from __future__ import print_function
import sys
import json
import timeit
import unittest
import time

from stream.teststream import TestStream
from stream.evalstream import EvalStream
from stream.rdfstream1 import RDFStream1
from stream.rdfstream2 import RDFStream2
from evalunit.program import Program

#------------------------------------------
def evalDiamond(winSize, nTriples):
	print("******************* Diamond Evaluation winSize = %d, Triples = %d *********************" % (winSize, nTriples))
	# ************************************************
	# Equivalent query in CSPARQL:
	#
	# REGISTER STREAM abc AS
	# SELECT ?s <http://example.org/stream/predicate#p1> ?o
	# FROM STREAM <http://ex.org/stream> [RANGE X s STEP 1s]
	# WHERE {
	#   ?s ?p ?o
	# }
	# ************************************************
	# Equivalent query in CQELS:
	#
	# SELECT ?s <http://example.org/stream/predicate#p1> ?o
	# WHERE {
	#   STREAM <http://ex.org/stream>[RANGE X s] {
	#      ?s ?p ?o
	#   }
	# }
	# ************************************************
	rules = [
		"'http://example.org/stream/predicate#p1'(X,Y) :- time_win(" + str(winSize) + ", 0, 1, diamond('http://example.org/stream/predicate#p'(X,Y)))"
	]

	s = RDFStream1(nTriples)
	prog = Program(rules, s)

	tList = list()
	for t in range(0, 2000):
		start = time.clock()
		res, tuples = prog.evaluate(t)
		end = time.clock()
		sys.stdout.write("Time = %d\r" % (t))
		sys.stdout.flush()
		tList.append(end - start)
	print("Avg = %f seconds for %d triples (%f seconds per triple)!" % (float(sum(tList)) / len(tList), nTriples, (float(sum(tList) / len(tList) / nTriples))))
	print("************************************************************")
#------------------------------------------
def evalBox(winSize, nTriples):
	print("******************* Box Evaluation winSize = %d, Triples = %d *********************" % (winSize, nTriples))
	rules = [
		"z(X) :- time_win(" + str(winSize) + ", 0, 1, box(p(X)))",
	]

	s = EvalStream("p", nTriples, maxRand=(nTriples / 3 + 1))
	prog = Program(rules, s)

	tList = list()
	for t in range(0, 2000):
		start = time.clock()
		res, tuples = prog.evaluate(t)
		end = time.clock()
		sys.stdout.write("Time = %d\r" % (t))
		sys.stdout.flush()
		tList.append(end - start)
	print("Avg = %f seconds for %d triples (%f seconds per triple)!" % (float(sum(tList)) / len(tList), nTriples, (float(sum(tList) / len(tList) / nTriples))))
	print("********************************************************")
#------------------------------------------
def evalSingleJoin(winSize, nTriples):
	print("******************* Join Evaluation winSize = %d, Triples = %d *********************" % (winSize, nTriples))
	# ************************************************
	# Equivalent query in CSPARQL:
	#
	# REGISTER STREAM abc AS
	# SELECT ?s <http://example.org/stream/predicate#p1> ?o
	# FROM STREAM <http://ex.org/stream> [RANGE X s STEP 1s]
	# WHERE {
	#   ?s <http://example.org/stream/predicate#p> ?t .
	#   ?t <http://example.org/stream/predicate#p> ?o .
	# }
	# ************************************************
	# Equivalent query in CQELS:
	#
	# SELECT ?s <http://example.org/stream/predicate#p1> ?o
	# WHERE {
	#   STREAM <http://ex.org/stream>[RANGE X s] {
	#      ?s <http://example.org/stream/predicate#p> ?t .
	#      ?t <http://example.org/stream/predicate#p> ?o .
	#   }
	# }
	# ************************************************
	rules = [
		"'http://example.org/stream/predicate#p1'(X,Z) :- time_win(" + str(winSize) + ", 0, 1, diamond('http://example.org/stream/predicate#p'(X,Y))) and time_win(" + str(winSize) + " ,0,1,diamond('http://example.org/stream/predicate#p'(Y,Z)))",
	]

	s = RDFStream2(nTriples)
	prog = Program(rules, s)

	tList = list()
	for t in range(0, 2000):
		start = time.clock()
		res, tuples = prog.evaluate(t)
		end = time.clock()
		sys.stdout.write("Time = %d\r" % (t)); sys.stdout.flush()
		tList.append(end - start)
	print("Avg = %f seconds for %d triples (%f seconds per triple)!" % (float(sum(tList)) / len(tList), nTriples, (float(sum(tList) / len(tList) / nTriples))))
	print("********************************************************")
#------------------------------------------
def evalMultipleRules(nRules, winSize, nTriples):
	print("******************* Multirule Join Evaluation Rules = %d, winSize = %d, Triples = %d *********************" % (nRules, winSize, nTriples))
	def generate_rules(nRules, winSize):
		rules = [
			"'http://example.org/stream/predicate#p1'(X,Z) :- time_win(" + str(winSize) + ", 0, 1, diamond('http://example.org/stream/predicate#p'(X,Y))) and time_win(" + str(winSize) + ",0,1,diamond('http://example.org/stream/predicate#p'(Y,Z)))",
		]
		return rules * nRules

	rules = generate_rules(nRules, winSize)

	s = RDFStream2(nTriples)
	prog = Program(rules, s)

	tList = list()
	for t in range(0, 2000):
		start = time.clock()
		res, tuples = prog.evaluate(t)
		end = time.clock()
		sys.stdout.write("Time = %d\r" % (t)); sys.stdout.flush()
		tList.append(end - start)
	print("Avg = %f seconds for %d triples (%f seconds per triple)!" % (float(sum(tList)) / len(tList), nTriples, (float(sum(tList) / len(tList) / nTriples))))
	print("**********************************************************************************************************")
#------------------------------------------
def evalCoolingSystem(winSize, nTriples):
	print("******************* Cooling System Evaluation winSize = %d, Triples = %d *********************" % (winSize, nTriples))

	rules = [
		"@(T, steam(V)) :- time_win(" + str(winSize) + ", 0, 1, @(T, (temp(V)))) and COMP(>=, V, 100)",
		"@(T, liquid(V)) :- time_win(" + str(winSize) + ", 0, 1, @(T, temp(V))) and COMP(<, V, 100) and COMP(>=, V, 1)",
		"@(T, isSteam) :- time_win(" + str(winSize) + ", 0, 1, @(T, steam(V)))",
		"@(T, isLiquid)  :- time_win(" + str(winSize) + ", 0, 1, @(T, liquid(V)))",
		"alarm :- time_win(" + str(winSize) + ", 0, 1, box(isSteam))",
		"normal :- time_win(" + str(winSize) + ", 0, 1, box(isLiquid))",
		"veryHot(T) :- time_win(" + str(winSize) + ",0,1, @(T, steam(V))) and COMP(>=, V, 150)",
		"veryCold(T) :- time_win(" + str(winSize) + ",0,1, @(T, liquid(V))) and COMP(=, V, 1)",
		"freeze :- not(alarm) and not(normal)",
	]

	s = EvalStream("temp", nTriples, maxRand=200)
	prog = Program(rules, s)

	tList = list()
	for t in range(0, 2000):
		start = time.clock()
		res, tuples = prog.evaluate(t)
		end = time.clock()
		sys.stdout.write("Time = %d\r" % (t)); sys.stdout.flush()
		tList.append(end - start)
	print("Avg = %f seconds for %d triples (%f seconds per triple)!" % (float(sum(tList)) / len(tList), nTriples, (float(sum(tList) / len(tList) / nTriples))))
	print("**********************************************************************************************************")
#------------------------------------------
if __name__ == "__main__":
	if sys.argv[1] == "evalCoolingSystem":
		winSize = int(sys.argv[2])
		nTriples = int(sys.argv[3])
		evalCoolingSystem(winSize, nTriples)
	elif sys.argv[1] == "evalMultipleRules":
		nRules = int(sys.argv[2])
		winSize = int(sys.argv[3])
		nTriples = int(sys.argv[4])
		evalMultipleRules(nRules, winSize, nTriples)
	elif sys.argv[1] == "evalSingleJoin":
		winSize = int(sys.argv[2])
		nTriples = int(sys.argv[3])
		evalSingleJoin(winSize, nTriples)
	elif sys.argv[1] == "evalDiamond":
		winSize = int(sys.argv[2])
		nTriples = int(sys.argv[3])
		evalDiamond(winSize, nTriples)
	elif sys.argv[1] == "evalBox":
		winSize = int(sys.argv[2])
		nTriples = int(sys.argv[3])
		evalBox(winSize, nTriples)
	else:
		print("Unknown experiment %s" % (sys.argv[1]))
		exit(1)
