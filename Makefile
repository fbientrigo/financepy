.PHONY: qa test clean install

PYTHON := python
PIP := pip

qa: install test
	@echo "Running QA checks..."
	$(PYTHON) scripts/qa.py

dashboard:
	@echo "Starting Dashboard..."
	streamlit run app/dashboard.py

test:
	$(PYTHON) -m unittest discover tests

install:
	$(PIP) install -r requirements.txt || echo "No requirements.txt found, skipping install."

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf test_reports test_cache
