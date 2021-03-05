.PHONY: build

install:
	python -m pip install -e .
	python -m pip install -r requirements-test.txt

clean:
	rm -rf dist/ build/

test:
	python -m pytest

build:
	python setup.py sdist bdist_wheel

check:
	twine check dist/*

upload:
	twine upload --repository=http-prompt dist/*

release: test clean build check upload
