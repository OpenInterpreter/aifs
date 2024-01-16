# AI Filesystem

Local semantic search. Stupidly simple.

```shell
pip install aifs
```

```python
from aifs import search

search("How does AI Filesystem work?", path="/path/to/folder")
search("It's not unlike how Spotlight works.") # Path defaults to CWD
```
