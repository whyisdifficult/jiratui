.PHONY: lint
lint:
	ruff format .
	ruff check . --fix

.PHONY: test
test:
	pytest src
