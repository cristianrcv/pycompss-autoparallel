Python Code Loader
=============================

Loads the content of a Python function using the Inspect module


### Dependencies


### Test with debug

```
python code_loader.py
```


### Test without debug

```
python -O code_loader.py
```


### Run

```
import CodeLoader
func_source = CodeLoader.load(func)
```


### Clean

```
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```

