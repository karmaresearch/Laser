import tokenizer as tokenizer

from utils.stack        import Stack

from evalunit.evaltree.node      import Node
from evalunit.evaltree.innernode import InnerNode
from evalunit.evaltree.leafnode  import LeafNode
from evalunit.evaltree.formula   import Formula
from evalunit.evaltree.operator  import Operator
############################################
def syntax_err(msg):
	print(msg)
	exit(1)

def isUnaryOperator(oprt):
	return ((oprt == "@")             or \
		(oprt == "not")           or \
	        (oprt == "time_win")      or \
		(oprt == "tuple_win")     or \
		(oprt == "not")     or \
		(oprt == "box")           or \
		(oprt == "diamond")       or \
		(oprt == "predicate_win")
	)

def isBinaryOperator(oprt):
	return ((oprt == "and") or \
	        (oprt == "or")
	)

def isOperator(oprt):
	return isUnaryOperator(oprt) or isBinaryOperator(oprt)

def parse_predicate_arguments(idx, tokens):
	args = list()
	if idx >= len(tokens):
		syntax_err("Expected constant, or variable after token '('")
	while idx < len(tokens):
		token = tokens[idx]
		if token["type"] == tokenizer.TOKEN_IDENTIFIER:
			args.append(token["value"])
			nxt = tokens[idx + 1] if idx + 1 != len(tokens) else None
			if nxt == None:
				syntax_err("Expected ',' or ')' after '" + token["value"])
			if nxt['value'] == ',':
				idx += 1
			elif nxt['value'] == ')':
				pass
		elif token["type"] == tokenizer.TOKEN_CLOSE_PARA:
			if len(args) == 0:
				syntax_err("Expected at least one constant, or variable after token '('")
			break
		idx += 1
	return (idx, args)

def parse_operator(oprt, args_stack, isHead=False):
	oprt = oprt["value"].strip()
	if oprt == ",":
		if args_stack.size() < 2:
			syntax_err("Expected two operands for ',' operator")
		operand_1 = args_stack.pop()
		operand_2 = args_stack.pop()

		args = list()

		if operand_1.__class__ != Node:
			if type(operand_1) != list:
				args.append(operand_1)
			else:
				args += operand_1

		if operand_2.__class__ != Node:
			if type(operand_2) != list:
				args.append(operand_2)
			else:
				args += operand_2
		if operand_1.__class__ == Node:
			if operand_1.pred.isupper() or operand_1.pred.isdigit():
				if len(args) > 0:
					args.append(operand_1.pred)
				else:
					args = [operand_1.pred]
			else:
				args = [operand_1]
		if operand_2.__class__ == Node:
			if operand_2.pred.isupper() or operand_2.pred.isdigit():
				if len(args) > 0:
					args.append(operand_2.pred)
				else:
					args = [operand_2.pred]
			else:
				args = [operand_2]

		args_stack.push(args)
	elif (oprt == "and") or (oprt == "or"):
		if args_stack.size() < 2:
			operand_1 = args_stack.pop()

			syntax_err("Expected two operands for JOIN operation")
		operand_1 = args_stack.pop()
		operand_2 = args_stack.pop()

		node = list()
		if type(operand_1) == list:
			node += operand_1
		else:
			node.append(operand_1)

		if type(operand_2) == list:
			node += operand_2
		else:
			node.append(operand_2)

		args_stack.push(node)
	elif oprt == "@":
		if args_stack.size() < 1:
			syntax_err("Expected two operands for @ operation")
		params = list(reversed(args_stack.pop()))
		oprnd = params[-1]

		if type(params) != list:
			syntax_err("\"@\" operator expected a list of arguments")
		if oprnd.__class__ != Node:
			syntax_err("\"@\" operator expected a node object")

		if len(params) != 2:
			syntax_err("Too many paramters passed to \"@\" operator")

		timepoint = params[0]
		if timepoint.isdigit():
			if oprnd.nodeType == Node.Atom:
				oprnd.nodeType = Node.AtAtom
			elif oprnd.nodeType == Node.NegAtom:
				oprnd.nodeType = Node.AtNegAtom
			else:
				syntax_err("Unexpected node %s" % (str(oprnd.nodeType)))
			oprnd.oprtParams["@"] = int(timepoint)
		else:
			assert timepoint.isupper(), "Time variables must be upper case letters"
			if oprnd.nodeType == Node.Atom:
				oprnd.nodeType = Node.AtVarAtom
			elif oprnd.nodeType == Node.NegAtom:
				oprnd.nodeType = Node.AtVarNegAtom
			else:
				syntax_err("Unexpected node %s" % (str(oprnd.nodeType)))
			oprnd.oprtParams["@"] = timepoint
			if not isHead:
				oprnd.substitutetable.add_column_names([timepoint])
				oprnd.returnSttt.add_column_names([timepoint])

		args_stack.push(oprnd)
	elif oprt == "time_win":
		if args_stack.size() < 1:
			syntax_err("Expected two operands for time_window  operation")

		params = list(reversed(args_stack.pop()))
		oprnd = params[-1]

		if type(params) != list:
			syntax_err("\"timewin\" operator expected a list of arguments")
		if oprnd.__class__ != Node:
			syntax_err("\"timewin\" operator expected a node object")

		oprnd.oprtParams["timeWin"] = [int(item) for item in params[:3]]

		if oprnd.nodeType == Node.Atom:
			oprnd.nodeType = Node.TimeWinAtom
		elif oprnd.nodeType == Node.NegAtom:
			oprnd.nodeType = Node.TimeWinNegAtom
		elif oprnd.nodeType == Node.BoxAtom:
			oprnd.nodeType = Node.TimeWinBoxAtom
		elif oprnd.nodeType == Node.BoxNegAtom:
			oprnd.nodeType = Node.TimeWinBoxNegAtom
		elif oprnd.nodeType == Node.DiamondAtom:
			oprnd.nodeType = Node.TimeWinDiamondAtom
		elif oprnd.nodeType == Node.DiamondNegAtom:
			oprnd.nodeType = Node.TimeWinDiamondNegAtom
		elif oprnd.nodeType == Node.AtAtom:
			oprnd.nodeType = Node.TimeWinAtAtom
		elif oprnd.nodeType == Node.AtVarAtom:
			oprnd.nodeType = Node.TimeWinAtVarAtom
		elif oprnd.nodeType == Node.AtVarNegAtom:
			oprnd.nodeType = Node.TimeWinAtVarNegAtom
		else:
			syntax_err("Unexpected node %s" % (str(oprnd.nodeType)))

		args_stack.push(oprnd)
	elif oprt == "tuple_win":
		if args_stack.size() < 1:
			syntax_err("No operand for tuple_window operand")

		params = list(reversed(args_stack.pop()))
		oprnd = params[-1]

		if type(params) != list:
			syntax_err("\"tuple_win\" operator expected a list of arguments")
		if oprnd.__class__ != Node:
			syntax_err("\"tuple_win\" operator expected a node object")

		oprnd.oprtParams["tupleWin"] = [int(item) for item in params[:1]]

		if oprnd.nodeType == Node.Atom:
			oprnd.nodeType = Node.TupleWinAtom
		elif oprnd.nodeType == Node.NegAtom:
			oprnd.nodeType = Node.TupleWinNegAtom
		elif oprnd.nodeType == Node.BoxAtom:
			oprnd.nodeType = Node.TupleWinBoxAtom
		elif oprnd.nodeType == Node.BoxNegAtom:
			oprnd.nodeType = Node.TupleWinBoxNegAtom
		elif oprnd.nodeType == Node.DiamondAtom:
			oprnd.nodeType = Node.TupleWinDiamondAtom
		elif oprnd.nodeType == Node.DiamondNegAtom:
			oprnd.nodeType = Node.TupleWinDiamondNegAtom
		elif oprnd.nodeType == Node.AtVarAtom:
			oprnd.nodeType = Node.TupleWinAtVarAtom
		elif oprnd.nodeType == Node.AtVarNegAtom:
			oprnd.nodeType = Node.TupleWinAtVarNegAtom
		else:
			syntax_err("Unexpected node %s" % (str(oprnd.nodeType)))

		args_stack.push(oprnd)
	elif (oprt == "box") or (oprt == "diamond"):
		if args_stack.size() < 1:
			syntax_err("Expected one operands for box operation")

		oprnd = args_stack.pop()

		if oprnd.__class__ != Node:
			syntax_err("\"%s\" operator expected a node object" % (oprt))

		if oprnd.nodeType == Node.Atom:
			oprnd.nodeType = Node.BoxAtom if oprt == "box" else Node.DiamondAtom
		elif oprnd.nodeType == Node.NegAtom:
			oprnd.nodeType = Node.BoxNegAtom if oprt == "box" else Node.DiamondNegAtom
		else:
			syntax_err("Unexpected node %s" % (str(oprnd.nodeType)))

		args_stack.push(oprnd)
	elif oprt == "not":
		if args_stack.size() < 1:
			syntax_err("Expected one operands for \"not\" operation")

		oprnd = args_stack.pop()

		if oprnd.nodeType == Node.Atom:
			oprnd.nodeType = Node.NegAtom
		elif oprnd.nodeType == Node.AtAtom:
			oprnd.nodeType = Node.AtNegAtom
		elif oprnd.nodeType == Node.AtVarAtom:
			oprnd.nodeType = Node.NegAtVarAtom
		elif oprnd.nodeType == Node.BoxAtom:
			oprnd.nodeType = Node.NegBoxAtom
		elif oprnd.nodeType == Node.DiamondAtom:
			oprnd.nodeType = Node.NegDiamondAtom
		elif oprnd.nodeType == Node.TimeWinAtom:
			oprnd.nodeType = Node.NegTimeWinAtom
		elif oprnd.nodeType == Node.TimeWinDiamondAtom:
			oprnd.nodeType = Node.NegTimeWinDiamondAtom
		elif oprnd.nodeType == Node.TimeWinBoxAtom:
			oprnd.nodeType = Node.NegTimeWinBoxAtom
		elif oprnd.nodeType == Node.TupleWinAtom:
			oprnd.nodeType = Node.NegTupleWinAtom
		elif oprnd.nodeType == Node.TupleWinDiamondAtom:
			oprnd.nodeType = Node.NegTupleWinDiamondAtom
		elif oprnd.nodeType == Node.TupleWinBoxAtom:
			oprnd.nodeType = Node.NegTupleWinBoxAtom
		else:
			syntax_err("Unexpected node type %s" % (str(oprnd.nodeType)))

		oprnd.isNegated = True
		args_stack.push(oprnd)
	else:
		print("Unknown operator " + str(oprt))
		exit(1)

#def registerScopes(node, scope):
#	if node.__class__ == InnerNode:
#		oprt_name = node.getOperator().getName()
#		if (oprt_name == "time_win" or oprt_name == "tuple_win"):
#			params = node.getOperator().getParams()
#
#			child = node.getChildren()[0]
#			newscope = { "winType" : oprt_name, "winSize" : params[0], "winSizeUnit" : params[2] }
#			registerScopes(child, newscope)
#		else:
#			node.setScope(scope)
#			children = node.getChildren()
#
#			for ch in children:
#				registerScopes(ch, scope)
def _optimize(node):
	if node.__class__ == LeafNode:
		return

	for idx,ch in enumerate(node.getChildren()):
		if (ch.__class__ == InnerNode and (ch.getOperator().getName() == "time_win" or ch.getOperator().getName() == "tuple_win")):
			node.getChildren()[idx] = ch.getChildren()[0]
			node.getChildren()[idx].setParent(node)
	for ch in node.getChildren():
		optimize(ch)

#def optimize(node):
#	_optimize(node)
#	if (node.__class__ == InnerNode and (node.getOperator().getName() == "time_win" or node.getOperator().getName() == "tuple_win")):
#		node.getChildren()[0].setParent(node.getParent())
#		return node.getChildren()[0]
#	return node
#def print_rule(node):
#	if node.__class__ == InnerNode:
#		print("Inner: %s" % (node.getOperator().getName()))
#		children = node.getChildren()
#		for ch in children:
#			print_rule(ch)
#	else:
#		print("Leaf %s" % (node.getFormula().getPredicate()))
#	print("----------")
def parse(rule):
	tokens = tokenizer.tokenize(rule)

	primary_stack = Stack()
	args_stack = Stack()

	head = None
	body = None
	idx = 0
	while idx < len(tokens):
		token = tokens[idx]
		# primary_stack.show()
		# open parenthesis always has the highest precedence
		if token["type"] == tokenizer.TOKEN_OPEN_PARA:
			primary_stack.push(token)
		elif token["type"] == tokenizer.TOKEN_OPRT:
			# Since left has higher precedence than right, when we see an operator token,
			# we must try to make sure all previously pushed operators on the stack are
			# fully parsed before we push any new operator on the stack.
			# So, we go through previous operators, and try to parse them if we have enough
			# information now.
			while not primary_stack.empty():
				lastOprt = primary_stack.top()
				# It must never happen that two unary operators come immediately after
				# each other, without any binary operator between them. They can nest
				# inside one another, but they cannot appear in the same level, and immediately
				# after each other. That is a syntax error if happens.
				if (isUnaryOperator(lastOprt["value"])) and (isUnaryOperator(token["value"])):
					syntax_err("Syntax error near operator " + token["value"])
				# If a binary, or unary operator is already on top of the stack, and another
				# binary operator shows up, we must first finish the parsing of operator on the
				# stack, and then deal with the new operator.
				elif (isOperator(lastOprt["value"])) and (isBinaryOperator(token["value"])):
					if not args_stack.empty():
						primary_stack.pop()
						parse_operator(lastOprt, args_stack)
				# If top of stack is occupied with coma, and/or parenthesis, that means we are
				# still parsing arguments of an operator. In such cases, we cannot empty the stack,
				# because current parsing is not done yet. We need to look into next tokens.
				# So, we break the loop and continue to receive future tokens.
				else:
					break
			primary_stack.push(token)
		elif token["type"] == tokenizer.TOKEN_IDENTIFIER:
			nxt = tokens[idx + 1] if idx + 1 != len(tokens) else None
			if (nxt != None) and (nxt["type"] == tokenizer.TOKEN_OPEN_PARA):
				idx, args = parse_predicate_arguments(idx + 2, tokens)
				#formula = Formula()
				#formula.setPredicate(token["value"])
				pred = token["value"]
				#formula.setArgs(args)
				#args_stack.push(LeafNode(formula.getPredicate(), formula))
				if pred == "MATH":
					assert len(args) == 4, "Expected four parameters for function MATH"
					args_stack.push(Node(Node.Math, args[0], args[1:]))
				elif pred == "COMP":
					assert len(args) == 3, "Expected four parameters for function COMP"
					args_stack.push(Node(Node.Comp, args[0], args[1:]))
				else:
					args_stack.push(Node(Node.Atom, pred, args))
			else:
				#formula = Formula()
				#formula.setPredicate(token["value"])
				pred = token["value"]
				#formula.setArgs([])
				#args_stack.push(LeafNode(formula.getPredicate(), formula))
				args = []
				args_stack.push(Node(Node.Atom, pred, args))
		elif token["type"] == tokenizer.TOKEN_CLOSE_PARA:
			while True:
				if args_stack.empty():
					syntax_err("Expected operand or '('")
				oprt = primary_stack.pop()
				if oprt["value"] == '(':
					break
				parse_operator(oprt, args_stack)
		elif token["type"] == tokenizer.TOKEN_ENTAILMENT_SIGN:
			# In principal, it is possible that the rule has no head.
			# I am not sure if they are useful or not, but they can
			# exist in theory.
			if args_stack.empty():
				print("No head in the rule")
			else:
				# Before parsing the body of the rule
				# we must make sure all operators in the
				# head are dealt with. So, we go through
				# the operator stack, and make sure that
				# all of them are processed.
				while not primary_stack.empty():
					oprt = primary_stack.pop()
					parse_operator(oprt, args_stack, True)
				# Pop the head from the operand stack
				head = args_stack.pop()
				head.returnSttt = head.substitutetable
				#if type(head) != list:
				#	head = head
		idx += 1

	while not primary_stack.empty():
		oprt = primary_stack.pop()
		if oprt["value"] == '(':
			syntax_err("Missing ')' in rule ")
		parse_operator(oprt, args_stack)

	body = args_stack.pop()
	if type(body) != list:
		body = [body]

	body = list(reversed(body))
	# By default we only look at the current time point, namely no window
	#registerScopes(body, {"winType": "time_win", "winSize" : 0, "winSizeUnit": 1})
	#body = optimize(body) # Get rid of window operators
	#print_rule(body)
	#print(body.getChildren()[1].getChildren()[0].getChildren()[0].getChildren()[0].getChildren()[0].getFormula().getPredicate())
	#print(body.getChildren()[0].getChildren()[1].getOperator().getParams())
	#print(head.getChildren()[0].getFormula().getArgs())
	return {
		"head" : head,
		"body" : body
	}
