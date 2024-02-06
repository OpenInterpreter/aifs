from typing import cast, TypeAlias, Sequence

from fastembed.embedding import FlagEmbedding

from .settings import DEFAULT_EMBEDDER


Embedding: TypeAlias = Sequence[float] | Sequence[int]
"""Embedding Type."""

class Embedder:
    """Class to create an embedder instance."""

    available_models = FlagEmbedding.list_supported_models()
    """Available Models."""

    def __init__(self, model: str, dim: int, **kwargs) -> None:
        self.name = model
        self.dimensions = dim
        self._instance = FlagEmbedding(model_name=model)
        self._repr_kwargs = {
            'name': model, 
            'dimensions': dim, 
            'description': kwargs.pop('description', None),
            'size_in_GB': kwargs.pop('size_in_GB', "??")
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self._repr_kwargs.items())})"

    @classmethod
    def default(cls):
        return cls(**DEFAULT_EMBEDDER)
    
    def embed(self, inputs: list[str]):
        """Embeds list of contexts."""
        return list(cast(Embedding, vector.tolist())
            for vector in self._instance.passage_embed(
                inputs, batch_size=32, parallel=None)
        )