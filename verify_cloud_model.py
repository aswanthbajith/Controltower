"""Verify the cloud model provider end-to-end against recorded fixtures.

This verifier runs in fixture mode by default — no live cloud calls are
made. The fixture responses are loaded from
``tests/fixtures/cloud_responses/`` and validated against the same
Pydantic contracts used by the live pipeline.

To run against a real cloud (Google Gemini) export:

    CLOUD_PROVIDER=google
    CLOUD_API_BASE=https://generativelanguage.googleapis.com
    CLOUD_MODEL=gemini-2.5-flash
    GEMINI_API_KEY=<your-key>

…and re-run this script.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from src.agents.alignment_engine import AlignmentEngine
from src.agents.application_writer import ApplicationWriter
from src.agents.proposal_generator import ProposalGenerator
from src.agents.research_discovery import ResearchDiscoveryAgent
from src.core.logging import configure_logging
from src.core.model_provider import GenerationRequest, get_model_provider
from src.database.models import (
    ApplicationDocuments,
    AlignmentScore,
    DualRetrievalEvidence,
    EvidenceChunk,
    ThesisProposal,
)
from src.database.sqlite_client import TrackerDBClient
from src.rag.ingestion import IngestionEngine


FIXTURE_DIR = Path("tests/fixtures/cloud_responses")


def _sample_evidence() -> DualRetrievalEvidence:
    return DualRetrievalEvidence(
        company_name="MTU Aero Engines",
        focus_area="Digital Twins and Process Optimization",
        company_evidence=[
            EvidenceChunk(
                collection="company_research",
                content=(
                    "MTU evidence describes digital manufacturing and MRO innovation with "
                    "aerospace production relevance, including automation of turbine disk "
                    "manufacturing, AI-driven process control, and predictive maintenance."
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
                    "large-scale technical analysis. The candidate has hands-on experience "
                    "with thermal modelling, parallel numerical kernels, and Python-based "
                    "simulation infrastructure."
                ),
                source="simulation_30000_entities.json",
                metadata={"document_type": "Project"},
            )
        ],
        status="Success",
    )


def _check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    line = f"[{status}] {label}"
    if detail:
        line += f" — {detail}"
    print(line, flush=True)
    return condition


def main() -> int:
    configure_logging()

    started = time.time()
    provider = get_model_provider(fixture_dir=FIXTURE_DIR)
    print(f"Provider in use: {provider.name}", flush=True)

    failures: list[str] = []

    # 1. JSON generation
    try:
        result = provider.generate_json(
            GenerationRequest(
                system="Return only valid JSON for testing.",
                prompt="Return a JSON object with fields a, b, c.",
                temperature=0.0,
                max_output_tokens=64,
            )
        )
        if not _check("JSON generation returns a parsed object", result.parsed is not None):
            failures.append("json-generation")
    except Exception as exc:
        failures.append("json-generation")
        _check("JSON generation", False, str(exc))

    # 2. Alignment scoring
    try:
        evidence = _sample_evidence()
        engine = AlignmentEngine(provider=provider)
        t0 = time.time()
        score = engine.evaluate_opportunity(evidence)
        elapsed = time.time() - t0
        if not _check(
            "Alignment scoring returns AlignmentScore",
            isinstance(score, AlignmentScore),
            f"overall={score.overall_score:.2f}, status={score.status.value}, t={elapsed:.2f}s",
        ):
            failures.append("alignment")
    except Exception as exc:
        failures.append("alignment")
        _check("Alignment scoring", False, str(exc))

    # 3. Thesis proposal
    try:
        generator = ProposalGenerator(provider=provider)
        t0 = time.time()
        proposal = generator.generate_thesis_concept(evidence)
        elapsed = time.time() - t0
        if not _check(
            "Thesis proposal generation returns ThesisProposal",
            isinstance(proposal, ThesisProposal),
            f"title={proposal.title!r}, t={elapsed:.2f}s",
        ):
            failures.append("proposal")
    except Exception as exc:
        failures.append("proposal")
        _check("Thesis proposal generation", False, str(exc))

    # 4. Application documents (cover + motivation + outreach)
    try:
        writer = ApplicationWriter(provider=provider)
        t0 = time.time()
        documents = writer.generate_documents(evidence, proposal)
        elapsed = time.time() - t0
        if not _check(
            "Application writer returns ApplicationDocuments",
            isinstance(documents, ApplicationDocuments),
            f"outreach_words={len(documents.outreach_email.split())}, t={elapsed:.2f}s",
        ):
            failures.append("writer")
    except Exception as exc:
        failures.append("writer")
        _check("Application writer", False, str(exc))

    # 5. Health check
    health = provider.health_check()
    if not _check("Provider health check reports status", "ok" in health, json.dumps(health)):
        failures.append("health")

    # 6. Cost estimate
    try:
        estimate = provider.estimate_cost(
            GenerationRequest(system="s", prompt="hello world", max_output_tokens=256)
        )
        if not _check(
            "Cost estimate returns CostEstimate",
            hasattr(estimate, "total"),
            f"total={estimate.total:.6f}",
        ):
            failures.append("cost")
    except Exception as exc:
        failures.append("cost")
        _check("Cost estimate", False, str(exc))

    # 7. Research Discovery Mode smoke (full pipeline) — uses real retrieval.
    try:
        # Make sure collections are populated. ingest_profile is idempotent.
        IngestionEngine().ingest_profile_jsons()
        agent = ResearchDiscoveryAgent(provider=provider)
        # We may not have live web access here; skip ingest_url path.
        result = agent.discover(
            company="MTU Aero Engines",
            url=None,
            focus_area="Digital Twins and Process Optimization",
            ingest_url=False,
        )
        if not _check(
            "Research Discovery Mode produces a result",
            result.opportunity_id.startswith("rd_"),
            f"opportunity_id={result.opportunity_id}, score={result.score}",
        ):
            failures.append("research-discovery")
    except Exception as exc:
        failures.append("research-discovery")
        _check("Research Discovery Mode", False, str(exc))

    # 8. Persistence — research_opportunities row written.
    try:
        db = TrackerDBClient()
        count = db.count_research_opportunities()
        if not _check("research_opportunities table populated", count >= 1, f"count={count}"):
            failures.append("persistence")
    except Exception as exc:
        failures.append("persistence")
        _check("research_opportunities persistence", False, str(exc))

    elapsed_total = time.time() - started
    print(f"\nTotal wall-clock: {elapsed_total:.2f}s")
    if failures:
        print(f"FAILED checks: {failures}")
        return 1
    print("All cloud-model checks PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())