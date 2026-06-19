from __future__ import annotations

import tempfile
from pathlib import Path

from src.agents.tracker_agent import TrackerAgent
from src.database.models import (
    AlignmentScore,
    ApplicationDocuments,
    DualRetrievalEvidence,
    EvidenceChunk,
    ThesisProposal,
)
from src.database.sqlite_client import TrackerDBClient
from src.ui import app
from src.ui.dashboard_data import DashboardRepository


def main() -> int:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        db = TrackerDBClient(db_path=Path(temp_dir) / "tracker.db")
        tracker = TrackerAgent(db)
        job_id = tracker.log_opportunity(
            company="MTU Aero Engines",
            title="Master Thesis Digital Twin Manufacturing",
            url="https://www.mtu.de/innovation/manufacturing-and-mro-of-the-future/",
            focus_area="Digital twins for aerospace manufacturing",
        )
        tracker.save_scores(
            job_id,
            AlignmentScore(
                research_alignment=80,
                technical_alignment=82,
                experience_alignment=76,
                thesis_potential=86,
                interview_probability=78,
                justification=(
                    "Evidence links aerospace manufacturing research with simulation, "
                    "optimization, and HPC-heavy candidate experience."
                ),
            ),
        )
        tracker.save_evidence(job_id, _sample_evidence())
        tracker.save_thesis_proposal(
            job_id,
            ThesisProposal(
                title="Digital Twin Optimization for Aerospace Manufacturing",
                abstract=(
                    "This thesis investigates how evidence-grounded simulation and AI workflows "
                    "can support aerospace manufacturing planning. It links company digital "
                    "manufacturing evidence with candidate experience in HPC simulation and "
                    "optimization. The work remains scoped to retrieved evidence and human review."
                ),
                methodology="Build a retrieval-grounded simulation analysis plan with HPC profiling.",
                business_value="Improve prioritization of technically aligned thesis opportunities.",
                novelty="Combine local RAG evidence with conservative proposal generation.",
            ),
        )
        tracker.save_application_documents(
            job_id,
            ApplicationDocuments(
                outreach_email="Hello, I am interested in discussing a grounded thesis direction.",
                cover_letter=(
                    "Dear team,\nThis application is based on retrieved evidence, local "
                    "retrieval, and a conservative human-review workflow for research fit."
                ),
                motivation_letter=(
                    "I am motivated by evidence-grounded aerospace research that connects "
                    "simulation, optimization, and reliable local AI support systems."
                ),
            ),
        )

        repository = DashboardRepository(db)
        opportunities = repository.list_opportunities()
        documents = repository.get_documents(job_id)
        evidence = repository.get_evidence(job_id)

        assert callable(app.main)
        assert len(opportunities) == 1
        assert opportunities[0].document_count == 4
        assert opportunities[0].evidence_count == 2
        assert len(documents) == 4
        assert len(evidence) == 2

    print("Phase 8 dashboard data and Streamlit entrypoint verification complete.")
    return 0


def _sample_evidence() -> DualRetrievalEvidence:
    return DualRetrievalEvidence(
        company_name="MTU Aero Engines",
        focus_area="Digital twins for aerospace manufacturing",
        company_evidence=[
            EvidenceChunk(
                collection="company_research",
                content=(
                    "MTU evidence describes digital manufacturing and MRO innovation with "
                    "aerospace production relevance."
                ),
                source="https://www.mtu.de/innovation/manufacturing-and-mro-of-the-future/",
                metadata={"company": "MTU Aero Engines"},
            )
        ],
        candidate_evidence=[
            EvidenceChunk(
                collection="candidate_profile",
                content=(
                    "Aswa profile evidence describes HPC simulation, optimization, and "
                    "large-scale technical analysis."
                ),
                source="simulation_30000_entities.json",
                metadata={"document_type": "Project"},
            )
        ],
        status="Success",
    )


if __name__ == "__main__":
    raise SystemExit(main())
