"""Scoped pre-publication check for selected recruiter-facing source paths.

This is not a historical Git audit, a security certification or a substitute for
GitHub secret scanning, code review, dependency review or credential rotation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIRS = (
    "demo_safe/governed-rag",
    "demo_safe/governed-rag-model-lab",
    "portfolio_projects/renteria-tracelens",
    "portfolio_projects/renteria-continuity-router",
    "portfolio_projects/renteria-sourcegate",
    "hosted_demo/reliability",
)
PUBLIC_FILES = (
    "hosted_demo/index.html",
    "hosted_demo/rag-demo.js",
    "hosted_demo/app.js",
)
SOURCE_ENTRYPOINTS = (
    "demo_safe/governed-rag/demo.py",
    "portfolio_projects/renteria-tracelens/tracelens.py",
    "portfolio_projects/renteria-tracelens/test_tracelens.py",
    "portfolio_projects/renteria-continuity-router/continuity_router.py",
    "portfolio_projects/renteria-continuity-router/test_router.py",
    "portfolio_projects/renteria-sourcegate/sourcegate.py",
    "portfolio_projects/renteria-sourcegate/test_sourcegate.py",
)
EXTENSIONS = {".py", ".js", ".json", ".md", ".html", ".toml", ".txt", ".yml", ".yaml"}
MAX_TEXT_BYTES = 1_000_000

CREDENTIAL_SIGNATURES = (
    ("PEM private key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub access token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Slack access token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{15,}\b")),
    ("OpenAI-style API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b")),
    ("Literal bearer credential", re.compile(r"(?i)\bauthorization\s*[:=]\s*['\"]Bearer\s+[A-Za-z0-9_.-]{20,}['\"]")),
)

def iter_targets():
    for rel in PUBLIC_DIRS:
        directory = ROOT / rel
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing public directory: {rel}")
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in EXTENSIONS:
                yield path
    for rel in PUBLIC_FILES:
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"Missing public file: {rel}")
        yield path

def main() -> int:
    findings: list[str] = []
    checked = 0
    try:
        for rel in SOURCE_ENTRYPOINTS:
            if not (ROOT / rel).is_file():
                findings.append(f"missing source entrypoint: {rel}")
        for path in sorted(set(iter_targets())):
            rel = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                findings.append(f"symlink requires manual review: {rel}")
                continue
            if path.stat().st_size > MAX_TEXT_BYTES:
                findings.append(f"oversized text requires manual review: {rel}")
                continue
            if path.name == ".env" or (path.name.startswith(".env.") and not path.name.endswith(".example")):
                findings.append(f"environment settings not allowed in public scope: {rel}")
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                findings.append(f"non-UTF8 source requires manual review: {rel}")
                continue
            checked += 1
            for title, pattern in CREDENTIAL_SIGNATURES:
                for hit in pattern.finditer(content):
                    line = content.count("\n", 0, hit.start()) + 1
                    findings.append(f"possible {title}: {rel}:{line}")
        site = (ROOT / "hosted_demo/index.html").read_text(encoding="utf-8")
        for anchor in ("governed-rag", "polyglot-relay", "context-atlas", "monetary-simulator"):
            if f'id="{anchor}"' not in site:
                findings.append(f"missing demo target anchor: {anchor}")
        reliability = (ROOT / "hosted_demo/reliability/index.html").read_text(encoding="utf-8")
        for anchor in ("tracelens", "continuity-router", "sourcegate"):
            if f'href="#{anchor}"' not in reliability:
                findings.append(f"missing reliability anchor: {anchor}")
    except (FileNotFoundError, OSError) as exc:
        findings.append(str(exc))
    if findings:
        print("Public source check: REVIEW REQUIRED", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print(f"Public source check: PASS ({checked} scoped text files, 7 entrypoints, 7 demo links)")
    print("Scope only: historical secrets, dependencies, private content and live security require separate review.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
