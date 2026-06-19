from __future__ import annotations

from src.cli.main import doctor, ingest_profile


def main() -> int:
    doctor()
    ingest_profile()
    print("Phase 9 CLI smoke verification complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

