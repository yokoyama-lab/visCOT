all:
	python3 visualize.py

clean:
	$(RM) -rf visualize/__pycache__ visualize/parser.out visualize/parsetab.py

test:
	echo "B0-(b-+(b-+(l-,l+),B+{n}),(cons(c+(B+{n},n),cons(c+(l+,n),cons(c+(l+,n),n)))))" | python3 visualize.py
	echo "B0+(b+-(b+-(l+,l-),B-{n}),(cons(c-(B-{n},n),cons(c-(l-,n),cons(c-(l-,n),n)))))" | python3 visualize.py
	echo "a0()" | python3 visualize.py
	echo "a0(a+(l+))" | python3 visualize.py
	echo "a0(a+(l+).a+(l+))" | python3 visualize.py
	echo "B0+(l+,())" | python3 visualize.py
	echo "B0+(l+,(c-(l-,n)))" | python3 visualize.py
	echo "B0+(l+,(c-(l-,n).c-(l-,n)))" | python3 visualize.py
	echo "B0-(l-,())" | python3 visualize.py
	echo "B0+(b+-(l+,l-),(c-(l-,).c-(l-,).c-(l-,)))" | python3 visualize.py
	echo "B0+(b+-(l+,l-),(c-(B-{},).c-(l-,).c-(l-,)))" | python3 visualize.py
