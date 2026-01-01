/**
 * Client-side Router
 * Handles URL routing for the SPA
 */

// Route configuration
const routes = {
    '/dashboard': { formId: null, title: 'Dashboard' },
    '/abklaerung': { formId: 'panne-unfall', title: 'Abklärung Panne/Unfall' },
    '/oelspur': { formId: 'oelspur', title: 'Annahme Ölspur' },
    '/mobi': { formId: 'mobi', title: 'Annahme Mobi' },
    '/kilian': { formId: 'kilian', title: 'Annahme Kilian' },
    '/rudolph': { formId: 'rudolph', title: 'Annahme Rudolph' },
    '/wehner': { formId: 'wehner', title: 'Annahme Wehner Motors' },
    '/falschparker': { formId: 'falschparker', title: 'Falschparker Privat' },
    '/unterhaslberger': { formId: 'unterhaslberger', title: 'Annahme Unterhaslberger' },
    '/safar-bhg': { formId: 'safar-bhg', title: 'Report Safar & BHG' }
};

// Form ID to route mapping
const formIdToRoute = {
    'panne-unfall': '/abklaerung',
    'oelspur': '/oelspur',
    'mobi': '/mobi',
    'kilian': '/kilian',
    'rudolph': '/rudolph',
    'wehner': '/wehner',
    'falschparker': '/falschparker',
    'unterhaslberger': '/unterhaslberger',
    'safar-bhg': '/safar-bhg'
};

// Store forms data globally
let formsData = [];

/**
 * Initialize the router
 */
function initRouter() {
    // Handle browser back/forward buttons
    window.addEventListener('popstate', handleRouteChange);
    
    // Handle initial route
    handleRouteChange();
}

/**
 * Navigate to a specific route
 */
function navigateTo(path) {
    if (window.location.pathname !== path) {
        window.history.pushState({}, '', path);
        handleRouteChange();
    }
}

/**
 * Handle route changes
 */
function handleRouteChange() {
    const path = window.location.pathname;
    const route = routes[path];
    
    // Close sidebar on mobile after navigation
    if (window.innerWidth <= 768) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }
    
    if (route) {
        if (route.formId) {
            // Load specific form
            const form = formsData.find(f => f.id === route.formId);
            if (form) {
                loadFormContent(form);
                setActiveNavByFormId(route.formId);
            }
        } else {
            // Load dashboard welcome screen
            loadDashboardWelcome();
            clearActiveNav();
        }
        document.title = `${route.title} - NightDUTY Abfragetool`;
    } else {
        // Unknown route - redirect to dashboard
        navigateTo('/dashboard');
    }
}

/**
 * Load dashboard welcome screen
 */
function loadDashboardWelcome() {
    const mainContent = document.getElementById('mainContentArea');
    if (!mainContent) return;
    
    mainContent.innerHTML = `
        <div class="content-header">
            <h2>Willkommen</h2>
            <p>im NightDUTY Abfragetool. Effizient. Strukturiert. Professionell.</p>
        </div>

        <div class="content-body">
            <div class="welcome-screen">
                <div class="welcome-content">
                    <div class="quick-access-panel">
                        <h3>Quick Access</h3>
                        
                        <div class="access-item">
                            <div class="icon">🔧</div>
                            <div class="access-item-text">
                                <h4>Abklärung Panne/Unfall</h4>
                                <p>Geführte Erfassung aller relevanten Details.</p>
                            </div>
                        </div>

                        <div class="access-item">
                            <div class="icon">💧</div>
                            <div class="access-item-text">
                                <h4>Annahme Ölspur</h4>
                                <p>Erfassung von Ölspuren und Umwelteinsätzen.</p>
                            </div>
                        </div>

                        <div class="access-item">
                            <div class="icon">📱</div>
                            <div class="access-item-text">
                                <h4>Annahme Mobi</h4>
                                <p>Schnelle Bearbeitung von Mobilitätsfällen.</p>
                            </div>
                        </div>
                    </div>

                    <div class="quick-access-panel">
                        <h3>Weitere Funktionen</h3>
                        
                        <div class="access-item">
                            <div class="icon">🚛</div>
                            <div class="access-item-text">
                                <h4>Annahme Kilian</h4>
                                <p>Aufträge für die Polizei, GDV und Bus/LKW.</p>
                            </div>
                        </div>

                        <div class="access-item">
                            <div class="icon">🅿️</div>
                            <div class="access-item-text">
                                <h4>Falschparker</h4>
                                <p>Private Falschparker-Meldungen.</p>
                            </div>
                        </div>

                        <div class="access-item">
                            <div class="icon">📊</div>
                            <div class="access-item-text">
                                <h4>Reports</h4>
                                <p>Tägliche Reports für Safar und Bad Homburg.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Set active navigation by form ID
 */
function setActiveNavByFormId(formId) {
    const buttons = document.querySelectorAll('.nav-button');
    buttons.forEach(btn => {
        if (btn.getAttribute('data-form-id') === formId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

/**
 * Clear all active navigation
 */
function clearActiveNav() {
    const buttons = document.querySelectorAll('.nav-button');
    buttons.forEach(btn => btn.classList.remove('active'));
}

/**
 * Get route for form ID
 */
function getRouteForFormId(formId) {
    return formIdToRoute[formId] || '/dashboard';
}
