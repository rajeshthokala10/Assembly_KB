"""Initialize the Qdrant collection with the required schema and indices."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.vectorstore.qdrant_store import QdrantStore


def main() -> None:
    store = QdrantStore()
    store.ensure_collection()
    print(f"Collection '{store.collection}' is ready.")


if __name__ == "__main__":
    main()
