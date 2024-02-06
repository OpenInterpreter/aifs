import json
from uuid import uuid4
from typing import Optional, Literal
from typing_extensions import TypedDict

from qdrant_client.http.models import (
    Batch, Filter, FieldCondition, MatchValue)
from qdrant_client.local.local_collection import LocalCollection

from . import settings
from .indexables import File, Directory, is_indexable
from .embedder import Embedder, Embedding


class Metadata(TypedDict):
    """Dictionary representing metadata component of Index."""
    contexts: list[str]
    directory: str
    filepath: str
    last_modified: float

class Index(TypedDict):
    """Dictionary representing index"""
    embeddings: list[Embedding]
    metadata: Metadata

class AIFileSystem:
    
    """Initiate a File System instance."""
    def __init__(self, embedder: Optional[Embedder] = None) -> None:
        from qdrant_client.local.qdrant_local import QdrantLocal
        from qdrant_client.models import Distance, VectorParams

        self._embedder = embedder or Embedder.default()
        self._storage_path = settings.CACHE_DIR / self._embedder.name.replace('/', '--')
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._map_path = self._storage_path / 'map.json'
        self._map_path.touch()
        
        self._storage = QdrantLocal(location=str(self._storage_path))
        """Currently using local but we can switch to localhost client
        which provides async functionality."""
        self._new_index_params = VectorParams(
            size=self._embedder.dimensions, distance=Distance.COSINE)
        
        self._cache: dict[File | Directory, LocalCollection] = {}
        """I don't know if this is the best way to cache the collection or 
        that it's even necessary. In search method, collection_of is called 3 times 
        if the directory is not indexed. so I thought of storing it in a mapping."""
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({json.dumps(self.map, indent=4)})"
    
    @property
    def map(self) -> dict[str, str]:
        """Base path mapped collection name."""
        return json.loads(self._map_path.read_bytes() or '{}')

    def _build_filter(
        self, 
        type: Literal['should', 'must'],
        mapping: dict[Literal['directory', 'filepath'], list[str]]
    ):
        """Build filter for vectorstore operations."""
        conditions = []
        for key, values in mapping.items():
            conditions.extend([FieldCondition(
                key=key, match=MatchValue(value=value)
            ) for value in values])
        
        return Filter(**{type: conditions})

    def _read_metadatas(
        self, collection: LocalCollection, filter: Filter, limit: int = 1
    ) -> list[Metadata]:
        """Read metadatas for given filter."""
        return [r.payload for r in collection.scroll(filter, limit)[0] if r.payload]

    def generate_index(self, file: File) -> Index:
        """Generate index of a `File` instance."""
        from unstructured.partition.auto import partition
        from unstructured.chunking.title import chunk_by_title
        try:
            contexts = list(map(
                lambda x: x.text, chunk_by_title(
                    partition(filename=str(file)), 
                    max_characters=settings.MAX_CHARS_PER_CHUNK))
            )
            if len(contexts) > settings.MAX_CHUNKS:
                contexts = contexts[:settings.MAX_CHUNKS]
            if contexts == []:
                raise Exception("Failed to chunk.")
        except Exception:
            contexts = [f"There is a file at `{str(file)}`."]

        return {
            'embeddings': self._embedder.embed(contexts),
            'metadata': {
                "contexts": contexts,
                "directory": str(file.directory),
                "filepath": str(file),
                "last_modified": file.last_modified
            }}
    
    def __ingest_file(self, file: File, collection: LocalCollection):
        index = self.generate_index(file)
        ctx_len = len(index['metadata']["contexts"])
        _ = collection.upsert(points=Batch(
            ids=[str(uuid4())] * ctx_len,
            vectors=index["embeddings"],
            payloads=[index["metadata"]] * ctx_len)
        )
    
    def collection_of(self, __indexable: File | Directory) -> LocalCollection:
        """Get collection of a `File` or `Directory`."""
        collection = self._cache.get(__indexable)
        if collection:
            return collection
        
        _map, base = self.map, __indexable.base
        collection_name = _map.get(base)
        if collection_name is None:
            collection_name = str(uuid4())
            _ = self._storage.create_collection(
                    collection_name=collection_name,
                    vectors_config=self._new_index_params)
            self._map_path.write_text(
                json.dumps(_map | {base: collection_name}))
        
        collection = self._storage._get_collection(collection_name)
        self._cache[__indexable] = collection
        return collection

    def is_indexed(self, __indexable: File | Directory) -> bool:
        """Check if a `File` or `Directory` has been indexed."""
        if isinstance(__indexable, File):
            mapping = {'filepath': [str(__indexable)]}
        else:
            mapping = {'directory': [str(__indexable)]}

        metadatas = self._read_metadatas(
            collection=self.collection_of(__indexable), 
            filter=self._build_filter(type='must', mapping=mapping))
        
        return True if metadatas else False

    def index(self, __indexable: File | Directory) -> None:
        """Index a `File` or `Directory`.

        - For a `Directory`, it recursively indexes all contained files that 
        are either not yet indexed or have been modified since the last indexing. 
        It also removes entries for files that have been deleted to ensure the index is up-to-date.

        - For a `File`, it checks if the file is already indexed by comparing its 
        metadata within the collection. If the file is not indexed or its last modification 
        time has changed, it is marked for indexing.

        """
        if not is_indexable(__indexable.path):
            raise ValueError(f'{str(__indexable)} cannot be indexed.')

        from rich.progress import Progress, SpinnerColumn

        collection = self.collection_of(__indexable)
        _ = self._cache.pop(__indexable, None)

        if isinstance(__indexable, File):
            metadatas = self._read_metadatas(
                collection=collection, filter=self._build_filter(
                    type='must', mapping={"filepath": [str(__indexable)]}
                ))
            if not metadatas or metadatas[0]["last_modified"] != __indexable.last_modified:
                with Progress(
                    SpinnerColumn('aesthetic'),  *Progress.get_default_columns()) as progress:
                    task = progress.add_task(f"[honeydew2]INDEXING({__indexable.name})", total=None)
                    self.__ingest_file(__indexable, collection)
                    progress.update(task, description=f"[honeydew2]INDEXED({__indexable.name})")
            return
        
        files: list[File] = []
        avaialble_files = __indexable.files
        metadatas = self._read_metadatas(
            collection=collection, filter=self._build_filter(
                type='should', mapping={
                    'directory': [str(d) for d in __indexable.subdirectories + [__indexable]]
                }), limit=len(avaialble_files)
        )

        indexed_files = {m['filepath']: m['last_modified'] for m in metadatas}
        for file in avaialble_files:
            l_mtime = indexed_files.pop(str(file), None)
            if not l_mtime or l_mtime != file.last_modified:
                files.append(file)
        
        collection.delete(selector=self._build_filter(
            type='should', mapping={'filepath': list(indexed_files.keys())})
        )
        
        with Progress(
            SpinnerColumn('aesthetic'),  *Progress.get_default_columns()) as progress:
            
            task = progress.add_task(f"[honeydew2]INDEXING({__indexable.name})", total=len(files))
            for f in files:
                self.__ingest_file(f, collection)
                progress.update(task, advance=1, description=f"[honeydew2]@({f.name})")
            progress.update(task, description=f"[honeydew2]INDEXED({__indexable.name})")

    def search(
        self, 
        query: str, 
        directory: Optional[Directory] = None, 
        max_results: int = 5,
        score_threshold: Optional[float] = None
    ) -> dict[str, list[str]] | None:
        """
        Search for indexes for a given query.
        @param query: The search query string to find matching indexes.
        @param directory: The directory object within which the search is to be performed. If None, current directory is used.
        @param max_results: The maximum number of search results to return. Defaults to 5.
        @param score_threshold: A minimum score threshold for search results. Results with scores below this threshold are excluded. If None, no threshold is applied.

        :returns: File path mapped context
        """
        dir = directory or Directory()
        if not is_indexable(dir.path):
            raise ValueError(f'{str(dir)} cannot be indexed.')

        if not self.is_indexed(dir):
            self.index(dir)

        points = self.collection_of(dir).search(
            query_vector=self._embedder.embed([query])[0],
            query_filter=self._build_filter(
                type='should', mapping={
                    'directory': [str(d) for d in dir.subdirectories + [dir]]
            }),
            limit=max_results, 
            score_threshold=score_threshold
        )
        if points:
            mapping = {}
            for point in points[:min(len(points), max_results)]:
                payload:Metadata = point.payload
                if not payload:
                    continue
                mapping[payload['filepath']] = payload['contexts']
            return mapping
        
    def rename(__indexable: File | Directory):
        """Rename File or Directory based on content. Will require llm integration."""
        raise NotImplementedError()