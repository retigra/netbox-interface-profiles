sources = interface_profiles

.PHONY: test format lint unittest docker-test pre-commit docs docs-build clean
test: format lint unittest

format:
	ruff check --select I --fix $(sources) tests
	ruff format $(sources) tests

lint:
	ruff check $(sources) tests

# Run the test suite in the Docker development environment, with the same configuration as CI.
# Uses a separate test database, so the data of the development environment is left untouched.
docker-test:
	cd docker && docker compose up -d --wait postgres valkey
	cd docker && docker compose run --rm --no-deps --entrypoint "" \
		-e DB_HOST=postgres -e REDIS_HOST=valkey -e REDIS_PASSWORD=netbox netbox bash -c '\
		source /opt/netbox/venv/bin/activate && \
		uv pip install -q -e /opt/interface-profiles tblib && \
		cp /opt/interface-profiles/testing/configuration.py /opt/netbox/netbox/netbox/configuration.py && \
		cd /opt/netbox/netbox && \
		python manage.py test $(or $(TESTS),interface_profiles.tests) --parallel --keepdb --noinput'

docs:
	cd docs && npm ci && npm run dev

docs-build:
	cd docs && npm ci && npm run build

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf *.egg-info
	rm -rf .tox dist site docs/dist docs/.astro
