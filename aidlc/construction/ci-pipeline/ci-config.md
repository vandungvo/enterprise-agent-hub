# Continuous Integration Pipeline Specification

## GitHub Actions Workflow (`.github/workflows/ci.yml`)

```yaml
name: CI Quality Gate & Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-and-verify:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install flake8 pytest pytest-cov

      - name: Code Quality & Linting
        run: |
          # Stop build if there are Python syntax errors or undefined names
          flake8 app tests --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Run Test Suite with Pytest
        run: |
          pytest -v --cov=app --cov-report=term-missing

      - name: Policy Regression Guard
        run: |
          # Bắt buộc 100% test policy phải vượt qua
          pytest tests/test_policy.py -v
```
