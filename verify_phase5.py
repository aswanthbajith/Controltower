from __future__ import annotations

from src.agents.alignment_engine import AlignmentEngine
from src.core.logging import configure_logging
from src.rag.dual_retrieval import DualRetrievalEngine


def main() -> int:
    configure_logging()
    evidence = DualRetrievalEngine().get_alignment_evidence(
        company_name="MTU Aero Engines",
        focus_area="Digital Twins and Process Optimization",
    )
    score = AlignmentEngine().evaluate_opportunity(evidence)
    print(score.model_dump_json(indent=2))
    print(f"overall_score={score.overall_score:.2f} status={score.status.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

