/**
 * BMAD Dash - View Switcher Component
 * Provides buttons to switch between Dashboard, Timeline, and List views
 */

/**
 * Render the View Switcher Component
 * @param {Router} router - Router instance for navigation
 * @param {string} activeView - Currently active view ('/dashboard', '/timeline', or '/list')
 */
export function render(router, activeView = '/dashboard') {
    const container = document.getElementById('view-switcher-container');
    if (!container) {
        console.warn('View switcher container not found');
        return;
    }

    const views = [
        { name: 'Dashboard', route: '/dashboard' },
        { name: 'Timeline', route: '/timeline' },
        { name: 'List', route: '/list' }
    ];

    const buttonsHTML = views.map(view => {
        const isActive = activeView === view.route;
        const activeClass = isActive
            ? 'bg-bmad-accent text-white'
            : 'bg-bmad-gray text-bmad-text hover:bg-bmad-muted';

        return `
            <button
                data-route="${view.route}"
                class="px-6 py-2 min-w-[44px] min-h-[44px] rounded font-medium transition-colors ${activeClass}"
                aria-current="${isActive ? 'page' : 'false'}"
            >
                ${view.name}
            </button>
        `;
    }).join('');

    container.innerHTML = `
        <div class="flex gap-2 items-center">
            ${buttonsHTML}
        </div>
    `;

    // Bind click events to router navigation
    const buttons = container.querySelectorAll('button[data-route]');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const route = button.getAttribute('data-route');
            router.navigate(route);
        });
    });
}

/**
 * Update active state without re-rendering
 * @param {string} activeView - Currently active view
 */
export function updateActive(activeView) {
    const container = document.getElementById('view-switcher-container');
    if (!container) return;

    const buttons = container.querySelectorAll('button[data-route]');
    buttons.forEach(button => {
        const route = button.getAttribute('data-route');
        const isActive = route === activeView;

        if (isActive) {
            button.classList.remove('bg-bmad-gray', 'text-bmad-text', 'hover:bg-bmad-muted');
            button.classList.add('bg-bmad-accent', 'text-white');
            button.setAttribute('aria-current', 'page');
        } else {
            button.classList.remove('bg-bmad-accent', 'text-white');
            button.classList.add('bg-bmad-gray', 'text-bmad-text', 'hover:bg-bmad-muted');
            button.setAttribute('aria-current', 'false');
        }
    });
}
