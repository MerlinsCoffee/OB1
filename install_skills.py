"""
Install OB1 skills into ~/.claude/skills/ so they're available in every Claude Code session.
Copies folders — does not remove them from the OB1 repo.

Claude Code expects skills in folder form: ~/.claude/skills/<name>/SKILL.md
Flat <name>.md files are not registered as callable skills.
"""

import shutil
from pathlib import Path

OB1_ROOT = Path(__file__).parent
SKILLS_DIR = Path.home() / ".claude" / "skills"

# (source folder relative to OB1_ROOT, destination folder name in ~/.claude/skills/)
SKILLS = [
    ("skills/claudeception",         "claudeception"),
    ("recipes/live-retrieval",        "live-retrieval"),
    ("skills/panning-for-gold",      "panning-for-gold"),
    ("skills/meeting-synthesis",      "meeting-synthesis"),
    ("skills/competitive-analysis",   "competitive-analysis"),
    ("skills/deal-memo-drafting",     "deal-memo-drafting"),
    ("skills/financial-model-review", "financial-model-review"),
    ("skills/research-synthesis",     "research-synthesis"),
]

SKILLS_DIR.mkdir(parents=True, exist_ok=True)

installed = []
skipped = []
cleaned_flat = []

for src_rel, dest_name in SKILLS:
    src = OB1_ROOT / src_rel
    dest = SKILLS_DIR / dest_name
    legacy_flat = SKILLS_DIR / f"{dest_name}.md"

    if not src.exists():
        print(f"  MISSING  {src_rel}")
        skipped.append(dest_name)
        continue

    # Source must contain a skill manifest. Two naming conventions in OB1:
    #   skills/*       — SKILL.md
    #   recipes/*      — <name>.skill.md
    # Claude Code only recognizes SKILL.md, so normalize on copy.
    skill_md = src / "SKILL.md"
    recipe_md = next(src.glob("*.skill.md"), None)
    if not skill_md.exists() and recipe_md is None:
        print(f"  NO SKILL.md  {src_rel}")
        skipped.append(dest_name)
        continue

    # Remove any legacy flat .md installed by the old version of this script
    if legacy_flat.is_file():
        legacy_flat.unlink()
        cleaned_flat.append(legacy_flat.name)

    if dest.exists():
        shutil.rmtree(dest)
        action = "updated"
    else:
        action = "installed"

    shutil.copytree(src, dest)

    # Normalize recipe manifests to SKILL.md so Claude Code picks them up
    if not (dest / "SKILL.md").exists():
        copied_recipe = next(dest.glob("*.skill.md"), None)
        if copied_recipe is not None:
            copied_recipe.rename(dest / "SKILL.md")

    print(f"  {action:10s} {dest_name}/  <-  {src_rel}/")
    installed.append(dest_name)

print()
print(f"Done. {len(installed)} installed/updated, {len(skipped)} skipped.")
print(f"Skills directory: {SKILLS_DIR}")
if cleaned_flat:
    print(f"Removed legacy flat files: {', '.join(cleaned_flat)}")
if skipped:
    print(f"Skipped (source not found or missing SKILL.md): {', '.join(skipped)}")
print()
print("Restart Claude Code for newly installed skills to appear in the skills list.")
