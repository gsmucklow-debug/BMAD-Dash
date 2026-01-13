/**
 * BMAD Documentation Sync Component
 * Handles checking for and updating BMAD documentation
 */

export class BMADSync {
    constructor() {
        this.status = null;
        this.updateAvailable = false;
        this.isUpdating = false;
        this.projectRoot = null;
    }

    async init(projectRoot) {
        this.projectRoot = projectRoot;
        await this.checkStatus();
    }

    async checkStatus() {
        try {
            const response = await fetch(`/api/bmad-sync/status?project_root=${encodeURIComponent(this.projectRoot)}`);
            if (!response.ok) throw new Error('Failed to check status');
            this.status = await response.json();
            this.updateAvailable = this.status.update_available || false;
            this.render();
        } catch (error) {
            console.error('Error checking BMAD sync status:', error);
        }
    }

    async forceCheck() {
        try {
            const response = await fetch('/api/bmad-sync/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_root: this.projectRoot })
            });
            if (!response.ok) throw new Error('Failed to check updates');
            const result = await response.json();
            this.updateAvailable = result.has_updates;
            this.status = { ...this.status, ...result };
            this.render();
        } catch (error) {
            console.error('Error checking BMAD updates:', error);
        }
    }

    async performSync() {
        if (this.isUpdating) return;
        this.isUpdating = true;
        this.render();

        try {
            const response = await fetch('/api/bmad-sync/perform', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_root: this.projectRoot })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to sync documentation');
            }

            const result = await response.json();
            this.status = { ...this.status, ...result, last_updated: new Date().toISOString() };
            this.updateAvailable = false;
            alert('BMAD Documentation successfully synced to local _bmad folder.');
        } catch (error) {
            console.error('Error syncing BMAD docs:', error);
            alert(`Sync failed: ${error.message}`);
        } finally {
            this.isUpdating = false;
            this.render();
        }
    }

    async viewDocs() {
        // Open docs in browser (no download)
        const docsUrl = this.status?.docs_url || 'http://docs.bmad-method.org';
        window.open(docsUrl, '_blank');

        // Mark as seen so banner goes away if they don't want to sync right now
        try {
            await fetch('/api/bmad-sync/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_root: this.projectRoot,
                    version: this.status?.latest_version
                })
            });
            this.updateAvailable = false;
            this.render();
        } catch (e) {
            console.error('Failed to mark docs as seen:', e);
        }
    }

    render() {
        const container = document.getElementById('bmad-sync-container');
        if (!container) return;

        if (this.updateAvailable) {
            container.innerHTML = `
                <div class="bg-bmad-surface border border-bmad-yellow/30 rounded-lg p-4 mb-4 backdrop-blur-sm shadow-lg animate-pulse-subtle">
                    <div class="flex items-center justify-between">
                        <div>
                            <div class="flex items-center gap-2">
                                <span class="w-2 h-2 rounded-full bg-bmad-yellow animate-ping"></span>
                                <h3 class="text-bmad-yellow font-semibold">BMAD Documentation Update Available</h3>
                            </div>
                            <p class="text-bmad-text text-sm mt-1">
                                Latest: <span class="font-mono text-bmad-accent">${this.status.latest_version || 'v.latest'}</span>
                            </p>
                        </div>
                        <div class="flex gap-2">
                            <button id="view-bmad-btn" class="bg-bmad-gray hover:bg-bmad-gray/80 text-white px-4 py-2 rounded text-sm font-medium transition-colors">
                                View Online
                            </button>
                            <button id="sync-bmad-btn" class="bg-bmad-yellow hover:bg-bmad-yellow/80 text-bmad-dark px-4 py-2 rounded text-sm font-bold shadow-md transition-all active:scale-95">
                                ${this.isUpdating ? 'Syncing...' : 'Sync Now (Offline)'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('view-bmad-btn')?.addEventListener('click', () => this.viewDocs());
            document.getElementById('sync-bmad-btn')?.addEventListener('click', () => this.performSync());
        } else {
            const lastUpdated = this.status?.last_updated ? new Date(this.status.last_updated).toLocaleString() : 'Never';

            container.innerHTML = `
                <div class="bg-bmad-surface border border-bmad-green/30 rounded-lg p-4 mb-4 backdrop-blur-sm">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="text-bmad-green font-semibold">BMAD Documentation Synced</h3>
                            <p class="text-bmad-text/60 text-[10px] mt-1">
                                Version: <span class="text-bmad-text">${this.status.current_version}</span> | 
                                Last Sync: <span class="text-bmad-text">${lastUpdated}</span>
                            </p>
                        </div>
                        <div class="flex gap-4 items-center">
                            <a href="${this.status.docs_url || 'http://docs.bmad-method.org'}" target="_blank" class="text-bmad-text/60 hover:text-bmad-accent text-xs underline transition-colors">
                                View Online
                            </a>
                            <button id="check-bmad-btn" class="bg-bmad-gray/30 hover:bg-bmad-gray/50 text-bmad-text px-3 py-1 rounded text-[10px] transition-colors">
                                Check for updates
                            </button>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('check-bmad-btn')?.addEventListener('click', () => this.forceCheck());
        }
    }
}

// Singleton instance
let bmadSyncInstance = null;

export function getBMADSync() {
    if (!bmadSyncInstance) {
        bmadSyncInstance = new BMADSync();
    }
    return bmadSyncInstance;
}
