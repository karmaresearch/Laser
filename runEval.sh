#!/bin/bash

ntriples=( 200 400 800 )
win_size=( 1 20 40 80 )
for exp in evalDiamond evalBox evalSingleJoin evalMultipleRules evalCoolingSystem; do
	for win in "${win_size[@]}"; do
		for triples in "${ntriples[@]}"; do
			if [ "$exp" == "evalMultipleRules" ]; then
				for nRules in 10 20 50 100; do
					pypy -OO eval.py $exp $nRules $win $triples
				done
			else
				pypy -OO eval.py $exp $win $triples
			fi
		done
	done
done
