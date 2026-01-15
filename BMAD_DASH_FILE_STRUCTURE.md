# BMAD Dash File Structure Requirements

**Last Updated:** 2026-01-15
**Purpose:** Document the required file structure for BMAD projects to work correctly with BMAD Dash

---

## Overview

BMAD Dash parses project artifacts using specific conventions. Projects **must** follow these file structure requirements for the dashboard to load and display story details correctly.

---

## Story File Requirements

### 1. Location

Story files **MUST** be located in:
```
{project-root}/_bmad-output/implementation-artifacts/
```

**Naming Pattern:**
```
{epic}-{story}-{slug}.md
```

**Examples:**
- `1-0-project-initialization-architecture-scaffold.md`
- `1-1-living-orb-overlay-core.md`
- `2-4-universal-export-engine.md`

**❌ INCORRECT Locations:**
- `_bmad-output/implementation-artifacts/stories/1-1-*.md` (subdirectory)
- `epics/epic-1/story-1-1.md` (wrong parent directory)
- `plans/story-1-1.md` (wrong parent directory)

---

### 2. File Format

Story files **MUST** be pure Markdown **WITHOUT** YAML frontmatter.

**✅ CORRECT Format:**
```markdown
# Story 1.1: Living Orb & Overlay Core

## User Story

As a User,
I want to open and edit my notes in a distraction-free environment,
So that I can refine my captured thoughts without opening a complex external app.

## Acceptance Criteria

**Given** I have searched for a note
**When** I click on a search result
**Then** The Integrated Editor should open in a floating window
**And** The content should be displayed in "Live Preview" mode
**And** Any edits I make should be auto-saved to disk (debounce < 1s)

## Implementation Tasks

- [ ] Create Editor component with markdown support
- [ ] Implement Live Preview mode (render markdown, hide syntax)
- [ ] Create floating editor window
- [ ] Add auto-save with debounce (< 1s)
```

**❌ INCORRECT Format (with YAML frontmatter):**
```markdown
---
id: "1.1"
title: "Living Orb & Overlay Core"
epic: "1"
status: "ready-for-dev"
---

# Story 1.1: Living Orb & Overlay Core
...
```

**Why?** The BMAD Dash backend parser expects pure markdown and gets all metadata from `sprint-status.yaml`, NOT from story files.

---

### 3. Metadata Source

All story metadata (ID, title, status, epic) comes from:
```
{project-root}/_bmad-output/implementation-artifacts/sprint-status.yaml
```

**Example sprint-status.yaml structure:**
```yaml
development_status:
  # Epic 1
  epic-1: in-progress

  # Stories
  1-0-project-initialization-architecture-scaffold: done
  1-1-living-orb-overlay-core: ready-for-dev
  1-2-local-vault-indexing-service: backlog

  # Epic 2
  epic-2: backlog
  2-1-semantic-search-rag-pipeline: backlog
  2-2-verified-response-source-ribbon: backlog
```

**Key Points:**
- Story keys in `sprint-status.yaml` **MUST** match story filenames (without `.md`)
- The parser reads this file to know which stories exist and their current status
- Story files contain only content (user story, AC, tasks), NOT metadata

---

## Common Issues & Solutions

### Issue: "'NoneType' object is not subscriptable" Error

**Cause:** Story files have YAML frontmatter that the parser can't handle.

**Solution:**
1. Remove all YAML frontmatter from story files (lines between `---` markers)
2. Ensure files start directly with `# Story X.Y: Title`

**Fix Script:**
```python
import os
import re

artifacts_dir = "_bmad-output/implementation-artifacts"
for filename in os.listdir(artifacts_dir):
    if filename.endswith('.md') and re.match(r'\d+-\d+-', filename):
        filepath = os.path.join(artifacts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find first heading line
        start_idx = next((i for i, line in enumerate(lines) if line.startswith('#')), 0)

        # Write only from heading onwards
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines[start_idx:])

        print(f"Fixed {filename}")
```

---

### Issue: Story Details Panel is Empty

**Cause:** Story file is in the wrong location.

**Solution:**
1. Verify story files are in `_bmad-output/implementation-artifacts/` (NOT in subdirectories)
2. Check filename matches the pattern: `{epic}-{story}-{slug}.md`
3. Ensure the story key in `sprint-status.yaml` matches the filename

**Check:**
```bash
ls _bmad-output/implementation-artifacts/*.md
```

Should show files like:
```
1-0-project-initialization.md
1-1-living-orb-overlay-core.md
2-1-semantic-search.md
```

---

### Issue: Project Won't Load at All

**Cause:** Malformed `sprint-status.yaml` or missing required files.

**Solution:**
1. Verify `sprint-status.yaml` exists at `_bmad-output/implementation-artifacts/sprint-status.yaml`
2. Check YAML syntax is valid (no tabs, proper indentation)
3. Ensure `development_status:` key exists
4. Verify epic and story keys follow the pattern

**Validate YAML:**
```bash
python -c "import yaml; yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml'))"
```

---

## Required File Structure Summary

```
{project-root}/
├── _bmad-output/
│   ├── implementation-artifacts/
│   │   ├── sprint-status.yaml          ← Metadata source
│   │   ├── project-state.json          ← Generated cache
│   │   ├── 1-0-story-name.md           ← Story files (pure markdown)
│   │   ├── 1-1-story-name.md
│   │   ├── 2-1-story-name.md
│   │   └── ...
│   └── planning-artifacts/
│       ├── prd.md
│       ├── architecture.md
│       ├── epics.md                     ← Planning document (NOT parsed for stories)
│       └── ...
```

**Key Takeaway:** Story files are in `implementation-artifacts/` root, NOT in subdirectories.

---

## Parser Behavior

The BMAD Dash backend (`backend/parsers/bmad_parser.py`) works as follows:

1. **Reads `sprint-status.yaml`** to get the list of epics and stories with their metadata
2. **For each story key**, looks for a matching file at `_bmad-output/implementation-artifacts/{story-key}.md`
3. **Parses the markdown** content to extract:
   - User Story (from `## User Story` section)
   - Acceptance Criteria (from `## Acceptance Criteria` section)
   - Tasks (from `## Implementation Tasks` or `## Tasks` section)
4. **Does NOT read YAML frontmatter** from story files (metadata comes from sprint-status.yaml)

---

## Migration Guide

If you have story files in the wrong format or location:

### Step 1: Move Files to Correct Location

```bash
# If files are in subdirectories
mv _bmad-output/implementation-artifacts/stories/*.md _bmad-output/implementation-artifacts/
mv epics/epic-1/*.md _bmad-output/implementation-artifacts/
```

### Step 2: Remove YAML Frontmatter

Use the Python script provided in the "Common Issues" section above.

### Step 3: Verify sprint-status.yaml

Ensure story keys match filenames:
- File: `1-1-living-orb-overlay-core.md`
- sprint-status.yaml key: `1-1-living-orb-overlay-core: ready-for-dev`

### Step 4: Test

1. Refresh BMAD Dash
2. Click on a story card
3. Verify story details (User Story, AC, Tasks) display correctly

---

## Questions?

If you encounter issues not covered here:
1. Check the browser console for JavaScript errors
2. Check the backend logs for Python errors
3. Ask the AI Coach in BMAD Dash: "Why can't I see story details?"
4. The AI Coach now has this documentation in its knowledge base

---

**Document Version:** 1.0
**Related Files:**
- `backend/parsers/bmad_parser.py` - Main parser logic
- `backend/services/story_detail_fetcher.py` - Story file reader
- `backend/services/ai_coach.py` - AI Coach with file structure knowledge
