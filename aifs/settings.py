import json
from pathlib import Path

FILES_TO_IGNORE = (".DS_Store", '.gitignore')
EXTENSIONS_TO_IGNORE = (".tar.gz", ".gz", ".whl")
DIRECTORIES_TO_IGNORE = ('.git', '__pycache__')

MAX_CHARS_PER_CHUNK = 500
MAX_CHUNKS = 300

CACHE_DIR = Path().home() / '.cache' / 'aifs'
"""AIFS cache directory."""
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_EMBEDDER_FILE = CACHE_DIR / 'default_embedder.json'
if not DEFAULT_EMBEDDER_FILE.exists():
    DEFAULT_EMBEDDER_FILE.write_text(json.dumps({
        "model": "BAAI/bge-small-en-v1.5",
        "dim": 384,
        "description": "Fast and Default English model",
        "size_in_GB": 0.13}))

DEFAULT_EMBEDDER = json.loads(DEFAULT_EMBEDDER_FILE.read_bytes())
