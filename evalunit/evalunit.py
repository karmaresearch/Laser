from evaltree.innernode import InnerNode
from evaltree.leafnode  import LeafNode
############################################
def gc(node, now):
	for row in node.substitutetable.copy():
		if row[1] < now:
			node.substitutetable.delete_row(row)
	if node.__class__ == InnerNode:
		for ch in node.getChildren():
			gc(ch, now)
############################################
def generate_head_atoms(rule):
	body_var = rule.get_body().substitutetable.columns
	head_var = rule.get_head().substitutetable.get_column_names()

	derivations = set()
	for row in rule.get_body().substitutetable:
		elem = [rule.get_head().getFormula().getPredicate()]
		for v in head_var:
			if v in body_var:
				elem.append(row[body_var[v]])
		derivations.add(tuple(elem))
	return list(derivations)
############################################
def evaluate(rule, stream, now):
	gc(rule.get_body(), now)
	evaluation_result = distributed_input_stream(rule, stream, now)
	return generate_head_atoms(rule) if evaluation_result else []
