from __future__ import annotations

from src.agents.proposal_generator import ProposalGenerator
from src.core.logging import configure_logging
from src.rag.dual_retrieval import DualRetrievalEngine


def main() -> int:
    configure_logging()
    evidence = DualRetrievalEngine().get_alignment_evidence(
        company_name="MTU Aero Engines",
        focus_area="Digital Twins and Process Optimization",
    )
    proposal = ProposalGenerator().generate_thesis_concept(evidence)
    print(proposal.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

