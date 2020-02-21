UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S), Linux)
	python = python3
endif
ifeq ($(UNAME_S), Darwin)
	python = python
endif

clean:
	rm -rf ./__pycache__
	rm -rf ./classes/__pycache__
	rm -rf ./cogs/__pycache__
	rm -rf ./utils/__pycache__

install:
	$(python) -m pip install -r requirements.txt

lint:
	flake8

run:
	$(python) launcher.py
