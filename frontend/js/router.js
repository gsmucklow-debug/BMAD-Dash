/**
 * BMAD Dash - Hash-Based Router
 * Handles client-side routing without page reloads
 */

// Transition duration in milliseconds (NFR5: <100ms)
const TRANSITION_MS = 80;

export class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        this.defaultRoute = '/dashboard';
        this.pendingTransition = null; // Track pending transition timeout

        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRoute());

        // Handle initial load
        window.addEventListener('DOMContentLoaded', () => this.handleRoute());
    }

    /**
     * Registers a route handler
     * @param {string} path - Route path (e.g., '/dashboard')
     * @param {Function} handler - Function to call when route is accessed
     */
    register(path, handler) {
        this.routes[path] = handler;
    }

    /**
     * Sets the default route to load when hash is empty
     * @param {string} path - Default route path
     */
    setDefault(path) {
        this.defaultRoute = path;
    }

    /**
     * Handles route changes
     * Applies CSS transition for smooth view switching (60fps - NFR4)
     */
    handleRoute() {
        let hash = window.location.hash.slice(1) || this.defaultRoute;

        // Normalize hash if it doesn't start with /
        if (!hash.startsWith('/')) {
            hash = '/' + hash;
        }

        const handler = this.routes[hash];

        if (handler) {
            // Clear any pending transition to prevent race conditions
            if (this.pendingTransition) {
                clearTimeout(this.pendingTransition);
                this.pendingTransition = null;
            }

            // Apply fade transition for <100ms transition (NFR5) and 60fps (NFR4)
            const mainContent = document.getElementById('main-content');
            if (mainContent) {
                // Fade out
                mainContent.style.opacity = '0';
                mainContent.style.transition = `opacity ${TRANSITION_MS / 1000}s ease-in-out`;

                // Change view after fade out
                this.pendingTransition = setTimeout(() => {
                    this.currentRoute = hash;
                    handler();

                    // Fade in
                    mainContent.style.opacity = '1';
                    this.pendingTransition = null;
                }, TRANSITION_MS);
            } else {
                this.currentRoute = hash;
                handler();
            }
        } else {
            console.warn(`No handler for route: ${hash}`);
            // Fallback to default route if route not found
            if (hash !== this.defaultRoute) {
                this.navigate(this.defaultRoute);
            }
        }
    }

    /**
     * Navigates to a route programmatically
     * @param {string} path - Route path to navigate to
     */
    navigate(path) {
        // Normalize path
        if (!path.startsWith('/')) {
            path = '/' + path;
        }
        window.location.hash = path;
    }

    /**
     * Gets the current active route
     * @returns {string} Current route path
     */
    getCurrentRoute() {
        return this.currentRoute || this.defaultRoute;
    }
}
