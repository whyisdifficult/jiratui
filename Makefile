.PHONY: lint
lint:
	ruff format .
	ruff check . --fix

.PHONY: test
test:
	pytest src

docs-live:
	@echo 'Generating documentation with live reload'
	sphinx-autobuild docs _build/html

docs-markdown:
	@echo 'Generating documentation in Markdown format'
	sphinx-build -M markdown docs /tmp/markdown

docs-html:
ifeq ($(strip $(OUTPUT_DIR)),)
	@echo 'Generating documentation in HTML format into docs/_build/html'
	sphinx-build docs docs/_build/html --doctree-dir /tmp
	rm -rf /tmp/index.doctree
else
	@echo 'Generating documentation in HTML format into $(OUTPUT_DIR)'
	sphinx-build docs ${OUTPUT_DIR} --doctree-dir /tmp
	rm -rf /tmp/index.doctree
endif
