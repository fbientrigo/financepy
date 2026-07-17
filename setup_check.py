#!/usr/bin/env python
"""
Quick setup script for FinancePy minimal environment.
Verifies logging is working and all dependencies are installed.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verify Python 3.10+"""
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required. Current: {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")

def check_dependencies():
    """Verify all required packages are installed."""
    required = {
        "pandas": "pandas",
        "numpy": "numpy",
        "scipy": "scipy",
        "yaml": "pyyaml",
        "plotly": "plotly",
        "streamlit": "streamlit",
        "yfinance": "yfinance",
    }
    
    print("\nChecking dependencies...")
    all_ok = True
    for import_name, pkg_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✓ {pkg_name}")
        except ImportError:
            print(f"  ❌ {pkg_name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_logging():
    """Verify logging configuration is working."""
    print("\nTesting logging configuration...")
    try:
        from src.logger_config import setup_logging, get_logger
        setup_logging("INFO")
        logger = get_logger("financepy.setup")
        
        logger.debug("Debug message (should not appear in INFO mode)")
        logger.info("✓ Logging is working correctly")
        logger.warning("Warning: This is a test warning")
        
        return True
    except Exception as e:
        print(f"  ❌ Logging test failed: {e}")
        return False

def check_config():
    """Verify config files exist."""
    print("\nChecking configuration files...")
    files = [
        "configs/config.yaml",
        "configs/assets.txt",
        "environment-minimal.yml",
        "requirements-minimal.txt",
    ]
    
    all_ok = True
    for f in files:
        path = Path(f)
        if path.exists():
            print(f"  ✓ {f}")
        else:
            print(f"  ❌ {f} - NOT FOUND")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("FinancePy - Minimal Setup Verification")
    print("=" * 60)
    
    check_python_version()
    
    deps_ok = check_dependencies()
    logging_ok = check_logging()
    config_ok = check_config()
    
    print("\n" + "=" * 60)
    if deps_ok and logging_ok and config_ok:
        print("✓ All checks passed! Ready to run pipeline.")
        print("\nQuick start:")
        print("  python run_daily.py --date 2025-12-30 --log-level INFO")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Install dependencies:")
        print("  conda env create -f environment-minimal.yml")
        print("  Or: pip install -r requirements-minimal.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
