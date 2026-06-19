from __future__ import annotations

from src.core.logging import configure_logging
from src.rag.ingestion import IngestionEngine


TARGETS = [
    {
        "url": "https://www.mtu.de/innovation/manufacturing-and-mro-of-the-future/",
        "company": "MTU Aero Engines",
        "category": "Aviation R&D and Process Optimization",
    },
    {
        "url": "https://www.freudenberg.com/en/technologies/innovation-insights",
        "company": "Freudenberg",
        "category": "Manufacturing Innovation and Physical Systems",
    },
]


def main() -> int:
    configure_logging()
    engine = IngestionEngine()
    summaries = []
    for target in TARGETS:
        summaries.append(
            engine.ingest_company_url(
                url=target["url"],
                company=target["company"],
                category=target["category"],
            )
        )
    total = engine.count(engine.collection_a)
    print(f"Collection A vector count: {total}")
    print(f"Sources ingested: {sum(summary.documents_seen for summary in summaries)}")
    return 0 if total > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
