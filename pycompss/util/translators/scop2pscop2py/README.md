OpenScop - Parallel OpenScop Translator                                                                                                                                                                                                                                        
=============================

Uses the PLUTO tool to generate parallel SCOP code from a source SCOP representation


### Dependencies

- A valid PLUTO installation
- The unit tests use the [UnitTest][1] Python module
- To run all tests you require the [Nose][2] Python module
- To add code coverage you require [coverage][3] and [codacy-coverage][4] Python modules


### Test with debug

```
python translator_scop2pscop2py.py
```


### Test without debug

```
python -O translator_scop2pscop2py.py
```


### Run

```
import Scop2PScop2Py
Scop2PScop2Py.translate(source_file, output_file)
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

