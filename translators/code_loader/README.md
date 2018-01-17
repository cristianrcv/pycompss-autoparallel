Python Code Loader
=============================

Loads the content of a Python function using the Inspect module


### Dependencies


### Test

```
python nose_tests.py
```


### Run

```
import CodeLoader
func_source = CodeLoader.load(func)
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


