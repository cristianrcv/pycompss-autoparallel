Python Code Loader
=============================

Loads the content of a Python function using the Inspect module


### Dependencies


### Test with debug

```
export PYTHONPATH=${git_base_dir}
python nose_tests.py
```


### Test without debug                                                                                                                                                                                                                                                         

```
export PYTHONPATH=${git_base_dir}
python -O nose_tests.py
```


### Clean

```
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```


### Run coverage

```
coverage run --omit="/usr/lib/*" nose_tests.py
coverage report -m
coverage xml
```


