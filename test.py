import sys
import json
import timeit
import unittest

from stream.teststream import TestStream
from evalunit.program import Program

class Test(unittest.TestCase):
	def test_0(self):
		stream = {
			0:["r(a,b)", "a", "z(a,b,c)",],
			1:["p(c,d)", "b", "z(a,b,c)", "t(a)"],
			2:["b", "e(a,b,c)", "e(a)"],
		}
		rules = [
			"s(A)   :- t(A)",
			"p(B,C) :- r(B,C) and not(s(C))",
			"q(XX,YY) :- p(XX,YY)",
			"z(Y,X) :- q(X,Y)",
		]

		s = TestStream(stream, 0,2)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['p(a,b)', 'q(a,b)', 'z(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['q(c,d)', 's(a)', 'z(d,c)'])})
	def test_1(self):
		stream = {
			0:["r(a,b)", "a", "z(a,b,c)",],
			1:["p(c,d)", "b", "z(a,b,c)", "t(a)"],
			2:["b", "e(a,b,c)", "e(a)"],
		}
		rules = [
			"s(A)   :- t(A)",
			"p(B,C) :- not(s(C)) and r(B,C)",
			"q(XX,YY) :- p(XX,YY)",
			"z(Y,X) :- q(X,Y)",
		]

		s = TestStream(stream, 0,2)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['p(a,b)', 'q(a,b)', 'z(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['q(c,d)', 's(a)', 'z(d,c)'])})
	def test_3(self):
		stream = {
			0:["r(a,b)", "a", "z(a,b,c)",],
			1:["r(c,d)", "b", "z(a,b,c)", "t(a)"],
			2:["b", "e(a,b,c)", "e(a)"],
			3:["b", "e(a,b,c)", "e(a)"],
		}
		rules = [
			"s(A)   :- time_win(1,0,1,diamond(t(A)))",
			"p(B,C) :- time_win(1,0,1,diamond(not(s(C)))) and time_win(2,0,1, diamond(r(B,C)))",
			"q(XX,YY) :- p(XX,YY)",
			"z(Y,X) :- q(X,Y)",
		]

		s = TestStream(stream, 0,3)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['p(a,b)', 'q(a,b)', 'z(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['p(a,b)', 'q(a,b)', 'z(b,a)', 's(a)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2:set(['s(a)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['p(c,d)', 'q(c,d)', 'z(d,c)'])})
	def test_4(self):
		stream = {
			0:["r(a,b)", 'r(c,d)', "a", "z(g)", "z(h)"],
			1:["r(e,f)", 's(c,d)', "a", "z(g)", "z(h)"],
			2:["r(g,h)", 's(e,f)', "a", "z(g)", "z(h)"],
			3:["z(g,h)", 'z(e,f)', "a", "z(g)", "z(h)"],
		}
		rules = [
			"p(B,C) :- time_win(1,0,1,diamond(not(s(C, B)))) and time_win(2,0,1, diamond(r(B,C)))",
		]

		s = TestStream(stream, 0,3)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['p(a,b)', 'p(c,d)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['p(a,b)', 'p(c,d)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['p(e,f)', 'p(g,h)'])})
	def test_5(self):
		stream = {
			0:["r(a,b)", 'r(c,d)', "s", "z(g)", "z(h)"],
			1:["r(a,b)", 'r(c,d)', "s", "z(g)", "z(h)"],
			2:["r(a,b)", 'r(c,d)', "a", "z(g)", "z(h)"],
			3:["r(e,f)", 'r(g,h)', "a", "z(g)", "z(h)"],
			4:["r(i,j)", 'r(k,l)', "a", "z(g)", "z(h)"],
			5:["r(m,n)", "s", "z(g)", "z(h)"],
			6:["r(m,n)", "s", "z(g)", "z(h)"],
		}
		rules = [
			"p(B,C) :- time_win(1,0,1,diamond(not(s))) and time_win(2,0,1, diamond(r(B,C)))",
		]

		s = TestStream(stream, 0,6)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['p(a,b)', 'p(c,d)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['p(a,b)', 'p(c,d)', 'p(e,f)', 'p(g,h)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['p(a,b)', 'p(c,d)', 'p(e,f)', 'p(g,h)', 'p(i,j)', 'p(k,l)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['p(e,f)', 'p(g,h)', 'p(i,j)', 'p(k,l)', 'p(m,n)'])})

		res, tuples = prog.evaluate(6)
		self.assertFalse(res)
		self.assertEquals(tuples, {})
	def test1(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
		}

		rules = [
			"h(Y,X) :- p(X,Y)",
		]

		s = TestStream(stream, 0,2)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['h(d,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})
	def test2(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
		}

		rules = [
			"h1(Y,X) :- p(X,Y)",
			"h2(Y)   :- h1(X,Y)",
			"h3(X)   :- h2(X)"
		]

		s = TestStream(stream, 0,2)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h1(b,a)', 'h2(a)', 'h3(a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h1(d,c)', 'h2(c)', 'h3(c)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})
	def test3(self):
		stream = {
			0:["p", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p", "z(a,b,c)", "q(a)"],
		}

		rules = [
			"h :- not(p)",
		]

		s = TestStream(stream, 0,2)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['h'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples,  {2: set(['h'])})

		res, tuples = prog.evaluate(3)
		self.assertFalse(res)
		self.assertEquals(tuples,{})
	def test4(self):
		stream = {
			0:["p", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p", "z(a,b,c)", "q(a)"],
		}

		rules = [
			"d :- not(s)",
			"s :- not(h)",
			"b :- not(s) and not(h)",
			"h :- not(p)",
		]

		s = TestStream(stream, 0,2)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['d', 's'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['d', 'h'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples,  {2: set(['d', 'h'])})

		res, tuples = prog.evaluate(3)
		self.assertFalse(res)
		self.assertEquals(tuples,{})
	def test5(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(a,b)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:[""],
			6:[""]
		}

		rules = [
			"h(Y,X) :- box(p(X,Y))",
		]
		s = TestStream(stream, 0,4)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['h(b,a)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(4)
		self.assertFalse(res)
		self.assertEquals(tuples, {})
	def test6(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:[""],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- diamond(p(X,Y))",
		]
		s = TestStream(stream, 0,4)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['h(b,a)', 'h(d,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(b,a)', 'h(d,c)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples,  {3: set(['h(b,a)', 'h(d,c)', 'h(f,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples,  {4: set(['h(b,a)', 'h(d,c)', 'h(f,e)', 'h(h,g)'])})
	def test7(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- time_win(2,0,1, p(X,Y))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['h(d,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(f,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(h,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(j,i)'])})
	def test8(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- time_win(2,0,1, p(X,Y))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['h(d,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(f,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(h,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(j,i)'])})
	def test9(self):
		stream = {
			0:["p(a,b)", "qq(aa)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(a,b)", "q", "z(a,b,c)", "q(a)"],
			2:["p(a,b)", "z(a,b,c)", "q(a)"],
			3:["p(c,d)", "z(a,b,c)", "q(a)"],
			4:["p(c,d)", "z(a,b,c)", "q(a)"],
			5:["p(c,d)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- time_win(2,0,1, box(p(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(b,a)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(b,a)'])})

		res, tuples = prog.evaluate(3)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(4)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(d,c)'])})
	def test10(self):
		stream = {
			0:["p(a,b)", "qq(aa)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["p(e,f)", "z(a,b,c)", "q(a)"],
			3:["p(g,h)", "z(a,b,c)", "q(a)"],
			4:["pp(a,d)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- time_win(2,0,1, diamond(p(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(d,c)', 'h(b,a)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(f,e)', 'h(d,c)', 'h(b,a)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(h,g)', 'h(f,e)', 'h(d,c)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(h,g)', 'h(f,e)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(h,g)', 'h(j,i)'])})
	def test11(self):
		stream = {
			0:["p(a,b)", "qq(aa)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["p(e,f)", "z(a,b,c)", "q(a)"],
			3:["p(g,h)", "z(a,b,c)", "q(a)"],
			4:["pp(gg,hh)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- tuple_win(4, p(X,Y))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(d,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(f,e)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(h,g)'])})

		res, tuples = prog.evaluate(4)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(j,i)'])})
	def test12(self):
		stream = {
			0:["p(a,b)", "qq(aa)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(a,b)", "q", "z(a,b,c)", "q(a)"],
			2:["p(a,b)", "z(a,b,c)", "q(a)"],
			3:["p(g,h)", "p(a,b)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- tuple_win(4, box(p(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(b,a)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(b,a)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(b,a)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(h,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertFalse(res)
		self.assertEquals(tuples, {})
	def test13(self):
		stream = {
			0:["p(a,b)", "qq(aa)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(a,b)", "q", "z(a,b,c)", "q(a)"],
			2:["p(a,b)", "z(a,b,c)", "q(a)"],
			3:["p(g,h)", "p(a,b)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- tuple_win(4, diamond(p(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(b,a)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(b,a)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(b,a)', 'h(h,g)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(b,a)', 'h(h,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(j,i)', 'h(h,g)'])})
	def test14(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- @(3, p(X,Y))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples,  {})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(f,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(f,e)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(f,e)'])})
	def test15(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(T,X) :- @(T, p(X,Y))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(0,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(0,a)', 'h(1,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(0,a)', 'h(1,c)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(0,a)', 'h(1,c)', 'h(3,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(0,a)', 'h(1,c)', 'h(3,e)', 'h(4,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(0,a)', 'h(1,c)', 'h(3,e)', 'h(4,g)', 'h(5,i)'])})
	def test16(self):
		stream = {
			0:["p(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(T,X) :- time_win(2,0,1, @(T, p(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(0,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(0,a)', 'h(1,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(0,a)', 'h(1,c)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(1,c)', 'h(3,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(3,e)', 'h(4,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(3,e)', 'h(4,g)', 'h(5,i)'])})
	def test17(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(T,X) :- tuple_win(4,0,1, @(T, p(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(0,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(0,a)', 'h(1,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(1,c)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(3,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(3,e)', 'h(4,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(4,g)', 'h(5,i)'])})
	def test18(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(a,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h1(T,X) :- tuple_win(3,0,1, @(T, p(X,Y)))",
			"h2      :- h1(X,Y)",
			"h3      :- not(h2)",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h1(0,a)', "h2"])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h1(1,c)', "h2"])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h3'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(3,e)', "h2"])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h1(3,e)', 'h1(4,g)', "h2"])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(4,g)', 'h1(5,i)', "h2"])})
	def test19(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:[],
			2:[],
			3:[],
			4:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			5:["q", "z(a,b,c)", "q(a)"],
			6:["p(e,f)", "z(a,b,c)", "q(a)"],
			7:[],
			8:[],
			9:[],
		}

		rules = [
			"h1(T,X) :- tuple_win(4, @(T, p(X,Y)))",
			"h2      :- time_win(2,0,1, diamond(h1(X,Y)))",
			"h3      :- not(h2)",
		]

		s = TestStream(stream, 0,9)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h1(0,a)', "h2"])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h1(0,a)', "h2"])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h1(0,a)', "h2"])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(0,a)', "h3"])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h1(0,a)', 'h1(4,c)', 'h2'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(4,c)', "h2"])})

		res, tuples = prog.evaluate(6)
		self.assertTrue(res)
		self.assertEquals(tuples, {6: set(['h1(6,e)', "h2"])})

		res, tuples = prog.evaluate(7)
		self.assertTrue(res)
		self.assertEquals(tuples, {7: set(['h1(6,e)', "h2"])})

		res, tuples = prog.evaluate(8)
		self.assertTrue(res)
		self.assertEquals(tuples, {8: set(['h1(6,e)', "h2"])})

		res, tuples = prog.evaluate(9)
		self.assertTrue(res)
		self.assertEquals(tuples, {9: set(['h1(6,e)', "h3"])})
	def test20(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(e,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(g,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h1(T,X) :- tuple_win(3,0,1, @(T, p(X,Y))) and z(X,W,Z)",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h1(0,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(3,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(4,g)'])})
	def test21(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(e,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(g,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h1(T1,X) :- tuple_win(3,0,1, @(T, p(X,Y))) and MATH(+,T1,T,2)",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h1(2,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h1(3,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(5,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h1(5,e)', 'h1(6,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(6,g)', 'h1(7,i)'])})
	def test22(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(e,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(g,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"@(T1, h1(T,X)) :- tuple_win(3,0,1, @(T, p(X,Y))) and MATH(+, T1,T,2)",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h1(0,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(1,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(3,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(3,e)']), 6: set(['h1(4,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {6: set(['h1(4,g)']), 7: set(['h1(5,i)'])})
	def test23(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(e,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(g,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"@(T1, h1(T,X)) :- time_win(3,0,1, @(T, p(X,Y))) and MATH(+,T1,T,2)",
			"h2(Y,X) :- time_win(1,0,1, diamond(h1(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set([]), 2: set(['h1(0,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set([]), 2: set(['h1(0,a)']), 3: set(['h1(1,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h1(0,a)', 'h2(a,0)']), 3: set(['h1(1,c)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(3,e)']), 2: set(['h1(0,a)']), 3: set(['h1(1,c)', 'h2(a,0)', 'h2(c,1)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {6: set(['h1(4,g)']), 5: set(['h1(3,e)']), 3: set(['h1(1,c)']), 4: set(['h2(c,1)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {7: set(['h1(5,i)']), 6: set(['h1(4,g)']), 5: set(['h1(3,e)', 'h2(e,3)'])})
	def test24(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(e,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(g,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h1(T1,X) :- time_win(1,0,1, @(T, p(X,Y))) and MATH(+,T1,T,2)",
			"h2(Y,X) :- time_win(2,0,1, diamond(h1(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h1(2,a)', 'h2(a,2)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h1(2,a)', 'h2(a,2)', 'h1(3,c)', 'h2(c,3)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h1(3,c)', 'h2(c,3)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(5,e)', 'h2(e,5)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h1(5,e)', 'h2(e,5)', 'h1(6,g)', 'h2(g,6)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(6,g)', 'h2(g,6)', 'h1(7,i)', 'h2(i,7)'])})
	def test25(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(e,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(g,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h1(T,X) :- time_win(1,0,1, @(T, p(X,Y))) and COMP(>,T,2)",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(3,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h1(3,e)', 'h1(4,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(4,g)', 'h1(5,i)'])})
	def test26(self):
		stream = {
			0:["p(a,b)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["p(d,f)", "z(a,b,c)", "q(a)"],
			3:["p(e,f)", "z(e,b,c)", "q(a)"],
			4:["p(g,h)", "z(a,b,c)", "q(a)"],
			5:["p(i,j)", "z(g,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h1(T,X) :- time_win(1,0,1, @(T, p(X,Y))) and COMP(>=,T,2)",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h1(2,d)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h1(2,d)', 'h1(3,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h1(3,e)', 'h1(4,g)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h1(4,g)', 'h1(5,i)'])})
	def test27(self):
		stream = {
			0:["a(12)", "a(20)", "a(10)"],
			1:["a(100)"],
			2:["a(0)"],
			3:[],
			4:[],
			5:[],
			6:[],
			7:[],
			8:[],
			9:[],
		}

		rules = [
			"@(T, high(V)) :- time_win(2,0,1, @(T, a(V))) and COMP(>=,V,18)",
			"@(T, mid(V)) :- time_win(2,0,1, @(T, a(V))) and COMP(>=,V,12) and COMP(<, V, 18)",
			"@(T, low(V)) :- time_win(2,0,1, @(T, a(V))) and COMP(<,V,12)",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high(20)", "mid(12)", "low(10)"])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high(20)", "mid(12)", "low(10)"]), 1: set(["high(100)"])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high(20)", "mid(12)", "low(10)"]), 1: set(["high(100)"]), 2: set(["low(0)"])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(["high(100)"]), 2: set(["low(0)"])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(["low(0)"])})

		res, tuples = prog.evaluate(5)
		self.assertFalse(res)
		self.assertEquals(tuples, {})
	def test28(self):
		stream = {
			0:["a(12)", "a(20)", "a(10)"],
			1:["a(100)"],
			2:["a(30)"],
			3:["a(25)"],
			4:[],
			5:[],
			6:[],
			7:[],
			8:[],
			9:[],
		}

		rules = [
			"@(T, high) :- time_win(2,0,1, @(T, a(V))) and COMP(>=,V,18)",
			"@(T, mid) :- time_win(2,0,1, @(T, a(V))) and COMP(>=,V,12) and COMP(<, V, 18)",
			"@(T, low) :- time_win(2,0,1, @(T, a(V))) and COMP(<,V,12)",
			"lfu :- time_win(2,0,1, box(high))",
			"lru :- time_win(2,0,1, box(mid))",
			"fifo :- time_win(2,0,1, box(low)) and time_win(2,0,1, diamond(realtm))",
		]

		s = TestStream(stream, 0,6)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high", "mid", "low", "lfu", "lru"])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high", "mid", "low"]), 1: set(["high", "lfu"])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high", "mid", "low"]), 1: set(["high"]), 2:set(["high", "lfu"])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(["high"]), 2:set(["high"]), 3:set(["high", "lfu"])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {2:set(["high"]), 3:set(["high"]), 4:set([])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {3:set(["high"]), 5:set([])})

		res, tuples = prog.evaluate(6)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

	def test29(self):
		stream = {
			0:["a(12)", "a(20)", "a(10)"],
			1:["a(100)"],
			2:["a(30)"],
			3:["a(25)"],
			4:[],
			5:[],
			6:[],
			7:[],
			8:[],
			9:[],
		}

		rules = [
			"@(T, high) :- time_win(2,0,1, @(T, a(V))) and COMP(>=,V,18)",
			"@(T, mid) :- time_win(2,0,1, @(T, a(V))) and COMP(>=,V,12) and COMP(<, V, 18)",
			"@(T, low) :- time_win(2,0,1, @(T, a(V))) and COMP(<,V,12)",
			"lfu :- time_win(2,0,1, box(high))",
			"lru :- time_win(2,0,1, box(mid))",
			"fifo :- time_win(2,0,1, box(low)) and time_win(2,0,1, diamond(realtm))",
			"done :- lfu",
			"done :- lru",
			"done :- fifo",
			"random :- not(done)",
		]

		s = TestStream(stream, 0,6)
		prog = Program(rules, s)


		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high", "mid", "low", "lfu", "lru", "done"])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high", "mid", "low"]), 1: set(["high", "lfu", "done"])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(["high", "mid", "low"]), 1: set(["high"]), 2:set(["high", "lfu", "done"])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(["high"]), 2:set(["high"]), 3:set(["high", "lfu", "done"])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {2:set(["high"]), 3:set(["high"]), 4:set(["random"])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {3:set(["high"]), 5:set(["random"])})

		res, tuples = prog.evaluate(6)
		self.assertTrue(res)
		self.assertEquals(tuples, {6: set(['random'])})
	def test31(self):
		stream = {
			0:["p*2(a,b)", "q", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["p*2(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["q", "z(a,b,c)", "q(a)"],
		}

		rules = [
			"h(Y,X) :- 'p*2'(X,Y)",
		]

		s = TestStream(stream, 0,2)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples,  {1: set(['h(d,c)'])})

		res, tuples = prog.evaluate(2)
		self.assertFalse(res)
		self.assertEquals(tuples, {})
	def test32(self):
		stream = {
			0:["http://ex.org/(a,b)", "qq(aa)", "z(a,b,c)", "p(a)", "p(a,b,v)"],
			1:["http://ex.org/(c,d)", "q", "z(a,b,c)", "q(a)"],
			2:["http://ex.org/(e,f)", "z(a,b,c)", "q(a)"],
			3:["http://ex.org/(g,h)", "z(a,b,c)", "q(a)"],
			4:["pp(a,d)", "z(a,b,c)", "q(a)"],
			5:["http://ex.org/(i,j)", "z(a,b,c)", "q(a)"],
			6:[""],
			7:[""],
			8:[""],
			9:[""],
		}

		rules = [
			"h(Y,X) :- time_win(2,0,1, diamond('http://ex.org/'(X,Y)))",
		]

		s = TestStream(stream, 0,5)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertTrue(res)
		self.assertEquals(tuples, {0: set(['h(b,a)'])})

		res, tuples = prog.evaluate(1)
		self.assertTrue(res)
		self.assertEquals(tuples, {1: set(['h(d,c)', 'h(b,a)'])})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['h(f,e)', 'h(d,c)', 'h(b,a)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['h(h,g)', 'h(f,e)', 'h(d,c)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['h(h,g)', 'h(f,e)'])})

		res, tuples = prog.evaluate(5)
		self.assertTrue(res)
		self.assertEquals(tuples, {5: set(['h(h,g)', 'h(j,i)'])})
	def test33(self):
		stream = {
			0:['p(c,d)'],
			1:['p(a,b)'],
			2:['p(d,e)'],
			3:['p(e,f)'],
			4:['p(b,c)'],
		}

		rules = [
			"q(X,Z) :- time_win(3,0,1, diamond(p(X,Y))) and time_win(1, 0, 1, diamond(p(Y,Z)))",
		]

		s = TestStream(stream, 0,4)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['q(c,e)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['q(d,f)', 'q(c,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['q(a,c)', 'q(d,f)'])})
	def test34(self):
		stream = {
			0:['p(c,d)'],
			1:['p(a,b)'],
			2:['p(d,e)'],
			3:['p(e,f)'],
			4:['p(b,c)'],
		}

		rules = [
			"q(X,Z) :- time_win(1, 0, 1, diamond(p(Y,Z))) and time_win(3,0,1, diamond(p(X,Y))) ",
		]

		s = TestStream(stream, 0,4)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['q(c,e)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['q(d,f)', 'q(c,e)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['q(a,c)', 'q(d,f)'])})
	def test35(self):
		stream = {
			0:['p(c,d)'],
			1:['p(a,b)'],
			2:['p(d,e)'],
			3:['p(e,f)'],
			4:['p(b,c)'],
		}

		rules = [
			"q(X,Z) :- time_win(0, 0, 1, diamond(p(Y,Z))) and time_win(3,0,1, diamond(p(X,Y))) ",
		]

		s = TestStream(stream, 0,4)
		prog = Program(rules, s)

		res, tuples = prog.evaluate(0)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(1)
		self.assertFalse(res)
		self.assertEquals(tuples, {})

		res, tuples = prog.evaluate(2)
		self.assertTrue(res)
		self.assertEquals(tuples, {2: set(['q(c,e)'])})

		res, tuples = prog.evaluate(3)
		self.assertTrue(res)
		self.assertEquals(tuples, {3: set(['q(d,f)'])})

		res, tuples = prog.evaluate(4)
		self.assertTrue(res)
		self.assertEquals(tuples, {4: set(['q(a,c)'])})
def main():
	unittest.main()
if __name__ == '__main__':
	main()
