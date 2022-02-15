#all:
#	python3 visualize.py

all: test

clean:
	$(RM) -rf visualize/__pycache__ visualize/parser.out visualize/parsetab.py

test:
	echo "a0" | python3 visualize.py
	echo "b++" | python3 visualize.py
	echo "b--" | python3 visualize.py
	echo "b+-" | python3 visualize.py
	echo "b-+" | python3 visualize.py
	echo "B+" | python3 visualize.py
	echo "B-" | python3 visualize.py
	echo "s+" | python3 visualize.py
	echo "s-" | python3 visualize.py
	echo "a0(a+(s+))" | python3 visualize.py
	echo "a0(a+.a-.a2)" | python3 visualize.py
	echo "a0(a+(s+).a-(s-))" | python3 visualize.py
	echo "a0(a2(,))" | python3 visualize.py
	echo "a0(a2(c+,))" | python3 visualize.py
	echo "a0(a2(,c-))" | python3 visualize.py
	echo "a0(a2(c+,c-))" | python3 visualize.py
	echo "a0(a2(c+.c+,c-.c-))" | python3 visualize.py
	echo "b++{s+,s+}" | python3 visualize.py
	echo "b--{s-,s-}" | python3 visualize.py
	echo "b+-(s+,s-)" | python3 visualize.py
	echo "b+-(B+,s-)" | python3 visualize.py
	echo "b+-(s+,B-)" | python3 visualize.py
	echo "b-+(s-,s+)" | python3 visualize.py
	echo "b-+(s-,B+)" | python3 visualize.py
	echo "b-+(B-,s+)" | python3 visualize.py
	echo "B+{c+}" | python3 visualize.py
	echo "b+-(b++,b-+(b-+,s+))" | python3 visualize.py
	echo "b+-(b+-(b+-,s-),s-)" | python3 visualize.py
	echo "b+-(B+{c+.c+},s-)" | python3 visualize.py
	echo "b+-(B+{c+},s-)" | python3 visualize.py
	echo "b+-(B+{c+(b++,c-)},s-)" | python3 visualize.py
	echo "B+{c+(s+,c-)}" | python3 visualize.py
	echo "B+{c+.c+}" | python3 visualize.py
	echo "b+-(B+{L+},B-{L-})" | python3 visualize.py
	echo "a0(a+.a+.a2(c+,L-).a-.a-)" | python3 visualize.py
	echo "b+-(B+{c+.c+.c+(b++,c-)},s-)" | python3 visualize.py
	echo "a0(a+(s+).a-(s-).a2(c+(s+,L-),L-))" | python3 visualize.py
	echo "a0(a+.a-.a2(c+,L-))" | python3 visualize.py
	echo "a0(a+(s+).a-(s-).a2(c+(s+,L-),L-))" | python3 visualize.py
