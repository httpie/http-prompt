install:
	python -m pip install -e .
	python -m pip install -r requirements-test.txt

test:
	python -m pytest
