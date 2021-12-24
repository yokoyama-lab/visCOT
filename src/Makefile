all:
	python3 visualize.py

clean:
	$(RM) -rf visualize/__pycache__ visualize/parser.out visualize/parsetab.py

test:
	echo "a0()" | python3 visualize.py
	echo "a0(a+(l+))" | python3 visualize.py
	echo "a0(a+(l+).a+(l+))" | python3 visualize.py
	echo "B0+(l+,)" | python3 visualize.py
	echo "B0+(l+,c-(l-,))" | python3 visualize.py
	echo "B0+(l+,c-(l-,).c-(l-,))" | python3 visualize.py
	echo "B0-(l-,)" | python3 visualize.py
	echo "B0+(b+-(l+,l-),c-(l-,).c-(l-,).c-(l-,))" | python3 visualize.py
	echo "B0+(b+-(l+,l-),c-(B-{},).c-(l-,).c-(l-,))" | python3 visualize.py
	echo "B0-(b-+(b-+(l-,l+),B+{}),c+(B+{},).c+(l+,).c+(l+,))" | python3 visualize.py
	echo "B0+(b+-(b+-(l+,l-),B-{}),c-(B-{},).c-(l-,).c-(l-,))" | python3 visualize.py
