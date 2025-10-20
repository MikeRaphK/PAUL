#!/bin/bash

# You can change this
SYMPY_PATH="./sympy__sympy-20590"

ORIG_DIR="$(pwd)"
VENV_PATH="$SYMPY_PATH/venv"
PYTEST_INI_PATH="$SYMPY_PATH/pytest.ini"
TEST_FILE="$SYMPY_PATH/sympy/core/tests/test_basic.py"

# Install sympy with dependencies
git clone https://github.com/sympy/sympy.git "$SYMPY_PATH"
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
pip install setuptools mpmath pytest pytest-doctestplus
git -C "$SYMPY_PATH" checkout cffd4e0f86fefd4802349a9f9b19ed70934ea354
sed -i 's/^doctestplus =/doctest_plus =/' "$PYTEST_INI_PATH"
cd "$SYMPY_PATH"
python setup.py install
cd "$ORIG_DIR"

### This should pass
echo -e "\n\n\n=================================================="
echo "Running tests (should pass)..."
echo "=================================================="
pytest "$TEST_FILE" -vvvv

### Append new test
cat << 'EOF' >> "$TEST_FILE"

def test_immutable(): 
    assert not hasattr(b1, '__dict__') 
    with raises(AttributeError): 
        b1.x = 1
EOF

### This should fail
echo -e "\n\n\n=================================================="
echo "Running tests with new failing test (should fail)..."
echo "=================================================="
pytest "$TEST_FILE::test_immutable" -vvvv

# Create a new branch so that we can easily reset to this point
git -C "$SYMPY_PATH" checkout -b paul-branch
git -C "$SYMPY_PATH" add .
git -C "$SYMPY_PATH" commit -m "Basis for PAUL"
