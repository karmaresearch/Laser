############################################
TOKEN_VAR             = "VAR"
TOKEN_OPRT            = "OPRT"
TOKEN_OPEN_PARA       = "OPEN_PARA"
TOKEN_CLOSE_PARA      = "CLOSE_PARA"
TOKEN_ENTAILMENT_SIGN = ":-"
TOKEN_IDENTIFIER      = "Identifier"
############################################
def recognize(s):
	s = s.strip()
	if (s == "@")         or \
	   (s == "and")       or \
	   (s == "or")        or \
	   (s == "not")       or \
	   (s == "box")       or \
	   (s == "diamond")   or \
	   (s == "time_win")  or \
	   (s == "tuple_win") or \
	   (s == "predicate_win"):
		return {
			"value" : s,
			"type"  : TOKEN_OPRT
		}
	elif s == ":-":
		return {
			"value" : s,
			"type"  : TOKEN_ENTAILMENT_SIGN
		}
	return {
		"value" : s,
		"type"  : TOKEN_IDENTIFIER
	}
############################################
def tokenize(rule):
	tokens = []
	buf = ""
	i = 0
	while i < len(rule):
		c = rule[i]
		if c == '\'':
			Vbuf = buf.strip()
			if len(buf) > 0:
				tokens.append(recognize(buf))
				buf = ""
			i += 1
			while True:
				c = rule[i]
				if c == '\'':
					break
				buf += c
				i += 1
			tokens.append({
				'value' : buf,
				'type'  : TOKEN_IDENTIFIER,
			})
			buf = ""
		elif c == ' ':
			buf = buf.strip()
			if len(buf) > 0:
				tokens.append(recognize(buf))
				buf = ""
		elif c == ',':
			Vbuf = buf.strip()
			if len(buf) > 0:
				tokens.append(recognize(buf))
				buf = ""
			tokens.append({
				'value' : c,
				'type'  : TOKEN_OPRT
			})
			buf = ""
		elif c == '(':
			buf = buf.strip()
			if len(buf) > 0:
				tokens.append(recognize(buf))
				buf = ""
			tokens.append({
				'value' : c,
				'type'  : TOKEN_OPEN_PARA
			})
			buf = ""
		elif c == ')':
			buf = buf.strip()
			if len(buf) > 0:
				tokens.append(recognize(buf))
				buf = ""
			tokens.append({
				'value' : c,
				'type'  : TOKEN_CLOSE_PARA
			})
			buf = ""
		else:
			buf += c
		i += 1
	if len(buf) != 0:
		buf = buf.strip()
		if len(buf) > 0:
			tokens.append(recognize(buf))
			buf = ""
	return tokens
