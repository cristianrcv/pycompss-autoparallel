Python OpenScop Representation
=============================

Based on the OpenScop documentation, a Python reprensentation of the OpenScop format.


### Dependencies

- The unit tests use the [UnitTest][1] Python module
- To run all tests you require the [Nose][2] Python module
- To add code coverage you require [coverage][3] and [codacy-coverage][4] Python modules


### Test with debug

```
python scop_class.py
```


### Test without debug

```
python -O scop_class.py
```


### Run

```
import scop
s = Scop(global, statements, extensions)
```


### Clean

```
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```


[1]: https://docs.python.org/2/library/unittest.html
[2]: https://nose.readthedocs.io/en/latest/
[3]: https://coverage.readthedocs.io/en/coverage-4.4.2/
[4]: https://github.com/codacy/python-codacy-coverage

