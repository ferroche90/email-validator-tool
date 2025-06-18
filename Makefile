# Makefile for email-validator-tool

.PHONY: lint format test run install

lint:
	flake8 email_validator_tool tests
	black --check email_validator_tool tests

format:
	isort email_validator_tool tests
	black email_validator_tool tests

test:
	pytest

run:
	python -m email_validator_tool.cli run emails.csv --output out.csv

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
