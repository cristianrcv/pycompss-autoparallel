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

- The unit tests use the UnitTest Python module
- To run all tests you require the Nose Python module


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

