# Parser Audit Report: Hardcoded Assumptions Analysis

**Date:** 2026-01-13
**Scope:** Identification of BMAD Dash-specific assumptions that may break on Echo-OS project
**Task:** Prep work for Epic 6 Multi-Project Validation

## Executive Summary

The parser code contains **7 key hardcoded assumptions** that are BMAD Dash-specific. Most have fallback logic, but Echo-OS may still encounter issues if it uses different directory structures or naming conventions.

**Risk Level: MEDIUM** - Many assumptions have fallbacks, but some are brittle.

---

## Critical Assumptions Identified

### 1. Directory Structure: `_bmad-output` (HARDCODED)

**Location:** `backend/parsers/bmad_parser.py:43-45`, `backend/services/phase_detector.py:35`

**Current Logic:**
```python
self.bmad_output = os.path.join(root_path, "_bmad-output")
self.implementation_artifacts = os.path.join(self.bmad_output, "implementation-artifacts")
self.planning_artifacts = os.path.join(self.bmad_output, "planning-artifacts")
```

**Assumption:** All BMAD projects use `_bmad-output/` directory at project root.

**What Could Break:**
- Echo-OS uses different naming (e.g., `bmad-output/`, `artifacts/`, `.bmad/`)
- Echo-OS stores artifacts in different location
- Different subdirectory structure (e.g., `_bmad-output/implementation/` instead of `implementation-artifacts/`)

**Fallback?** ✅ YES (Phase detector checks multiple locations)
- Checks: `_bmad-output/implementation-artifacts/`, `_bmad-output/`, root path
- **BUT:** Parser still hardcodes `_bmad-output` primarily

**Risk:** 🟡 MEDIUM - Parser will work if artifacts exist, but may not find all files

---

### 2. Story File Location & Naming Convention

**Location:** `backend/services/git_correlator.py:346-347`

**Current Logic:**
```python
os.path.join(project_root, "_bmad-output", "implementation-artifacts", f"{story_key}-*.md")
os.path.join(project_root, "_bmad-output", "implementation", f"{story_key}-*.md")  # Fallback
```

**Assumption:** Story files match pattern `{epic}-{story}-{name}.md`
Examples: `5-1-gemini-api-integration.md`, `5-2-project-aware-qa.md`

**What Could Break:**
- Echo-OS uses different naming (e.g., `story-5.1.md`, `5_1_name.md`, `Story_5-1.md`)
- Hyphenation is different (underscores vs hyphens)
- Story files stored differently (nested by epic, different format)

**Fallback?** ✅ YES (checks two directory patterns)
- Primary: `implementation-artifacts/`
- Fallback: `implementation/`

**Risk:** 🟢 LOW - Glob pattern `{story_key}-*.md` is flexible with naming

---

### 3. Required File Names (HARDCODED)

**Locations:** Multiple services reference specific filenames

**Files Assumed to Exist:**
- `sprint-status.yaml` - Project status tracking
- `epics.md` - Epic definitions
- `prd.md` - Product Requirements
- `architecture.md` - Architecture document
- `brainstorming.md` or `product-brief.md` - Analysis phase files

**What Could Break:**
- Echo-OS renamed files (e.g., `sprint_status.yaml` with underscore)
- Case sensitivity issues (e.g., `Epics.md` vs `epics.md`)
- Different file extensions (e.g., `.markdown` instead of `.md`)
- Files stored in different locations

**Fallback?** ✅ PARTIAL
- Phase detector checks multiple locations for each file
- **BUT:** Parser specifically looks for `sprint-status.yaml` only

**Risk:** 🟡 MEDIUM - File naming is strict, location is flexible

---

### 4. Sprint Status YAML Format (IMPLICIT ASSUMPTION)

**Location:** `backend/parsers/bmad_parser.py:84-95`

**Current Logic:**
```python
dev_status = parsed.get('development_status', {})
if dev_status:
    epics = self._parse_development_status(dev_status)
else:
    epics_data = parsed.get('epics', [])
```

**Assumption:** Sprint status uses flat `development_status:` structure

**Example Format:**
```yaml
development_status:
  epic-5: done
  5-1-story-name: done
  5-2-another-story: in-progress
```

**What Could Break:**
- Echo-OS uses nested structure:
  ```yaml
  epics:
    - id: 5
      stories:
        - id: 1
          name: story-name
          status: done
  ```
- Different status values (e.g., `completed` vs `done`)
- Different key naming (e.g., `progress_status` vs `development_status`)

**Fallback?** ✅ YES (checks both flat and nested formats)

**Risk:** 🟢 LOW - Handles both formats

---

### 5. Story ID Format (HARDCODED REGEX)

**Location:** `backend/parsers/bmad_parser.py:145`

**Current Logic:**
```python
story_match = re.match(r'^(\d+)-(\d+)-(.+)$', key)
# Matches: "5-1-story-name" → epic=5, story=1, name="story-name"
```

**Assumption:** Story IDs are exactly `{epic}-{story}-{name}` format

**What Could Break:**
- Echo-OS uses decimal format: `5.1` instead of `5-1`
- Echo-OS uses concatenated format: `51` instead of `5-1`
- Non-numeric components: `epic-5-story-1` instead of `5-1`

**Fallback?** ❌ NO - Regex is strict

**Risk:** 🔴 HIGH - If Echo-OS uses different ID format, parsing will fail silently

---

### 6. Project Root Path Extraction (IMPLICIT)

**Location:** `backend/parsers/bmad_parser.py:59`

**Current Logic:**
```python
project_name = os.path.basename(self.root_path)
# Example: "/Users/gary/BMAD-Dash" → project_name = "BMAD-Dash"
```

**Assumption:** Uses directory name as project name

**What Could Break:**
- Echo-OS might need project name from `prd.md` or `project.yaml` instead
- Directory name doesn't match actual project name

**Fallback?** ⚠️ WEAK - Will use directory name regardless

**Risk:** 🟡 MEDIUM - Wrong project name in UI (cosmetic, not functional)

---

### 7. Cache Strategy: File mtime Checking

**Location:** `backend/services/project_state_cache.py:341-346`

**Current Logic:**
```python
sprint_status_path = os.path.join(project_root, "_bmad-output/implementation-artifacts/sprint-status.yaml")
if sprint_status_path changed:
    trigger refresh
```

**Assumption:** File modification time indicates content changes

**What Could Break:**
- Echo-OS has rapid file changes in same second (mtime resolution is 1 second)
- Files modified but content not actually changed
- Symlinks or copy operations preserve old mtime

**Fallback?** ✅ YES - Manual refresh button always available

**Risk:** 🟢 LOW - Worst case: stale cache, user can refresh manually

---

## Test Plan for Echo-OS

### Before Testing (Validation Checklist)

When you load BMAD Dash on Echo-OS, verify:

1. **Directory Structure** ✓
   - [ ] Does Echo-OS have `_bmad-output/` directory?
   - [ ] Does it have `implementation-artifacts/` subdirectory?
   - [ ] Are story files in that location?

2. **File Names** ✓
   - [ ] Is there a `sprint-status.yaml` file?
   - [ ] Is it named exactly with that case/extension?
   - [ ] Are story files named as `{epic}-{story}-{name}.md`?

3. **Story ID Format** ✓
   - [ ] In sprint-status.yaml, are story IDs formatted as `5-1-name`?
   - [ ] Not as `5.1` or `story-5.1` or other variations?

4. **Sprint Status Format** ✓
   - [ ] Does sprint-status.yaml have a `development_status:` key?
   - [ ] Or does it use nested `epics:` structure instead?

5. **Phase Detection** ✓
   - [ ] Does dashboard correctly detect Echo-OS phase?
   - [ ] Log the detected phase and verify it's correct

### During Testing (Watch For)

- Dashboard doesn't load or times out (parsing failure)
- Stories not appearing in Kanban (ID mismatch)
- Project name shows as directory name instead of actual name
- Cache issues (stale data after file updates)
- Performance problems (large project size)

---

## Recommendations

### High Priority (Fix Before Echo-OS Testing)

1. **Story ID Format** - Make parser flexible to handle both `5-1` and `5.1` formats
   - Update regex in `bmad_parser.py:145` to accept both
   - Risk: 🔴 HIGH - Will break silently on Echo-OS if it uses decimal format

### Medium Priority (Fix If Echo-OS Breaks)

2. **Directory Structure** - Add explicit error messages when `_bmad-output` not found
   - Currently fails silently → makes debugging hard
   - Add logging: "Could not find artifacts in standard locations"

3. **Sprint Status Format** - Verify fallback logic actually works for nested format

### Low Priority (Polish)

4. **Project Name** - Add optional `project.yaml` with explicit name
5. **Performance** - Profile cache strategy with large projects

---

## Summary

**Total Assumptions:** 7
**High Risk:** 1 (story ID format)
**Medium Risk:** 3 (directory structure, file names, project naming)
**Low Risk:** 3 (sprint status format, cache strategy)

**Biggest Risk:** If Echo-OS uses `5.1` instead of `5-1` format for story IDs, the parser will silently fail to extract stories and the dashboard will show empty Kanban board.

**Recommendation:** Before testing on Echo-OS, ask yourself:
- What's the story ID format in Echo-OS' sprint-status.yaml?
- If it's different from `5-1` format, we need to fix the regex first.

