/**
 * Main Application Logic
 * Handles navigation, form loading, and UI interactions
 */

// Load forms from API
async function loadForms() {
    try {
        const response = await apiRequest('/api/forms/types');
        const data = await response.json();
        
        renderNavigation(data.forms);
    } catch (error) {
        console.error('Failed to load forms:', error);
        showToast('Fehler beim Laden der Formulare', 'error');
    }
}

// Render navigation buttons
function renderNavigation(forms) {
    const nav = document.getElementById('sidebarNav');
    if (!nav) return;

    nav.innerHTML = '';

    forms.forEach(form => {
        const button = document.createElement('button');
        button.className = 'nav-button';
        button.setAttribute('data-form-id', form.id);
        button.style.background = form.color;
        
        // Adjust text color for yellow background
        if (form.color === '#FFC107') {
            button.style.color = '#1c1c1c';
        }

        button.innerHTML = `
            <span class="icon">${form.icon}</span>
            <span>${form.name}</span>
        `;

        button.addEventListener('click', () => {
            loadFormContent(form);
            setActiveNav(button);
        });

        nav.appendChild(button);
    });
}

// Set active navigation button
function setActiveNav(activeButton) {
    const buttons = document.querySelectorAll('.nav-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    activeButton.classList.add('active');
}

// Load form content
function loadFormContent(form) {
    const mainContent = document.getElementById('mainContentArea');
    
    mainContent.innerHTML = `
        <div class="content-header" style="background: ${form.color};">
            <h2>${form.icon} ${form.name}</h2>
            <p>${form.description}</p>
        </div>
        <div class="content-body">
            <div class="form-container" id="formContent">
                <!-- Form will be rendered here -->
            </div>
        </div>
    `;

    // Adjust header text color for yellow
    const header = mainContent.querySelector('.content-header');
    if (form.color === '#FFC107') {
        header.style.color = '#1c1c1c';
    }

    // Render the specific form
    renderForm(form);
}

// Render specific form based on form type
function renderForm(form) {
    const formContent = document.getElementById('formContent');
    
    switch(form.id) {
        case 'panne-unfall':
            renderPanneUnfallForm(formContent, form);
            break;
        case 'oelspur':
            renderOelspurForm(formContent, form);
            break;
        case 'mobi':
            renderMobiForm(formContent, form);
            break;
        case 'kilian':
            renderKilianForm(formContent, form);
            break;
        case 'rudolph':
            renderRudolphForm(formContent, form);
            break;
        case 'wehner':
            renderWehnerForm(formContent, form);
            break;
        case 'falschparker':
            renderFalschparkerForm(formContent, form);
            break;
        case 'unterhaslberger':
            renderUnterhaslbergerForm(formContent, form);
            break;
        case 'safar-bhg':
            renderSafarBHGForm(formContent, form);
            break;
        default:
            formContent.innerHTML = '<p>Formular wird geladen...</p>';
    }
}

// Copy text to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Text wurde kopiert!', 'success');
        }).catch(err => {
            console.error('Clipboard write failed:', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

// Fallback for older browsers
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '-999999px';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Text wurde kopiert!', 'success');
    } catch (err) {
        console.error('Fallback copy failed:', err);
        showToast('Kopieren fehlgeschlagen', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Send WhatsApp message
function sendWhatsApp(phoneNumber, message) {
    if (!phoneNumber) {
        showToast('Bitte zuerst einen Fahrer auswählen', 'error');
        return;
    }
    
    const encodedMessage = encodeURIComponent(message);
    const url = `https://wa.me/${phoneNumber}?text=${encodedMessage}`;
    window.open(url, '_blank');
    showToast('WhatsApp wird geöffnet...', 'success');
}

// Get form values
function getFormValues(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    
    const formData = {};
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        const name = input.name || input.id;
        if (name) {
            if (input.type === 'checkbox') {
                formData[name] = input.checked;
            } else {
                formData[name] = input.value;
            }
        }
    });
    
    return formData;
}

// Reset form
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            input.checked = false;
        } else if (input.tagName === 'SELECT') {
            input.selectedIndex = 0;
        } else {
            input.value = '';
        }
    });
    
    showToast('Formular zurückgesetzt', 'success');
}

// Create form field helper
function createFormField(label, name, type = 'text', options = {}) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'form-field';
    
    const labelEl = document.createElement('label');
    labelEl.textContent = label;
    labelEl.setAttribute('for', name);
    fieldDiv.appendChild(labelEl);
    
    let input;
    
    if (type === 'select') {
        input = document.createElement('select');
        input.name = name;
        input.id = name;
        
        if (options.values) {
            options.values.forEach(value => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = value;
                input.appendChild(option);
            });
        }
    } else if (type === 'textarea') {
        input = document.createElement('textarea');
        input.name = name;
        input.id = name;
        if (options.rows) input.rows = options.rows;
    } else {
        input = document.createElement('input');
        input.type = type;
        input.name = name;
        input.id = name;
        if (options.placeholder) input.placeholder = options.placeholder;
    }
    
    if (options.required) input.required = true;
    
    fieldDiv.appendChild(input);
    return fieldDiv;
}
