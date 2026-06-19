from __future__ import annotations

from src.core.logging import configure_logging
from src.rag.ingestion import IngestionEngine


def main() -> int:
    configure_logging()
    engine = IngestionEngine()
    summary = engine.ingest_profile_jsons()
    count = engine.count(engine.collection_b)
    print(f"Collection B documents seen: {summary.documents_seen}")
    print(f"Collection B chunks ingested: {summary.chunks_ingested}")
    print(f"Collection B vector count: {count}")
    if count < summary.chunks_ingested:
        print("FAILED: vector count is lower than ingested chunks")
        return 1
    print("Phase 2 verification complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

