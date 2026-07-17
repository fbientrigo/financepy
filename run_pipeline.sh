#!/bin/bash
# FinancePy Daily Pipeline - Scheduled Task Launcher (Linux/Mac)
# This script is designed to run as a cron job at 1 PM daily
# It uses the local .venv (no conda overhead)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Get today's date in YYYY-MM-DD format
TODAY=$(date +%Y-%m-%d)

# Path to .venv Python
PYTHON=.venv/bin/python

# Path to logs
LOGS_DIR=logs
mkdir -p "$LOGS_DIR"
LOG_FILE="$LOGS_DIR/pipeline_${TODAY}.log"

# Run pipeline with logging
{
    echo "========================================"
    echo "Pipeline Run: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================"
    "$PYTHON" run_daily.py --date "$TODAY" --log-level INFO
    echo "[SUCCESS] Pipeline completed at $(date '+%H:%M:%S')"
} >> "$LOG_FILE" 2>&1

exit 0
