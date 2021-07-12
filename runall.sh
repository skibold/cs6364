#! /bin/bash
inp=$1
d=$2

progs=('ABOpening.py' 'ABGame.py' 'MiniMaxOpening.py' 'MiniMaxGame.py' 'MiniMaxOpeningBlack.py' 'MiniMaxGameBlack.py' 'MiniMaxOpeningImproved.py' 'MiniMaxGameImproved.py')

for prog in ${progs[@]}
do
	outf=$(basename $prog .py).txt
	python $prog $inp $outf $d
done
