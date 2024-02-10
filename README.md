# AI Filesystem

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1QdXPchTDnzW6I_3HTZFpSeak_XoH81v5?usp=sharing)

Local semantic search over folders. Why didn't this exist?

```shell
pip install aifs
pip install unstructured[all-docs] # If you want to parse all doc types. Includes large packages!
```

```python
from aifs import search

search("How does AI Filesystem work?", path="/path/to/folder")
search("It's not unlike how Spotlight works.") # Path defaults to CWD
```

# How it works

<br>

![aifs](https://github.com/KillianLucas/aifs/assets/63927363/c61599a9-aad8-483d-b6a4-3671629cd5f4)

Running `aifs.search` will chunk and embed all nested supported files (`.txt`, `.py`, `.sh`, `.docx`, `.pptx`, `.jpg`, `.png`, `.eml`, `.html`, and `.pdf`) in `path`. It will then store these embeddings into an `_.aifs` file in `path`.

By storing the index, you only have to chunk/embed once. This makes semantic search **very** fast after the first time you search a path.

If a file has changed or been added, `aifs.search` will update or add those chunks. We still need to handle file deletions (we welcome PRs).

### In detail:

1. If a folder hasn't been indexed, we first use [`unstructured`](https://github.com/Unstructured-IO/unstructured/tree/main) to parse and chunk every file in the `path`.
2. Then we use [`chroma`](https://github.com/chroma-core/chroma) to embed the chunks locally and save them to a `_.aifs` file in `path`.
3. Finally, `chroma` is used again to semantically search the embeddings.

If an `_.aifs` file _is_ found in a directory, it uses that instead of indexing it again. If some files have been updated, it will re-index those.

# Goals

- We should always have SOTA parsing and chunking. The logic for this should be swapped out as new methods arise.
  - Chunking should be semantic — as in, `python` and `markdown` files should have _different_ chunking algorithms based on the expected content of those filetypes. Who has this solution?
  - For parsing, I think Unstructured is the best of the best. Is this true?
- We should always have SOTA embedding. If a better local embedding model is found, we should automatically download and use it.
  - I think Chroma will always do this (is this true?) so we depend on Chroma.
- This project should stay **minimally scoped** — we want `aifs` to be the best local semantic search in the universe.

# Why?

We built this to let [`open-interpreter`](https://openinterpreter.com/) quickly semantically search files/folders.
