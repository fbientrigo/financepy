.PHONY: qa test clean install install-minimal setup-env dashboard help

PYTHON := python
PIP := pip
CONDA := conda

.DEFAULT_GOAL := help

help:
	@echo "FinancePy - Makefile Commands"
	@echo "=============================="
	@echo ""
	@echo "Environment Setup:"
	@echo "  make setup-env         Create minimal conda environment"
	@echo "  make install-minimal   Install minimal dependencies (pip)"
	@echo "  make install           Install full dependencies (pip)"
	@echo ""
	@echo "Development:"
	@echo "  make test              Run unit tests"
	@echo "  make qa                Run QA checks (tests + linting)"
	@echo ""
	@echo "Production:"
	@echo "  make run-daily         Run daily pipeline"
	@echo "  make dashboard         Start Streamlit dashboard"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             Clean cache/artifacts"

setup-env:
	@echo "Creating minimal conda environment from environment-minimal.yml..."
	$(CONDA) env create -f environment-minimal.yml --yes
	@echo ""
	@echo "✓ Environment created. Activate with:"
	@echo "  conda activate financepy"

install-minimal:
	@echo "Installing minimal production dependencies..."
	$(PIP) install -r requirements-minimal.txt

install:
	@echo "Installing full dependencies..."
	$(PIP) install -r requirements.txt

qa: install test
	@echo "Running QA checks..."
	$(PYTHON) scripts/qa.py

test:
	$(PYTHON) -m unittest discover tests

dashboard:
	@echo "Starting Dashboard..."
	streamlit run app/dashboard.py

run-daily:
	@echo "Running daily pipeline..."
	$(PYTHON) run_daily.py

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf test_reports test_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
