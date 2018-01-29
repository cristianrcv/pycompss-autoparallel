Code Replacer
=============================

Replaces the code of a given function by the new given code. It creates a new file containing the updated module (previous module with new function definition) and loads it.


### Dependencies


### Test with debug

```
python code_replacer.py
```


### Test without debug

```
python -O code_replacer.py
```


### Run

```
import CodeReplacer
func = <func instance>
new_code = <path_to_file_containing_new_code>
new_func = CodeReplacer.replace(func, new_code)
```


### Clean

```
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```

