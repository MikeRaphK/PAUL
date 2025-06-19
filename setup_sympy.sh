git clone https://github.com/sympy/sympy.git
cd sympy
python3 -m venv venv
. ./venv/bin/activate
git checkout cffd4e0f86fefd4802349a9f9b19ed70934ea354
pip install setuptools
python3 setup.py install

##### APPEND THIS TO sympy/core/tests/test_basic.py #####
cat << EOF >> sympy/core/tests/test_basic.py

def test_immutable():
    assert not hasattr(b1, '__dict__')
    with raises(AttributeError):
        b1.x = 1
EOF

##### THIS SHOULD FAIL #####
pytest sympy/core/tests/test_basic.py -vvvv