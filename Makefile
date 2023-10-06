install:
	poetry install
dev:
	poetry run flask --app page_analyzer:app run
lint:
	poetry run flake8 page_analyzer
test:
	poetry run pytest
check:  
	test lint
test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml
