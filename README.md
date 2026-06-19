# CONTROLTOWER

CONTROLTOWER is a local-first AI platform for discovering and evaluating high-value Master's thesis, R&D collaboration, hidden research, and working-student opportunities for Aswa.

The system optimizes for research alignment, technical alignment, thesis potential, interview probability, and long-term career growth. It explicitly does not optimize for application volume, and it never auto-submits applications.

## Phase 1 Scope

This first implementation pass establishes the foundation:

- Pydantic data contracts for profile records and later alignment/document objects.
- Seed profile JSON files for Collection B.
- A deterministic validation loader.
- A root verification script.
- Unit tests for validation and scoring contracts.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## Verify Phase 1

```powershell
.\.venv\Scripts\python verify_phase1.py
.\.venv\Scripts\python -m pytest
```

## Notes

The active machine does not currently expose `git` on PATH. GitHub version-control setup remains blocked until Git is installed or a target GitHub repository is provided for connector-based file operations.

