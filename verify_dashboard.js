(async () => {
    try {
        const response = await fetch('/api/dashboard?project_root=F:/BMAD Dash');
        const data = await response.json();

        console.log("--- DASHBOARD VERIFICATION ---");

        // 1. Check Story 3.2 Status
        // Story 3.2 should be in columns['done'] or its status field should be 'done'
        const findStory = (id, haystack) => {
            // Search in flat list or columns structure
            if (Array.isArray(haystack)) return haystack.find(s => s.id === id);
            if (haystack.kanban) {
                for (let k in haystack.kanban) {
                    let found = haystack.kanban[k].find(s => s.id === id);
                    if (found) return found;
                }
            }
            return null;
        };

        const story32 = findStory('3.2', data);
        if (story32) {
            console.log(`Story 3.2 Status: ${story32.status}`);
            console.log(`Story 3.2 Badge: ${story32.review_status || 'N/A'}`); // Assuming review status is passed through
        } else {
            console.log("Story 3.2 NOT FOUND");
        }

        // 2. Check Test Evidence for older stories
        const checkTests = (id) => {
            const s = findStory(id, data);
            if (s && s.evidence && s.evidence.tests) {
                console.log(`Story ${id} Tests: ${s.evidence.tests.passing}/${s.evidence.tests.total}`);
            } else if (s) {
                console.log(`Story ${id} Tests: NOT FOUND/EMPTY`);
            }
        };

        checkTests('1.1');
        checkTests('1.2');
        checkTests('1.3');
        checkTests('1.4');
        checkTests('2.1');

        return { success: true };
    } catch (e) {
        console.error(e);
        return { error: e.message };
    }
})();
