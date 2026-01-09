/**
 * BMAD Dash - Hash-Based Router
 * Handles client-side routing without page reloads
 */

export class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;

        // Listen for hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
    }

    /**
     * Registers a route handler
     * Will be expanded in Story 1.2
     */
    register(path, handler) {
        this.routes[path] = handler;
    }

    /**
     * Handles route changes
     */
    handleRoute() {
        const hash = window.location.hash.slice(1) || '/';
        const handler = this.routes[hash];

        if (handler) {
            this.currentRoute = hash;
            handler();
        } else {
            console.warn(`No handler for route: ${hash}`);
        }
    }

    /**
     * Navigates to a route
     */
    navigate(path) {
        window.location.hash = path;
    }
}
