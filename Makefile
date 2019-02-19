all: deps

deps:
	./install_deps.sh

clean:
	rm -rf classes

reallyclean: clean
	rm -rf lib deps

.PHONY: all compile test clean reallyclean
