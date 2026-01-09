---
story_id: "1.4"
story_key: "1-4-frontend-shell-breadcrumb-navigation"
epic: 1
title: "Frontend Shell & Breadcrumb Navigation"
status: "ready-for-dev"
created: "2026-01-09"
context_engine_version: "v1.0"
---

# Story 1.4: Frontend Shell & Breadcrumb Navigation

## User Story

As a **user**,  
I want **a dark-themed SPA that shows my project hierarchy in breadcrumbs**,  
So that **I can instantly see where I am: Project → Phase → Epic → Story → Task**.

## Business Context

This story delivers the first user-facing component of BMAD Dash - the frontend shell that fetches data from the `/api/dashboard` endpoint (Story 1.3) and renders the breadcrumb navigation showing the project hierarchy. This is the first visual element users see when opening BMAD Dash.

**Value:** Enables instant project orientation within 3 seconds of page load, eliminating cognitive overhead of "where am I?" questions.

## Acceptance Criteria

**Given** the frontend is loaded at localhost:5000  
**When** the page renders  
**Then** `index.html` is served with dark theme (#1a1a1a background)

**And** breadcrumb component displays at top of page

**And** breadcrumb shows Project → Phase → Epic → Story → Task with arrows

**And** current level in breadcrumb is visually distinct (highlighted)

**And** Tailwind CSS classes are applied correctly (dark theme enforced)

**And** `app.js` fetches `/api/dashboard` on page load

**And** `breadcrumb.js` component renders navigation from API data

**And** page loads and becomes interactive in <500ms (NFR1 requirement)

**And** no JavaScript errors in console

**And** ES6 modules load correctly (no transpilation needed)

---

## Implementation Tasks

### Task 1: Update `index.html` with Frontend Shell Structure
**Implementation Details:**
- Update `frontend/index.html` with complete dark-themed structure
- Add viewport meta tag for responsive design
- Link Tailwind CSS output file (`/css/output.css`)
- Create main layout: header (breadcrumb area), main content area, footer placeholder
- Add script tag for `app.js` as ES6 module (`type="module"`)
- Ensure dark theme background (#1a1a1a) applied to `<body>`
- Add loading state placeholder that disappears when data loads
- Include minimal inline styles for critical rendering path (dark bg)
- Add console error handler for debugging
- Structure should support future Quick Glance Bar (Story 1.5) placement

**Acceptance:**
- HTML structure semantically correct
- Dark theme applied by default
- Tailwind CSS linked and loading
- ES6 modules work correctly
- No console errors on load

### Task 2: Create `frontend/js/app.js` Main Application Controller
**Implementation Details:**
- Create main application entry point at `frontend/js/app.js`
- Implement `init()` function that runs on DOMContentLoaded
- Fetch project root from localStorage or use default (F:/BMAD Dash for testing)
- Implement `fetchDashboardData()` to call `/api/dashboard?project_root=...`
- Handle API response and parse JSON
- Pass data to breadcrumb component for rendering
- Implement error handling for API failures (show user-friendly message)
- Add loading state management (show/hide spinner)
- Cache project root selection in localStorage
- Export functions for use by other modules
- Add performance measurement (log to console if >500ms)
- Handle offline/network error gracefully

**Acceptance:**
- App initializes on page load
- Fetches dashboard data successfully
- Handles errors gracefully
- Passes data to components
- Performance <500ms measured

### Task 3: Create `frontend/js/components/breadcrumb.js` Component
**Implementation Details:**
- Create breadcrumb component at `frontend/js/components/breadcrumb.js`
- Export `render(data)` function that accepts dashboard API data
- Extract breadcrumb object from data: `{project, phase, epic, story, task}`
- Build breadcrumb HTML with Project → Phase → Epic → Story → Task
- Use `→` arrow character as separator between levels
- Apply Tailwind classes for dark theme styling
- Highlight current level (last non-null element) with distinct color
- Handle null values gracefully (e.g., if task is null, show up to story)
- Use semantic HTML (nav, ol, li elements)
- Each breadcrumb level is a separate `<li>` element
- Future-proof: Add data attributes for click handlers (Story 1.4+ navigation)
- Ensure text is readable (high contrast against #1a1a1a background)
- Use minimum 14px font size (NFR14)
- Add generous spacing between breadcrumb levels (UX requirement)

**Acceptance:**
- Breadcrumb renders from API data
- Shows Project → Phase → Epic → Story → Task
- Handles null values correctly
- Styling matches dark theme
- Text is readable and properly sized

### Task 4: Create `frontend/css/input.css` Tailwind Configuration
**Implementation Details:**
- Create `frontend/css/input.css` with Tailwind directives
- Add `@tailwind base;`, `@tailwind components;`, `@tailwind utilities;`
- Add custom BMAD-specific utility classes:
  - `.bg-bmad-dark` for #1a1a1a background
  - `.text-bmad-light` for light text color
  - `.breadcrumb-separator` for arrow styling
  - `.breadcrumb-current` for current level highlight
- Define custom colors in Tailwind config for BMAD theme
- Ensure dark mode is enforced (not toggleable)
- Add base styles for body (dark background, light text)
- Include responsive breakpoints if needed
- Keep CSS minimal (leverage Tailwind utilities)

**Acceptance:**
- Tailwind compiles without errors
- Custom BMAD utilities work
- Dark theme enforced
- CSS output file generated

### Task 5: Update `tailwind.config.js` with BMAD Theme
**Implementation Details:**
- Update `tailwind.config.js` to include BMAD-specific configuration
- Set `darkMode: 'class'` (though we enforce it, not toggle)
- Add custom colors to theme.extend.colors:
  - `bmad-dark: '#1a1a1a'` (main background)
  - `bmad-gray: '#2a2a2a'` (card backgrounds)
  - `bmad-accent: '#4a9eff'` (current breadcrumb highlight)
  - `bmad-text: '#e0e0e0'` (main text color)
  - `bmad-muted: '#888888'` (secondary text)
- Configure content paths: `['./frontend/**/*.{html,js}']`
- Add custom utilities if needed
- Configure JIT mode (already default in Tailwind v3)
- Ensure purge/content setting includes all frontend files
- Add custom spacing if needed for generous whitespace (UX req)

**Acceptance:**
- Tailwind config loads correctly
- Custom colors defined and usable
- Content paths correct for purging
- npm run build:css works

### Task 6: Add npm Scripts for Tailwind CSS Build
**Implementation Details:**
- Update `package.json` with Tailwind build scripts:
  - `"build:css": "tailwindcss -i frontend/css/input.css -o frontend/css/output.css"`
  - `"watch:css": "tailwindcss -i frontend/css/input.css -o frontend/css/output.css --watch"`
- Ensure `tailwindcss` is installed as devDependency
- Add `frontend/css/output.css` to `.gitignore` (generated file)
- Test that `npm run build:css` generates output file
- Test that `npm run watch:css` recompiles on changes
- Document in README how to build CSS during development

**Acceptance:**
- npm scripts execute successfully
- output.css is generated
- Watch mode works for development
- Generated file excluded from git

### Task 7: Create Project Root Selector UI Component
**Implementation Details:**
- Add project root selector to `index.html` (top-right corner or header)
- Create simple input field + "Load Project" button
- On button click, update localStorage with new project root
- Trigger re-fetch of dashboard data with new project root
- Display current project root in UI
- Handle file path format (Windows/Unix paths)
- Validate path exists (via API call) before loading
- Show error message if path invalid
- Auto-populate with last used project root from localStorage
- Style with dark theme to match overall design
- Make button minimum 44x44px (NFR10)
- Add loading indicator while fetching new project data

**Acceptance:**
- User can enter project root path
- Project data loads for specified path
- Path is persisted in localStorage
- Error handling for invalid paths
- UI matches dark theme

### Task 8: Write Comprehensive Frontend Tests
**Implementation Details:**
- Create `tests/test_frontend_integration.py` using pytest-flask
- Test serving `index.html` at localhost:5000
- Test that Tailwind CSS file is accessible at `/css/output.css`
- Test that JS modules are accessible at `/js/app.js`
- Create `frontend/js/__tests__/breadcrumb.test.js` for component unit tests
- Test breadcrumb rendering with full data (all levels present)
- Test breadcrumb rendering with partial data (null task, null story, etc.)
- Test breadcrumb highlighting of current level
- Test API integration (app.js fetches /api/dashboard)
- Test error handling (API returns 404, 500)
- Test loading states render correctly
- Use JSDOM or similar for JS testing if available, otherwise manual testing
- Document manual testing steps in README

**Acceptance:**
- Flask serves frontend files correctly
- Breadcrumb component renders correctly with various data
- API integration works
- Error states handled
- All frontend tests passing

---

## Technical Specifications

### Frontend Structure

**HTML (`frontend/index.html`):**
```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMAD Dash - Project Orientation Dashboard</title>
    <link href="/css/output.css" rel="stylesheet">
</head>
<body class="bg-bmad-dark text-bmad-text min-h-screen">
    <div id="app" class="container mx-auto px-4 py-6">
        <!-- Project Root Selector -->
        <div id="project-selector" class="mb-6">
            <!-- Project selector UI -->
        </div>
        
        <!-- Breadcrumb Navigation -->
        <nav id="breadcrumb-container" class="mb-6">
            <!-- Breadcrumb will render here -->
        </nav>
        
        <!-- Quick Glance Bar (Placeholder for Story 1.5) -->
        <div id="quick-glance-container" class="mb-6">
            <!-- Quick Glance will render in Story 1.5 -->
        </div>
        
        <!-- Main Content Area (Future Kanban Board) -->
        <main id="main-content" class="mt-8">
            <div id="loading" class="text-center text-bmad-muted">
                Loading dashboard...
            </div>
            <div id="error" class="hidden text-red-500">
                <!-- Error messages -->
            </div>
        </main>
    </div>
    
    <script type="module" src="/js/app.js"></script>
</body>
</html>
```

**App Controller (`frontend/js/app.js`):**
```javascript
import { render as renderBreadcrumb } from './components/breadcrumb.js';

const DEFAULT_PROJECT_ROOT = 'F:/BMAD Dash';

async function init() {
    console.time('Dashboard Load Time');
    
    const projectRoot = localStorage.getItem('bmad_project_root') || DEFAULT_PROJECT_ROOT;
    
    try {
        showLoading();
        const data = await fetchDashboardData(projectRoot);
        hideLoading();
        
        renderBreadcrumb(data.breadcrumb);
        // Future: render Quick Glance (Story 1.5)
        // Future: render Kanban (Story 3.2)
        
        console.timeEnd('Dashboard Load Time');
    } catch (error) {
        hideLoading();
        showError(error.message);
        console.error('Dashboard load failed:', error);
    }
}

async function fetchDashboardData(projectRoot) {
    const response = await fetch(`/api/dashboard?project_root=${encodeURIComponent(projectRoot)}`);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to load dashboard');
    }
    
    return response.json();
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = `Error: ${message}`;
    errorDiv.classList.remove('hidden');
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);

export { fetchDashboardData, init };
```

**Breadcrumb Component (`frontend/js/components/breadcrumb.js`):**
```javascript
export function render(breadcrumbData) {
    const container = document.getElementById('breadcrumb-container');
    
    if (!breadcrumbData) {
        container.innerHTML = '<p class="text-bmad-muted">No breadcrumb data available</p>';
        return;
    }
    
    const levels = [];
    
    // Build breadcrumb levels array
    if (breadcrumbData.project) {
        levels.push({ label: breadcrumbData.project, type: 'project' });
    }
    if (breadcrumbData.phase) {
        levels.push({ label: breadcrumbData.phase, type: 'phase' });
    }
    if (breadcrumbData.epic) {
        levels.push({ label: breadcrumbData.epic.title, type: 'epic', id: breadcrumbData.epic.id });
    }
    if (breadcrumbData.story) {
        levels.push({ label: breadcrumbData.story.title, type: 'story', id: breadcrumbData.story.id });
    }
    if (breadcrumbData.task) {
        levels.push({ label: breadcrumbData.task.title, type: 'task', id: breadcrumbData.task.id });
    }
    
    // Render breadcrumb
    const breadcrumbHTML = `
        <nav aria-label="Breadcrumb navigation">
            <ol class="flex items-center space-x-2 text-sm">
                ${levels.map((level, index) => {
                    const isLast = index === levels.length - 1;
                    const classes = isLast 
                        ? 'text-bmad-accent font-semibold' 
                        : 'text-bmad-muted';
                    
                    return `
                        <li class="flex items-center">
                            <span class="${classes}" data-type="${level.type}" data-id="${level.id || ''}">
                                ${level.label}
                            </span>
                            ${!isLast ? '<span class="ml-2 text-bmad-muted">→</span>' : ''}
                        </li>
                    `;
                }).join('')}
            </ol>
        </nav>
    `;
    
    container.innerHTML = breadcrumbHTML;
}
```

**Tailwind Input (`frontend/css/input.css`):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
    body {
        @apply bg-bmad-dark text-bmad-text;
    }
}

@layer utilities {
    .breadcrumb-separator {
        @apply text-bmad-muted mx-2;
    }
    
    .breadcrumb-current {
        @apply text-bmad-accent font-semibold;
    }
}
```

**Tailwind Config (`tailwind.config.js`):**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./frontend/**/*.{html,js}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'bmad-dark': '#1a1a1a',
        'bmad-gray': '#2a2a2a',
        'bmad-accent': '#4a9eff',
        'bmad-text': '#e0e0e0',
        'bmad-muted': '#888888',
      },
    },
  },
  plugins: [],
}
```

### Performance Targets

- **Page Load to Interactive:** <500ms (NFR1)
  - HTML parse: <50ms
  - CSS load: <50ms
  - JS load + execute: <100ms
  - API fetch: <200ms (leverages cache from Story 1.3)
  - DOM render: <100ms
  - Total buffer: 0ms (tight but achievable with caching)

- **API Response Time:** <50ms (cached), <200ms (uncached)
- **Breadcrumb Render Time:** <100ms
- **Memory Usage:** <10MB for frontend shell (well under 100MB NFR8)

### Browser Compatibility

- **Target:** Modern browsers with ES6 module support
- Chrome 87+, Firefox 88+, Safari 14+, Edge 88+
- No transpilation required (ES6 native support)
- No polyfills needed for target browsers

---

## Files to Create/Modify

**Frontend Files:**
- `frontend/index.html` - MODIFY - Complete HTML structure with dark theme
- `frontend/js/app.js` - CREATE - Main application controller
- `frontend/js/components/breadcrumb.js` - CREATE - Breadcrumb component
- `frontend/css/input.css` - MODIFY - Tailwind input file with custom utilities
- `tailwind.config.js` - MODIFY - BMAD theme configuration

**Build Configuration:**
- `package.json` - MODIFY - Add Tailwind build scripts
- `.gitignore` - MODIFY - Exclude `frontend/css/output.css`

**Tests:**
- `tests/test_frontend_integration.py` - CREATE - Frontend integration tests

**Total:** 8 files (3 new, 5 modified)

---

## Dependencies

**Completed Stories:**
- ✅ Story 0.1: Project Scaffold (frontend structure exists)
- ✅ Story 1.3: Dashboard API Endpoint (provides data for frontend)

**Required For:**
- Story 1.5: Quick Glance Bar (builds on this frontend shell)
- Story 3.1: View Mode Switching (extends this shell with routing)

**NPM Dependencies (should already be installed from Story 0.1):**
- `tailwindcss` ^3.4.0

---

## Testing Strategy

### Manual Testing Checklist
- [ ] Open localhost:5000, verify dark theme (#1a1a1a background)
- [ ] Verify breadcrumb shows Project → Phase → Epic → Story → Task
- [ ] Verify current level is highlighted (blue accent color)
- [ ] Change project root, verify breadcrumb updates
- [ ] Test with missing epic/story/task (breadcrumb handles nulls)
- [ ] Check console for errors (should be none)
- [ ] Verify page load <500ms (use DevTools Performance tab)
- [ ] Test on Chrome, Firefox, Safari, Edge (ES6 modules work)

### Automated Tests
- Test Flask serves `index.html` at `/`
- Test Flask serves static files (`/css/output.css`, `/js/app.js`)
- Test breadcrumb component renders with full data
- Test breadcrumb component handles null values
- Test API integration (app.js calls /api/dashboard)

---

## Status

**Current Status:** ready-for-dev  
**Created:** 2026-01-09  
**Epic:** 1 (Core Orientation System)  
**Dependencies:** Story 0.1, 1.3 (all complete)

**Next Steps:**
1. Update `index.html` with dark-themed structure
2. Create `app.js` main controller with API integration
3. Create `breadcrumb.js` component
4. Configure Tailwind CSS with BMAD theme
5. Add npm build scripts
6. Create project root selector UI
7. Write comprehensive tests
8. Verify <500ms page load performance
9. Move to Story 1.5 (Quick Glance Bar)
