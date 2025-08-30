.PHONY: help
help:
	@echo "Available targets:"
	@echo "  env                        - Synchronize the uv environment"
	@echo "  install_pre_commit_hooks   - Install pre-commit hooks"
	@echo "  lint                       - Lint the code"
	@echo "  test                       - Run tests"
	@echo "  docs-live                  - Generate documentation with live reload"
	@echo "  docs-markdown              - Generate documentation in Markdown format"
	@echo "  docs-html                  - Generate documentation in HTML format"


.PHONY: env
env:
	uv sync --all-groups

.PHONY: install_pre_commit_hooks
install_pre_commit_hooks:
	pre-commit install -t pre-commit
	pre-commit install -t pre-push

.PHONY: lint
lint:
	mkdir -p /tmp/artifacts
	ruff format .
	ruff check . --fix
	uv run mypy --version
	uv run mypy --cache-dir /dev/null --junit-xml /tmp/artifacts/mypy.xml src

.PHONY: test
test:
	uv run --no-sync pytest src

.PHONY: docs-live
docs-live:
	@echo 'Generating documentation with live reload'
	sphinx-autobuild docs _build/html

.PHONY: docs-markdown
docs-markdown:
	@echo 'Generating documentation in Markdown format'
	sphinx-build -M markdown docs /tmp/markdown

.PHONY: docs-html
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
