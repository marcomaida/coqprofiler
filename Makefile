.PHONY: example

clean:
	rm -f raw/*
	rm -f example/example.csv
	rm -f example/example.pdf
	rm -f example/example.txt

example:
	./coqprofiler.py example/example.v
