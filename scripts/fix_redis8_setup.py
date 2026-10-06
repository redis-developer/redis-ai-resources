#!/usr/bin/env python3
"""Migrate notebook/markdown setup cells from redis-stack-server to Redis 8 (redis-server).

Why: Colab moved to Ubuntu 24.04 (noble); packages.redis.io has no redis-stack-server
for noble, so the apt install cell fails. Redis 8's `redis-server` package IS on noble
and bundles the query engine + JSON, so we switch to it and keep $(lsb_release -cs).

Start line: the Redis 8 deb ships the modules as .so files and loads them via the
`loadmodule` lines in /etc/redis/redis.conf. A bare `redis-server --daemonize yes`
ignores that file and starts with only the built-in vectorset module, so FT.* / JSON.*
are "unknown command". Colab has no systemd to start the packaged service for us, so
the notebook must pass the conf explicitly (sudo: the conf is root:redis 0640).

Raw-text replace: every pattern below is plain ASCII with no JSON-special chars, so a
literal string replace on the file bytes stays valid JSON AND produces a minimal diff
(reserializing the JSON reformats notebooks saved with other conventions). Only these
exact command/image strings are rewritten; unrelated text left in recorded cell outputs
(e.g. "Starting redis-stack-server..." log lines) is NOT touched and simply refreshes
when the notebook is re-run. `-y` keeps the apt install non-interactive so it can't stall
on a confirmation prompt in a headless Colab shell. Idempotent.
"""
import json
import sys
from pathlib import Path

# Ordered: longer/specific patterns first so a bare "redis-stack-server" left in prose
# is never half-clobbered.
REPLACEMENTS = [
    ("redis/redis-stack-server:latest", "redis:8"),
    ("--name redis-stack-server", "--name redis"),
    ("apt-get install redis-stack-server", "apt-get install -y redis-server"),
    ("redis-stack-server --daemonize yes", "redis-server --daemonize yes"),
    # bare start -> start with the packaged conf so the modules load (not a substring of
    # its own output, so re-running stays idempotent)
    ("redis-server --daemonize yes", "sudo redis-server /etc/redis/redis.conf --daemonize yes"),
]

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"src", ".git", "node_modules"}  # skip vendored redisvl checkout under src/


def apply(text: str) -> tuple[str, int]:
    n = 0
    for old, new in REPLACEMENTS:
        c = text.count(old)
        if c:
            text = text.replace(old, new)
            n += c
    return text, n


def fix_file(path: Path) -> int:
    text = path.read_text()
    new, n = apply(text)
    if n:
        if path.suffix == ".ipynb":
            json.loads(new)  # guard: replacement must keep the notebook valid JSON
        path.write_text(new)
    return n


def main() -> None:
    grand = 0
    targets = []
    for base in ("python-recipes", "java-recipes"):
        d = ROOT / base
        if d.exists():
            targets += [p for p in d.rglob("*.ipynb") if not (SKIP_DIRS & set(p.parts))]
            targets += [p for p in d.rglob("*.md") if not (SKIP_DIRS & set(p.parts))]
    targets.append(ROOT / "README.md")

    for p in sorted(set(targets)):
        if not p.exists():
            continue
        n = fix_file(p)
        if n:
            grand += n
            print(f"  {n:3d}  {p.relative_to(ROOT)}")
    print(f"\nTotal replacements: {grand}")

    # self-check: no runnable setup reference to the old package should remain in SOURCE
    leftover = 0
    for p in sorted(set(targets)):
        if not p.exists():
            continue
        if p.suffix == ".ipynb":
            nb = json.loads(p.read_text())
            body = "".join("".join(c.get("source", [])) for c in nb.get("cells", []))
        else:
            body = p.read_text()
        for pat in ("install redis-stack-server", "redis-stack-server --daemonize",
                    "redis/redis-stack-server:latest", "redis-server --daemonize yes"):
            if pat in body:
                print(f"LEFTOVER {pat!r} in {p.relative_to(ROOT)}", file=sys.stderr)
                leftover += 1
    assert leftover == 0, f"{leftover} runnable redis-stack-server refs remain"
    print("self-check: no runnable redis-stack-server setup refs remain ✓")


if __name__ == "__main__":
    main()
