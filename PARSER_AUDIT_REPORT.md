# Parser Audit Report: Hardcoded Assumptions Analysis

**Date:** 2026-01-13
**Scope:** Identification of BMAD Dash-specific assumptions that may break on Echo-OS project
**Task:** Prep work for Epic 6 Multi-Project Validation

## Executive Summary

The parser code contains **7 key hardcoded assumptions** that were BMAD Dash-specific. All have been **validated or fixed** for multi-project support during Epic 6.

**Risk Level: LOW** - Now validated on Echo-OS project.

---

## Critical Assumptions Identified

### 1. Directory Structure: `_bmad-output` (HARDCODED)
- **Status:** ✅ VALIDATED on Echo-OS
- **Finding:** Echo-OS uses identical structure.
- **Robustness:** Phase detector handles variations; parser is stable with standard structure.

### 2. Story File Location & Naming Convention
- **Status:** ✅ VALIDATED on Echo-OS
- **Finding:** Echo-OS uses `{epic}-{story}-{name}.md` pattern.
- **Robustness:** Glob patterns `{story_key}-*.md` confirmed flexible.

### 3. Required File Names (HARDCODED)
- **Status:** ✅ VALIDATED on Echo-OS
- **Finding:** All standard files (`sprint-status.yaml`, `epics.md`, etc.) are present.
- **Robustness:** Critical files are strictly checked; optional files degrade gracefully.

### 4. Sprint Status YAML Format (IMPLICIT ASSUMPTION)
- **Status:** ✅ VALIDATED on Echo-OS
- **Finding:** Uses flat `development_status:` structure.
- **Robustness:** Parser correctly handles both flat and nested formats.

### 5. Story ID Format (HARDCODED REGEX)
- **Status:** ✅ VALIDATED & FIXED
- **Finding:** Hyphenated format `5-1` works perfectly.
- **Robustness:** Added robustness tests for decimal and double-digit variations.

### 6. Project Root Path Extraction (IMPLICIT)
- **Status:** ✅ VALIDATED on Echo-OS
- **Finding:** Correctly extracts "Echo-OS" from directory name.
- **Robustness:** Consistent across all local projects.

### 7. Cache Strategy: File mtime Checking
- **Status:** ✅ VALIDATED on Echo-OS
- **Finding:** Correctly triggers refresh and sync.
- **Robustness:** Project-keyed cache ensures isolation.

---

## Summary Result

**Total Assumptions:** 7
**Validated on Echo-OS:** 7
**Critical Failures:** 0

**Conclusion:** BMAD Dash is robust for multi-project use with standard BMAD Method artifacts.

