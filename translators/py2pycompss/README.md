Python - PyCOMPSs Translator
=============================

Translates a Python with parallel annotations to PyCOMPSs code


### Dependencies

- The unit tests use the [UnitTest][1] Python module
- To run all tests you require the [Nose][2] Python module
- To add code coverage you require [coverage][3] and [codacy-coverage][4] Python modules


### Test with debug

```
python nose_tests.py
```


### Test without debug                                                                                                                                                                                                                                                         

```
python -O nose_tests.py
```


### Run

```
python translator_py2scop.py -i <source> -o <output>
```


### Clean

```
find . -name "*.pyc" -delete
```


### Run coverage

```
coverage run --omit="/usr/lib/*" nose_tests.py
coverage report -m
coverage xml
export CODACY_PROJECT_TOKEN=%Project_Token%
python-codacy-coverage -r coverage.xml
rm -f coverage.xml
```


[1]: https://docs.python.org/2/library/unittest.html
[2]: https://nose.readthedocs.io/en/latest/
[3]: https://coverage.readthedocs.io/en/coverage-4.4.2/
[4]: https://github.com/codacy/python-codacy-coverage

