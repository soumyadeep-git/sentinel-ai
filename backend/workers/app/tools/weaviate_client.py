import os
from typing import Optional

try:
    import weaviate
except Exception:  # pragma: no cover
    weaviate = None  # type: ignore


class WeaviateClientFactory:
    @staticmethod
    def create() -> Optional["weaviate.Client"]:
        if weaviate is None:
            return None
        url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        return weaviate.Client(url)
