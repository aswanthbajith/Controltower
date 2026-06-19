from __future__ import annotations

from src.core.logging import configure_logging
from src.rag.dual_retrieval import DualRetrievalEngine


def main() -> int:
    configure_logging()
    evidence = DualRetrievalEngine().get_alignment_evidence(
        company_name="MTU Aero Engines",
        focus_area="Digital Twins and Process Optimization",
    )
    print(evidence.model_dump_json(indent=2))
    return 0 if evidence.status == "Success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

