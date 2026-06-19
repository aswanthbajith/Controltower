from __future__ import annotations

from pathlib import Path

from src.database.profile_loader import validate_profile_directory


PROFILE_JSON_DIR = Path("data/profile_jsons")


def main() -> int:
    results = validate_profile_directory(PROFILE_JSON_DIR)
    failures = [result for result in results if not result.ok]

    for result in results:
        if result.ok:
            print(f"SUCCESS: {result.path.name} is aligned: {result.title}")
        else:
            print(f"FAILED: {result.path.name}")
            print(result.error)

    if failures:
        print(f"\nPhase 1 validation failed for {len(failures)} file(s).")
        return 1

    print(f"\nPhase 1 validation complete. Validated {len(results)} profile artifact(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

