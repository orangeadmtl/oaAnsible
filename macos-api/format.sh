#!/bin/bash

# Format and lint script for macos-api
# Uses the shared oaPangaea/.venv for consistency with monorepo development
# This script NEVER fails - it reports issues for manual review

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

echo "🎨 Formatting and linting macos-api..."
echo "📍 Using virtual environment: $VENV_PATH"
echo "📁 Working directory: $SCRIPT_DIR"

cd "$SCRIPT_DIR"

# Track results
BLACK_RESULT=0
ISORT_RESULT=0
FLAKE8_RESULT=0
MYPY_RESULT=0

# Phase 1: Format (auto-fix)
echo ""
echo "🔧 Phase 1: Auto-formatting code..."

echo "  Running black..."
if black .; then
    echo "  ✅ Black formatting: APPLIED"
else
    echo "  ❌ Black formatting: FAILED"
    BLACK_RESULT=1
fi

echo "  Running isort..."
if isort .; then
    echo "  ✅ Import sorting: APPLIED"
else
    echo "  ❌ Import sorting: FAILED"
    ISORT_RESULT=1
fi

# Phase 2: Lint (check-only)
echo ""
echo "🔍 Phase 2: Linting code..."

echo "  Running flake8..."
if flake8 .; then
    echo "  ✅ Flake8: PASS"
else
    echo "  ⚠️  Flake8: Issues found (see output above)"
    FLAKE8_RESULT=1
fi

echo "  Running mypy..."
if mypy .; then
    echo "  ✅ MyPy: PASS"
else
    echo "  ⚠️  MyPy: Issues found (see output above)"
    MYPY_RESULT=1
fi

# Summary
echo ""
echo "📋 Summary:"
echo "==========="

if [ $BLACK_RESULT -eq 0 ] && [ $ISORT_RESULT -eq 0 ]; then
    echo "✅ Code formatting: All applied successfully"
else
    echo "❌ Code formatting: Some tools failed (check errors above)"
fi

if [ $FLAKE8_RESULT -eq 0 ]; then
    echo "✅ Flake8 linting: No issues found"
else
    echo "⚠️  Flake8 linting: Issues found - manual review needed"
    echo "   💡 Common fixes: Remove unused imports, fix line lengths"
fi

if [ $MYPY_RESULT -eq 0 ]; then
    echo "✅ Type checking: No issues found"
else
    echo "⚠️  Type checking: Issues found - manual review recommended"
    echo "   💡 Consider adding type annotations for better code quality"
fi

echo ""
if [ $FLAKE8_RESULT -eq 0 ] && [ $MYPY_RESULT -eq 0 ]; then
    echo "🎉 All good! Code is properly formatted and clean."
else
    echo "📝 Manual review needed for the issues reported above."
    echo "   The code has been formatted, but some quality issues remain."
fi

echo ""
echo "💡 Tip: Run 'git diff' to see what was automatically changed"
echo "💡 Tip: Use './check.sh' for CI-friendly checking without modifications"

# Always exit successfully - this is a development tool, not a blocker
exit 0