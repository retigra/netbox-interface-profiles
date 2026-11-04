sources = interface_profiles

.PHONY: test format lint unittest pre-commit docs docs-build clean
test: format lint unittest

format:
	ruff check --select I --fix $(sources) tests
	ruff format $(sources) tests

lint:
	ruff check $(sources) tests

docs:
	cd docs && npm ci && npm run dev

docs-build:
	cd docs && npm ci && npm run build

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site docs/dist docs/.astro
