# FinancePy Installation Guide

This document provides multiple installation methods for FinancePy. Choose the one that best fits your setup.

---

## Quick Start with Conda (Recommended)

**Requirements:** Conda or Miniconda installed

### Option 1A: Full Installation (All Dependencies)

```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate financepy

# Verify installation
python -c "import pandas, numpy, yfinance, plotly, streamlit; print('✓ All packages installed')"
```

### Option 1B: Fast Installation (One-liner)

```bash
conda create -n financepy -c conda-forge python=3.11 \
  pandas>=2.2 numpy>=2.0 scipy>=1.11 \
  yfinance>=0.2.32 pyyaml>=6.0 \
  plotly>=5.17 streamlit>=1.28 \
  pytest pytest-cov

conda activate financepy
```

### Option 1C: Minimal Installation (Core Only)

```bash
conda create -n financepy -c conda-forge python=3.11 \
  pandas numpy scipy yfinance pyyaml

conda activate financepy
```

Then install optional visualization packages:
```bash
conda install -n financepy -c conda-forge plotly streamlit
```

---

## Installation with Pip

**Requirements:** Python 3.10+ and pip installed

### Option 2A: Using PyProject (Modern)

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install with just core dependencies
pip install -e .
```

### Option 2B: Using Requirements Files

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies too
pip install -r requirements-dev.txt
```

### Option 2C: One-liner Installation

```bash
pip install pandas>=2.2 numpy>=2.0 scipy>=1.11 yfinance>=0.2.32 \
  pyyaml>=6.0 plotly>=5.17 streamlit>=1.28 pytest pytest-cov
```

---

## Installation with Poetry (Alternative)

If you prefer Poetry for dependency management:

```bash
# Install depends on having a poetry.lock file
# You can generate it from pyproject.toml:
poetry install

# Or use optional groups:
poetry install --with dev
```

---

## Verify Installation

After any installation method, verify everything works:

```bash
# Check core packages
python -c "
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
print('✓ Core packages OK')
"

# Check imports from financepy structure
python -c "
from src.data import DataLoader
from src.indicators.common import CommonIndicators
from src.signals.basic import BasicSignals
print('✓ FinancePy modules OK')
"

# Try running tests
pytest tests/test_indicators.py -v
```

---

## Development Setup

For contributing to FinancePy:

```bash
# 1. Create environment with dev tools
conda env create -f environment.yml

# 2. Activate
conda activate financepy

# 3. Install pre-commit hooks (if available)
# pre-commit install

# 4. Run tests
pytest tests/ -v --tb=short

# 5. Format and lint code
black src/ app/ scripts/ tests/
ruff check src/ app/ scripts/ tests/ --fix
```

---

## Docker Alternative (Optional)

Create a `Dockerfile`:

```dockerfile
FROM conda/miniconda3:latest

WORKDIR /app

COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "financepy", "/bin/bash", "-c"]

COPY . .
RUN pip install -e .

ENTRYPOINT ["conda", "run", "-n", "financepy", "python"]
CMD ["run_daily.py"]
```

Build and run:
```bash
docker build -t financepy:latest .
docker run -v $(pwd)/data_cache:/app/data_cache financepy
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'yfinance'`

**Solution:** Make sure yfinance is installed:
```bash
pip install yfinance>=0.2.32
# or
conda install -c conda-forge yfinance>=0.2.32
```

### Issue: `StreamlitAPIException: Streamlit requires raw socket access`

**Solution:** Use `streamlit run` instead of `python run`:
```bash
streamlit run app/dashboard.py
```

### Issue: Dependency conflicts with numpy/pandas

**Solution:** Use specified versions from environment.yml:
```bash
conda env remove -n financepy
conda env create -f environment.yml
```

### Issue: `YAML parsing error in config.yaml`

**Solution:** Ensure pyyaml is installed:
```bash
pip install pyyaml>=6.0
# or
conda install pyyaml
```

---

## Environment Management Commands

### List installed packages
```bash
conda list                    # If using conda
pip list                      # If using pip
```

### Update all packages
```bash
conda update -n financepy --all

# or selective updates
conda update -n financepy pandas numpy plotly
```

### Remove environment
```bash
conda remove -n financepy --all
```

### Export current environment
```bash
conda env export > environment-lock.yml

# Then recreate from lock file:
conda env create -f environment-lock.yml
```

---

## Version Reference

| Package | Min Version | Reason |
|---------|------------|--------|
| Python | 3.10 | Type hints (PEP 604), pattern matching |
| pandas | 2.2.0 | Performance, stability, dtype improvements |
| numpy | 2.0 | Linear algebra stability, eigenvalue precision |
| yfinance | 0.2.32 | Recent fixes for Yahoo Finance API |
| streamlit | 1.28.0 | Recent sidebar improvements, caching |
| plotly | 5.17 | Recent bug fixes, performance |
| pyyaml | 6.0 | Stability and parsing improvements |
| pytest | 7.4 | Modern test framework capabilities |

---

## Next Steps

After installation:

1. **Run the EOD pipeline:**
   ```bash
   python run_daily.py --date 2025-12-30
   ```

2. **Launch the dashboard:**
   ```bash
   make dashboard
   # or
   streamlit run app/dashboard.py
   ```

3. **Run tests:**
   ```bash
   make qa
   # or
   pytest tests/ -v
   ```

4. **Read the configuration:**
   - See `configs/config.yaml` for parameters
   - See `REFACTOR_DECISIONS.md` for technical decisions

---

## Contributing

Development workflow:
```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Install with dev dependencies
pip install -e ".[dev]"

# 3. Make changes
# 4. Run tests
pytest tests/ -v

# 5. Format code
black src/ app/ scripts/
ruff check --fix

# 6. Commit and push
git commit -m "Add my feature"
git push origin feature/my-feature
```

---

## Support

For issues or questions:
- Check `README.md` for project overview
- See `REFACTOR_DECISIONS.md` for architecture decisions
- Review `.sisyphus/` for technical debt tracking
