# AI Filesystem

Local semantic search. Stupidly simple.

```
pip install aifs
```

```
from aifs import search

search("How does AI Filesystem work?", path="/path/to/folder")
search("It's not unlike how Spotlight works.") # If path is unset, defaults to current working directory
```
