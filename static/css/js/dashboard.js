document.addEventListener("DOMContentLoaded", function() {
    // DOM Element Selectors
    const appModal = document.getElementById('app-modal');
    const appModalTitle = document.getElementById('modal-title');
    const openAppModalBtn = document.getElementById('open-modal-btn');
    const closeAppModalBtn = document.getElementById('close-modal-btn');
    const saveAppBtn = document.getElementById('save-app-btn');
    const appsGrid = document.getElementById('apps-grid');
    const appNameInput = document.getElementById('app-name');
    const appUrlInput = document.getElementById('app-url');
    
    const taskModal = document.getElementById('task-modal');
    const taskModalTitle = document.getElementById('task-modal-title');
    const openTaskModalBtn = document.getElementById('open-task-modal-btn');
    const closeTaskModalBtn = document.getElementById('close-task-modal-btn');
    const saveTaskBtn = document.getElementById('save-task-btn');
    const tasksTbody = document.getElementById('tasks-tbody');
    const taskNameInput = document.getElementById('task-name');
    const taskUrlInput = document.getElementById('task-url');
    const taskCategorySelect = document.getElementById('task-category');
    const taskOriginSelect = document.getElementById('task-origin');
    const taskDateInput = document.getElementById('task-date');

    const contextMenu = document.getElementById('custom-context-menu');
    const ctxUpdateBtn = document.getElementById('ctx-update-btn');
    const ctxDeleteBtn = document.getElementById('ctx-delete-btn');
    
    const filterIndicator = document.getElementById('active-filter-indicator');
    const brandHome = document.getElementById('brand-home');

    // State Variables
    let menuContextType = null;      // 'app' or 'task'
    let currentTargetIndex = null;   
    let activeFilterCategory = null; 
    let globalApps = [];
    let globalTasks = [];

    /* ==========================================
       BACKEND SERVER API NETWORKING CHECKS
       ========================================== */
    async function apiRequest(url, method = 'GET', data = null) {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (data) options.body = JSON.stringify(data);
        try {
            const response = await fetch(url, options);
            return await response.json();
        } catch (error) {
            console.error(`API Error on ${url}:`, error);
        }
    }

    async function syncData() {
        globalApps = await apiRequest('/api/apps');
        globalTasks = await apiRequest('/api/tasks');
        renderApps();
        renderTasks();
    }

    function updateSidebarBadges() {
        const counts = { courses: 0, assignments: 0, projects: 0, resources: 0 };
        globalTasks.forEach(task => { if (counts[task.category] !== undefined) counts[task.category]++; });
        Object.keys(counts).forEach(key => { document.getElementById(`badge-${key}`).textContent = counts[key]; });
    }

    /* ==========================================
       RENDERING FUNCTIONS
       ========================================== */
    function renderApps() {
        const cards = appsGrid.querySelectorAll('.icon-card:not(.add-card)');
        cards.forEach(card => card.remove());

        globalApps.forEach((app, index) => {
            const anchor = document.createElement('a');
            anchor.href = app.url;
            anchor.target = "_blank";
            anchor.rel = "noopener noreferrer";
            anchor.className = "icon-card";
            anchor.innerHTML = `<div class="icon-placeholder">${app.name.charAt(0)}</div><span>${app.name}</span>`;

            anchor.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                triggerContextMenu('app', index, e.clientX, e.clientY);
            });
            appsGrid.insertBefore(anchor, openAppModalBtn);
        });
        lucide.createIcons();
    }

    function renderTasks() {
        tasksTbody.innerHTML = '';
        const visibleTasks = activeFilterCategory ? globalTasks.filter(t => t.category === activeFilterCategory) : globalTasks;

        if (activeFilterCategory) {
            filterIndicator.innerHTML = `<span class="filter-alert" id="clear-filter-btn">${activeFilterCategory} <i data-lucide="x" size="14"></i></span>`;
            document.getElementById('clear-filter-btn').addEventListener('click', clearFilter);
        } else {
            filterIndicator.innerHTML = '';
        }

        if(visibleTasks.length === 0) {
            tasksTbody.innerHTML = `<tr><td colspan="4" class="empty-state">No active items tracked.</td></tr>`;
            lucide.createIcons();
            return;
        }

        visibleTasks.forEach((task) => {
            const trueIndex = globalTasks.indexOf(task);
            const row = document.createElement('tr');
            row.className = 'task-row';

            let readableDate = "No Deadline Set";
            if(task.date) {
                const parts = task.date.split('-');
                if(parts.length === 3) {
                    readableDate = new Date(parts[0], parts[1]-1, parts[2]).toLocaleDateString(undefined, {month: 'short', day: 'numeric', year: 'numeric'});
                }
            }

            row.innerHTML = `
                <td style="font-weight: 500; color: #0f172a;">${task.name}</td>
                <td><span class="badge badge-${task.category}">${task.category}</span></td>
                <td><span class="badge badge-origin">${task.origin}</span></td>
                <td style="color: #64748b;">${readableDate}</td>
            `;

            row.addEventListener('click', () => { if (task.url) window.open(task.url, '_blank', 'noopener,noreferrer'); });
            row.addEventListener('contextmenu', function(e) {
                e.preventDefault(); e.stopPropagation();
                triggerContextMenu('task', trueIndex, e.clientX, e.clientY);
            });
            tasksTbody.appendChild(row);
        });
        updateSidebarBadges();
        lucide.createIcons();
    }

    /* ==========================================
       SIDEBAR & INTERACTION SYSTEM CONTROLLERS
       ========================================== */
    const sidebarItems = document.querySelectorAll('.nav-item');
    sidebarItems.forEach(item => {
        item.addEventListener('click', function() {
            const selectedCategory = this.getAttribute('data-filter');
            if (this.classList.contains('active')) { clearFilter(); } 
            else {
                sidebarItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                activeFilterCategory = selectedCategory;
                renderTasks();
            }
        });
    });

    function clearFilter() {
        sidebarItems.forEach(i => i.classList.remove('active'));
        activeFilterCategory = null;
        renderTasks();
    }
    brandHome.addEventListener('click', clearFilter);

    function triggerContextMenu(type, index, clientX, clientY) {
        menuContextType = type; currentTargetIndex = index;
        contextMenu.style.top = `${clientY}px`; contextMenu.style.left = `${clientX}px`;
        contextMenu.style.display = 'block';
    }

    window.addEventListener('click', (e) => { if (!contextMenu.contains(e.target)) contextMenu.style.display = 'none'; });

    // API DELETE Execution Engine Click Call
    ctxDeleteBtn.addEventListener('click', async () => {
        if (currentTargetIndex === null) return;
        const targetUrl = menuContextType === 'app' ? '/api/apps' : '/api/tasks';
        await apiRequest(targetUrl, 'DELETE', { index: currentTargetIndex });
        contextMenu.style.display = 'none';
        syncData();
    });

    // Update Field Input Mapping Engine Click Call
    ctxUpdateBtn.addEventListener('click', () => {
        if (currentTargetIndex === null) return;
        contextMenu.style.display = 'none';

        if (menuContextType === 'app') {
            const targetApp = globalApps[currentTargetIndex];
            appModalTitle.textContent = "Update Shortcut";
            appNameInput.value = targetApp.name; appUrlInput.value = targetApp.url;
            appModal.classList.add('active');
        } else if (menuContextType === 'task') {
            const targetTask = globalTasks[currentTargetIndex];
            taskModalTitle.textContent = "Update Institutional Target";
            taskNameInput.value = targetTask.name; taskUrlInput.value = targetTask.url || '';
            taskCategorySelect.value = targetTask.category; taskOriginSelect.value = targetTask.origin;
            taskDateInput.value = targetTask.date;
            taskModal.classList.add('active');
        }
    });

    /* ==========================================
       MODAL VIEW ELEMENT TOGGLES
       ========================================== */
    openAppModalBtn.addEventListener('click', () => {
        menuContextType = null; currentTargetIndex = null;
        appModalTitle.textContent = "Add Custom Shortcut";
        appNameInput.value = ''; appUrlInput.value = '';
        appModal.classList.add('active'); appNameInput.focus();
    });
    closeAppModalBtn.addEventListener('click', () => appModal.classList.remove('active'));

    openTaskModalBtn.addEventListener('click', () => {
        menuContextType = null; currentTargetIndex = null;
        taskModalTitle.textContent = "Create Institutional Target";
        taskNameInput.value = ''; taskUrlInput.value = '';
        taskCategorySelect.value = activeFilterCategory || "courses";
        taskModal.classList.add('active'); taskNameInput.focus();
    });
    closeTaskModalBtn.addEventListener('click', () => taskModal.classList.remove('active'));

    window.addEventListener('click', (e) => {
        if (e.target === appModal) appModal.classList.remove('active');
        if (e.target === taskModal) taskModal.classList.remove('active');
    });

    /* ==========================================
       API SUBMISSION (POST/PUT) ROUTER LOGIC
       ========================================== */
    saveAppBtn.addEventListener('click', async () => {
        const name = appNameInput.value.trim(); let url = appUrlInput.value.trim();
        if (!name || !url) return alert('Fill out all input field parameters.');
        if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

        if (menuContextType === 'app' && currentTargetIndex !== null) {
            await apiRequest('/api/apps', 'PUT', { index: currentTargetIndex, app: { name, url } });
        } else {
            await apiRequest('/api/apps', 'POST', { name, url });
        }
        appModal.classList.remove('active');
        syncData();
    });

    saveTaskBtn.addEventListener('click', async () => {
        const name = taskNameInput.value.trim(); let url = taskUrlInput.value.trim();
        const category = taskCategorySelect.value; const origin = taskOriginSelect.value; const date = taskDateInput.value;
        if (!name || !date || !url) return alert('Name, track URL, and delivery timelines are required entries.');
        if (!/^https?:\/\//i.test(url)) url = 'https://' + url;

        if (menuContextType === 'task' && currentTargetIndex !== null) {
            await apiRequest('/api/tasks', 'PUT', { index: currentTargetIndex, task: { name, url, category, origin, date } });
        } else {
            await apiRequest('/api/tasks', 'POST', { name, url, category, origin, date });
        }
        taskModal.classList.remove('active');
        syncData();
    });

    // Initial Database Run
    syncData();
});