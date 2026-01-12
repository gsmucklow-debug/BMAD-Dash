/**
 * BMAD Dash - Cache Status Component
 * Story 5.55: Smart Per-Project Cache Layer
 * Displays cache statistics and provides cache management controls
 */

/**
 * Render cache status indicator
 * @param {Object} cacheData - Cache statistics from API
 * @param {string} projectRoot - Project root path
 * @returns {string} HTML string
 */
export function render(cacheData, projectRoot) {
    if (!cacheData) {
        return '';
    }

    const { total_stories, status_counts, cache_age_ms, cache_file_exists } = cacheData;

    // Format cache age
    const cacheAgeText = formatCacheAge(cache_age_ms);

    // Calculate done stories count
    const doneCount = status_counts['done'] || 0;

    return `
        <div class="cache-status bg-bmad-surface/50 border border-bmad-gray rounded-lg p-3 mb-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="flex items-center gap-2">
                        <span class="text-sm font-medium text-bmad-text">Cache</span>
                        <span class="text-xs text-bmad-muted">
                            ${cache_file_exists ?
            `<span class="text-bmad-green animate-pulse">●</span> ${doneCount} done stories cached` :
            `<span class="text-bmad-muted">○</span> Not cached yet`
        }
                        </span>
                    </div>
                    ${cache_file_exists ? `
                        <span class="text-xs text-bmad-muted">
                            Updated ${cacheAgeText}
                        </span>
                    ` : ''}
                </div>
                <button 
                    id="clear-cache-btn"
                    class="text-xs text-bmad-accent hover:text-bmad-accent-hover transition-colors px-2 py-1 rounded border border-bmad-accent/30 hover:border-bmad-accent/60"
                    ${!cache_file_exists ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}
                >
                    Clear Cache
                </button>
            </div>
        </div>
    `;
}

/**
 * Format cache age in human-readable format
 * @param {number} ageMs - Age in milliseconds
 * @returns {string} Formatted age string
 */
function formatCacheAge(ageMs) {
    if (!ageMs || ageMs === 0) return 'just now';

    const seconds = Math.floor(ageMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (minutes > 0) {
        return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
    } else {
        return 'just now';
    }
}

/**
 * Attach event listeners for cache management
 * @param {string} projectRoot - Project root path
 * @param {Function} onRefresh - Callback to refresh dashboard
 */
export function attachListeners(projectRoot, onRefresh) {
    const clearBtn = document.getElementById('clear-cache-btn');
    if (!clearBtn) return;

    clearBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear the cache? This will force all stories to be re-processed on the next load.')) {
            return;
        }

        // Disable button and show loading state
        clearBtn.disabled = true;
        clearBtn.textContent = 'Clearing...';

        try {
            const api = window.bmadApi;
            if (!api) {
                throw new Error('API client not initialized');
            }
            await api.clearCache(projectRoot);

            // Refresh dashboard
            if (onRefresh) {
                await onRefresh();
            }
        } catch (error) {
            console.error('Failed to clear cache:', error);
            alert('Failed to clear cache. See console for details.');
            clearBtn.disabled = false;
            clearBtn.textContent = 'Clear Cache';
        }
    });
}
