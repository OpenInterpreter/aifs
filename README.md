# AI Filesystem

Local semantic search over folders. Why didn't this exist?

```shell
pip install aifs
```

```python
from aifs import search

search("How does AI Filesystem work?", path="/path/to/folder")
search("It's not unlike how Spotlight works.") # Path defaults to CWD
```

# How it works

<br>

![aifs](https://github.com/KillianLucas/aifs/assets/63927363/c61599a9-aad8-483d-b6a4-3671629cd5f4)

Running `aifs.search` will chunk and embed all nested supported files (`.txt`, `.docx`, `.pptx`, `.jpg`, `.png`, `.eml`, `.html`, and `.pdf`) in `path`. It will then store these embeddings into an `_.aifs` file in `path`.

By storing the index, you only have to chunk/embed once. This makes semantic search **very** fast after the first time you search a path.

If a file has changed or been added, `aifs.search` will update or add those chunks. We still need to handle file deletions (we welcome PRs).

### In detail:

1. If a folder hasn't been indexed, we first use [`unstructured`](https://github.com/Unstructured-IO/unstructured/tree/main) to parse and chunk every file in the `path`.
2. Then we use [`chroma`](https://github.com/chroma-core/chroma) to embed the chunks locally and save them to a `_.aifs` file in `path`.
3. Finally, `chroma` is used again to semantically search the embeddings.

If an `_.aifs` file _is_ found in a directory, it uses that instead of indexing it again. If some files have been updated, it will re-index those.

# Why?

We built this to let [`open-interpreter`](https://openinterpreter.com/) quickly semantically search files/folders.
