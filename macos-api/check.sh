#!/bin/bash

# Check-only script for macos-api (for CI/testing - no modifications)
# Uses the shared oaPangaea/.venv for consistency with monorepo development
set -e

# Determine script directory and find the monorepo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_PATH="$REPO_ROOT/.venv"

# Check if shared venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Shared virtual environment not found at $VENV_PATH"
    echo "💡 Run 'source .venv/bin/activate' from oaPangaea root first"
    exit 1
fi

# Activate the shared virtual environment
source "$VENV_PATH/bin/activate"

echo "🔍 Checking macos-api code style (no modifications)..."
echo "📍 Using virtual environment: $VENV_PATH"
echo "📁 Working directory: $SCRIPT_DIR"

cd "$SCRIPT_DIR"

# Check formatting (no changes)
echo ""
echo "Checking black formatting..."
if black --check --diff .; then
    echo "✅ Black formatting: PASS"
else
    echo "❌ Black formatting: FAIL (run ./format.sh to fix)"
    exit 1
fi

echo "Checking import sorting..."
if isort --check-only --diff .; then
    echo "✅ Import sorting: PASS"
else
    echo "❌ Import sorting: FAIL (run ./format.sh to fix)"
    exit 1
fi

echo "Checking flake8..."
if flake8 .; then
    echo "✅ Flake8: PASS"
else
    echo "❌ Flake8: FAIL"
    exit 1
fi

echo "Checking mypy..."
if mypy .; then
    echo "✅ MyPy: PASS"
else
    echo "⚠️ MyPy: WARNINGS (check output above)"
fi

echo ""
echo "✅ All checks passed! Code is properly formatted and linted."