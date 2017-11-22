PyCOMPSs and PLUTO integration
=============================

PyCOMPSs and PLUTO integration using OpenSCOP.

## Table of Contents

* [C - OpenScop Converter](#c-openscop-converter)
* [Python - OpenScop Converter](#python-openscop-converter)


## C - OpenScop Converter

Uses a small C program to convert from C to OpenScop using CLAN.


### Dependencies

- A valid CLAN installation
- A valid OpenScop installation


### Build

```
make
```

### Run

```
make exec
```

### Clean

```
make clean
```


## Python - OpenScop Converter

Based on the OpenScop and CLAN documentation, takes a Python code, builds its representation and bulks it on OpenScop format.


### Dependencies

- The unit tests use the [UnitTest][1] Python module
- To run all tests you require the [Nose][2] Python module
- To add code coverage you require [coverage][3] and [codacy-coverage][4] Python modules

### Run all unit tests

```
python nose_tests.py
```

### Run a single unit test

```
cd ${class_folder}
python ${class_name}_class.py
```

### Run examples

```
python converter_py2scop.py
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

