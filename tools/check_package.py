#!/usr/bin/env python3
"""Dependency-free package checks and a limited public-content scan.

This does not replace manual privacy review or a full YAML parser.
"""

import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/ld-dot3dbuild-online"


def check():
    problems = []
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and not any(part in {".git", "__pycache__", ".venv"} for part in p.relative_to(ROOT).parts))
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    # The package intentionally uses this narrow YAML subset. Reject variations
    # rather than pretending that this implements general YAML parsing.
    front = re.match(r'\A---\nname: ([a-z0-9-]+)\ndescription: ("[^\n]+")\n---\n', content)
    if not front:
        problems.append("SKILL.md: unsupported or invalid package frontmatter")
    else:
        name, description = front.groups()
        version = re.search(r"版本：([0-9]+\.[0-9]+\.[0-9]+)", content).group(1)
        if name != SKILL.name or len(name) > 64:
            problems.append("SKILL.md: skill name does not match directory")
        description = json.loads(description)
        if not description.strip() or len(description) > 1024 or any(c in description for c in "<>"):
            problems.append("SKILL.md: invalid description")
        if f"## {version} " not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
            problems.append("CHANGELOG.md: current version missing")

    patterns = {
        "credential-like value": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{32,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"),
        "personal email": re.compile(r"\b[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "machine-specific path": re.compile(r"(?i)(?:[A-Z]:[\\/](?:Users|Agentic|app|work)[\\/]|/(?:Users|home)/[^/\s]+/)"),
        "private interface name": re.compile("mcp" + "__|functions" + r"\.exec|num_last_images" + "_to_include|referenced_image" + "_paths"),
    }
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix not in {".md", ".json", ".py", ".yaml", ".svg"} and path.name != ".gitignore":
            problems.append(f"{rel}: unexpected file type; review before publication")
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            if pattern.search(text):
                problems.append(f"{rel}: {label}")
        if path.suffix == ".py":
            ast.parse(text, filename=rel)
        if path.suffix == ".json":
            json.loads(text)
        if path.suffix == ".md":
            prose = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose):
                if re.match(r"^[a-z]+://|^#", target):
                    continue
                target = target.split("#", 1)[0]
                resolved = (path.parent / target).resolve()
                if not resolved.is_relative_to(ROOT) or not resolved.exists():
                    problems.append(f"{rel}: broken/out-of-repository relative link: {target}")

    manifest = json.loads((SKILL / "references/reference-manifest.template.json").read_text(encoding="utf-8"))
    ids = [r["id"] for r in manifest["references"]]
    if len(ids) != len(set(ids)) or manifest["current_primary"] not in ids:
        problems.append("Reference template: duplicate IDs or unknown current_primary")
    if manifest["skill_version"] != (version if front else None):
        problems.append("Reference template: skill version mismatch")
    for priorities in manifest["region_priority"].values():
        if not priorities or any(item not in ids for item in priorities):
            problems.append("Reference template: unknown region reference")
    if manifest["outputs"] or manifest["output_record_template"]["user_acceptance"]["status"] != "pending":
        problems.append("Reference template: should not contain real accepted outputs")
    if len(manifest["components"]) != len({c["id"] for c in manifest["components"]}):
        problems.append("Reference template: duplicate component IDs")
    return {"passed": not problems, "checked_files": len(files), "problems": problems,
            "scope": "narrow frontmatter, Python syntax, JSON, local links, limited privacy/secret patterns; manual review still required"}


if __name__ == "__main__":
    try:
        result = check()
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        sys.exit(0 if result["passed"] else 2)
    except (OSError, ValueError, SyntaxError, KeyError) as error:
        print(json.dumps({"passed": False, "error": str(error)}))
        sys.exit(2)
