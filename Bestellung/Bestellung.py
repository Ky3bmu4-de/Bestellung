from __future__ import annotations

# Backward-compatible entrypoint that runs the refactored app
try:
    from .app import main as _run
except ImportError:
    from app import main as _run  # type: ignore


if __name__ == "__main__":
    _run()
