.PHONY: requirements
requirements:
	poetry install --no-dev

.PHONY: requirements_dev
requirements_dev:
	poetry install

.PHONY: lint
lint:
	make requirements_dev
	poetry run flake8 --exclude=env,venv --max-line-length=120
	poetry run black --check .

.PHONY: format
format:
	make requirements_dev
	poetry run black .

.PHONY: typecheck
typecheck:
	make requirements_dev
	poetry run mypy libs
