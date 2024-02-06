# AI Filesystem

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1QdXPchTDnzW6I_3HTZFpSeak_XoH81v5?usp=sharing)

Local semantic search over folders. Why didn't this exist?


## Installation

```shell
pip install aifs
```

## CLI Usage

Display help section
```shell
aifs
```
```
Usage: aifs COMMAND

Local semantic search. Stupidly simple.

╭─ Commands ─────────────────────────────────────────────╮
│ embedder  Default embedder.                            │
│ index     Index a file or directory.                   │
│ search    Perform semantic search in a directory.      │
╰────────────────────────────────────────────────────────╯
╭─ Parameters ───────────────────────────────────────────╮
│ help,-h  Display this message and exit.                │
│ version  Display application version.                  │
╰────────────────────────────────────────────────────────╯
```

`index` command
```shell
aifs index help
```
```
Usage: aifs index [ARGS]

Index a file or directory.

╭─ Arguments ───────────────────────────────────────╮
│ *  PATH  Path to file or directory. [required]    │
╰───────────────────────────────────────────────────╯
```

- Indexing a file.
  ```shell
  aifs index ./Cyber.pdf
  ```
  ![aifs-index-file-GIF](https://github.com/synacktraa/synacktraa/assets/91981716/0b57f51c-c4e0-43c3-b0eb-72e8fc220927)

- Indexing a directory.
  ```shell
  aifs index ./test_docs
  ```
  ![aifs-directory-index-GIF](https://github.com/synacktraa/synacktraa/assets/91981716/33cb88c5-b602-4281-b42b-d005d87172d2)

`search` command
```shell
aifs search help
```
```
Usage: aifs search [ARGS] [OPTIONS]

Perform semantic search in a directory.

╭─ Arguments ───────────────────────────────────────────────────────────╮
│ DIR  Start search directory path. [default: /home/dev]                │
╰───────────────────────────────────────────────────────────────────────╯
╭─ Parameters ──────────────────────────────────────────────────────────╮
│ *  --query        -q  Search query string. [required]                 │
│    --max-results  -k  Maximum result count. [default: 5]              │
│    --threshold    -t  Minimum filtering threshold value.              │
│    --return       -r  Component to return. [choices: path,context]    │
╰───────────────────────────────────────────────────────────────────────╯
```

- Search in current directory
  ```shell
  aifs search --query "How does AI File System work?"
  ```

- Search in specific directory
  ```shell
  aifs search path/to/directory --query "How does AI File System work?"
  ```

- Get specific amount of results
  ```shell
  aifs search -q "How does AI File System work?" -k 8
  ```

- Control threshold value for better results
  ```shell
  aifs search -q "How does AI File System work?" -t 8.5
  ```

- Get specific component of results `[default: path mapped contexts JsON]`
  ```shell
  aifs search -q "How does AI File System work?" -r path
  ```

`embedder` command

```shell
aifs embedder help
```
```
Usage: aifs embedder [OPTIONS]

Default embedder.

╭─ Parameters ──────────────────────────────────────╮
│ --select  Select from available embedders.        │
╰───────────────────────────────────────────────────╯
```

- Display default embedder
  ```shell
  aifs embedder
  ```
  ```
  {
    "model": "BAAI/bge-small-en-v1.5",
    "dim": 384,
    "description": "Fast and Default English model",
    "size_in_GB": 0.13
  }
  ```
- Select from available embedders
  ```shell
  aifs embedder --select
  ```
  ![aifs-embedder-select](https://github.com/synacktraa/synacktraa/assets/91981716/7b0ed735-57cd-4986-80ab-04e2bdb0e758)


## Library Usage

#### Initialize `AIFileSystem`

```python
from aifs import AIFileSystem
aifs = AIFileSystem()
```

> By default it uses default embedder. You can specify a different `Embedder` instance too.

```python
from aifs.embedder import Embedder
aifs = AIFileSystem(
  embedder=Embedder(model="<model-name>", dim=<model-dimension>)
)
```
> Use `Embedder.available_models` to list supported models.

#### `index` method

- Indexing a file
  ```python
  from aifs.indexables import File
  aifs.index(File(__file__))
  ```

- Indexing a directory
  ```python
  from aifs.indexables import Directory
  aifs.index(Directory('path/to/directory'))
  ```

#### `is_indexed` method

> Verify If a `File` or `Directory` has been indexed.
```python
file = File(__file__)
aifs.is_indexed(file)
aifs.is_indexed(file.directory)
```

#### `search` method

- Search in current directory
  ```python
  aifs.search(query="How does AI File System work?")
  ```

- Search in specific directory
  ```python
  aifs.search(
    directory=Directory('path/to/directory'),
    query="How does AI File System work?"
  )
  ```

- Get specific amount of results
  ```python
  aifs.search(query="How does AI File System work?", max_results=8)
  ```

- Control threshold value for better results
  ```python
  aifs.search(
    query="How does AI File System work?", score_threshold=8.5
  )
  ```

# How It Works?

The `AIFileSystem` is a sophisticated file system management tool designed for organizing and searching through files and directories based on their content. It utilizes embeddings to represent file contents, allowing for semantic search capabilities. Here's a breakdown of its core components and functionalities:

### Core Components

#### `Metadata` and `Index`
- **Metadata**: A structured representation that includes file contexts (chunks of text extracted from files), the directory path, filepath, and the last modified timestamp.
- **Index**: Consists of embeddings (vector representations of file contents) and associated metadata.

#### `AIFileSystem` Class
The `AIFileSystem` class is the heart of the system, integrating various components to facilitate file indexing, searching, and management.

### Initialization

Upon initialization, the `AIFileSystem` prepares the environment for indexing and searching files and directories with the following steps:

- **Embedder Setup**: An embedder is initialized to generate vector embeddings from file content. If a custom embedder is not provided, the system defaults to a pre-configured option suitable for general-purpose text embedding.

- **Local Storage Initialization**: The system sets up a local storage mechanism to cache the embeddings and metadata. This involves:
  - Determining the storage path based on the embedder's name, ensuring a unique cache directory for different embedders.
  - Creating a mapping file (`map.json`) within the cache directory to maintain a record of collection names associated with base paths.

- **Base Path Handling**: The AIFileSystem intelligently handles base paths to accommodate the file system structure of different operating systems. 
  - **Windows Systems**: On Windows, base paths are recognized as drive letters (e.g., `C:`, `D:`). This allows the system to manage files and directories across different drives distinctly.
  - **POSIX Systems**: For POSIX-compliant systems (like Linux and macOS), base paths are identified as root directories (e.g., `/var`, `/home`). This approach facilitates indexing and searching files in a structured manner consistent with UNIX-like directory hierarchies.

- **Collection Management**: Utilizes a local persistent vector database, managed through the `qdrant_client`, to store and retrieve embeddings and metadata.

### Indexing Files and Directories
- **File Indexing**: Generates an index for a single file by extracting text, partitioning it into manageable chunks, and converting these chunks into embeddings. Metadata is also generated to include the file's contextual information and modification timestamp.
- **Directory Indexing**: Recursively indexes all files within a directory. It checks for modifications to ensure the index is current, adds new files, and removes entries for deleted files.

### Searching
Allows for semantic search within specified directories or globally across all indexed files. Searches are performed using query embeddings to find the most relevant files based on their content embeddings.

### Workflow
1. **Generate Index**: When a file or directory is indexed, the system extracts text, generates embeddings, and stores this information along with metadata in a dedicated collection.
2. **Search**: Input a text query to search across indexed files and directories. The system converts the query into an embedding and retrieves the most relevant files based on cosine similarity.
3. **Management**: The system supports adding, updating, and deleting files or directories in the index to keep the database current with the filesystem.


# Goals

- We should always have SOTA parsing and chunking. The logic for this should be swapped out as new methods arise.
  - Chunking should be semantic — as in, `python` and `markdown` files should have _different_ chunking algorithms based on the expected content of those filetypes. Who has this solution?
  - For parsing, I think Unstructured is the best of the best. Is this true?
- This project should stay **minimally scoped** — we want `aifs` to be the best local semantic search in the universe.

# Why?

We built this to let [`open-interpreter`](https://openinterpreter.com/) quickly semantically search files/folders.