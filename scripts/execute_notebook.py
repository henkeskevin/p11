from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import sys
import time

import nbformat
from nbclient import NotebookClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def execute(source: Path, output: Path, timeout: int) -> float:
    runtime_dir = PROJECT_ROOT / ".tmp" / "jupyter-runtime"
    ipython_dir = PROJECT_ROOT / ".tmp" / "ipython"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    ipython_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("JUPYTER_RUNTIME_DIR", str(runtime_dir))
    os.environ.setdefault("IPYTHONDIR", str(ipython_dir))
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    notebook = nbformat.read(source, as_version=4)
    started = time.perf_counter()
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(PROJECT_ROOT)}},
        allow_errors=False,
        record_timing=True,
    )
    client.execute(cwd=str(PROJECT_ROOT))
    elapsed = time.perf_counter() - started
    output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, output)
    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Exécuter un notebook depuis un noyau propre.")
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=PROJECT_ROOT / "notebooks" / "BottleNeck_analyse_portfolio.ipynb",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    source = args.source.resolve()
    output = (args.output or source).resolve()
    elapsed = execute(source, output, args.timeout)
    print(f"Notebook exécuté sans erreur en {elapsed:.2f} s: {output}")


if __name__ == "__main__":
    main()
