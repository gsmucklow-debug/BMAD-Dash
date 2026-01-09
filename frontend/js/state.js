/**
 * BMAD Dash - Client-Side State Management
 * Manages application state and reactivity
 */

export class State {
    constructor() {
        this.data = {
            project: null,
            currentView: 'dashboard',
            selectedStory: null
        };
        this.listeners = [];
    }

    /**
     * Updates state and notifies listeners
     * Will be expanded in Story 1.2
     */
    update(key, value) {
        this.data[key] = value;
        this.notify();
    }

    /**
     * Gets state value
     */
    get(key) {
        return this.data[key];
    }

    /**
     * Subscribes to state changes
     */
    subscribe(callback) {
        this.listeners.push(callback);
    }

    /**
     * Notifies all listeners of state change
     */
    notify() {
        this.listeners.forEach(callback => callback(this.data));
    }
}
