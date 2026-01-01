/**
 * Form Implementations
 * All 9 forms with their specific fields and logic
 */

// Fahrer-Daten (Driver data for forms)
const FAHRER_DATA = {
    'Gökhan Balkan': '4915122088986',
    'Denise Balkan': '4917641448898'
};

// Vehicle data for Mobi form
const VEHICLE_DATA = [
    {brand: "Volkswagen", models: ["Golf", "Passat", "Tiguan", "Polo", "T-Roc", "Touran"]},
    {brand: "Audi", models: ["A3", "A4", "A6", "Q3", "Q5", "e-tron"]},
    {brand: "Skoda", models: ["Octavia", "Fabia", "Kodiaq", "Superb", "Enyaq"]},
    {brand: "Seat", models: ["Leon", "Ibiza", "Ateca", "Arona"]},
    {brand: "Cupra", models: ["Formentor", "Born", "Leon", "Ateca"]}
];

// 1. Panne/Unfall Form
function renderPanneUnfallForm(container, form) {
    container.innerHTML = `
        <form id="panneUnfallForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Schaden</h4>
                    <div class="form-row">
                        ${createFormField('Schadensursache:', 'schadensursache', 'select', {
                            values: ['Bitte Wählen', 'Reifen', 'Motor/Antrieb', 'Elektrik/Elektronik', 'Fahrwerk/Bremse', 'Lenkung', 'Kraftstoffsystem', 'Kühlsystem/Klima', 'Abgassystem', 'Karosserie/Unfall', 'Schlüssel / Zugang', 'Sonstiges']
                        }).outerHTML}
                        ${createFormField('Schaden:', 'schaden', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Antriebsart:', 'antriebsart', 'select', {
                            values: ['Bitte Wählen', 'Diesel/Benzin', 'Gas (LPG/CNG)', 'Hybrid', 'Elektro']
                        }).outerHTML}
                        ${createFormField('Fahrzeugstand:', 'fahrzeugstand', 'select', {
                            values: ['Bitte Wählen', 'Noch rollfähig', 'Nicht mehr rollfähig']
                        }).outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Standort & Personen</h4>
                    <div class="form-row">
                        ${createFormField('Fahrzeug Standort:', 'standort', 'select', {
                            values: ['Bitte Wählen', 'Auf der Straße', 'Pannenstreifen', 'Parkplatz', 'Parkhaus', 'Tiefgarage']
                        }).outerHTML}
                        ${createFormField('Zugänglichkeit:', 'zugaenglichkeit', 'select', {
                            values: ['Bitte Wählen', 'steht freizugänglich', 'vorne nur zugänglich', 'seitlich zugänglich', 'hinten zugänglich']
                        }).outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Mitnahme von Personen:', 'personen', 'select', {
                            values: ['Bitte Wählen', '1', '2', '3', '4', '5']
                        }).outerHTML}
                        ${createFormField('Wartezeit Info:', 'wartezeit', 'select', {
                            values: ['Bitte Wählen', '15-30 Min', '30-45 Min', '45-60 Min', '60-90 Min', '90-120 Min']
                        }).outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Terminvereinbarung</h4>
                    <div class="form-row">
                        ${createFormField('Datum:', 'datum', 'text', {placeholder: 'TT.MM.JJJJ'}).outerHTML}
                        ${createFormField('Uhrzeit:', 'uhrzeit', 'text', {placeholder: 'HH:MM'}).outerHTML}
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-copy" onclick="copyPanneUnfallData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('panneUnfallForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function copyPanneUnfallData() {
    const data = getFormValues('panneUnfallForm');
    const text = `**Abklärung Panne/Unfall**

Schadensursache: ${data.schadensursache || ''}
Schaden: ${data.schaden || ''}
Antriebsart: ${data.antriebsart || ''}
Fahrzeugstand: ${data.fahrzeugstand || ''}

Standort: ${data.standort || ''}
Zugänglichkeit: ${data.zugaenglichkeit || ''}
Personen: ${data.personen || ''}
Wartezeit: ${data.wartezeit || ''}

Termin: ${data.datum || ''} um ${data.uhrzeit || ''}`;
    
    copyToClipboard(text);
}

// 2. Ölspur Form
function renderOelspurForm(container, form) {
    container.innerHTML = `
        <form id="oelspurForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Melder & Anrufer</h4>
                    <div class="form-row">
                        ${createFormField('Melder:', 'melder', 'text').outerHTML}
                        ${createFormField('Anrufer:', 'anrufer', 'text').outerHTML}
                        ${createFormField('Telefonnummer:', 'telefon', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Details der Verunreinigung</h4>
                    <div class="form-row">
                        ${createFormField('Art:', 'art', 'text').outerHTML}
                        ${createFormField('Länge:', 'laenge', 'text').outerHTML}
                        ${createFormField('Breite:', 'breite', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Einsatzort & Absicherung</h4>
                    <div class="form-row">
                        ${createFormField('Absicherung notwendig:', 'absicherung', 'select', {
                            values: ['Nein', 'Ja', 'Unklar']
                        }).outerHTML}
                        ${createFormField('Einsatzkräfte vor Ort?:', 'einsatzkraefte', 'text').outerHTML}
                        ${createFormField('Treffpunkt:', 'treffpunkt', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Zusatzinformationen</h4>
                    ${createFormField('Zusatzinformation:', 'zusatzinfo', 'textarea', {rows: 4}).outerHTML}
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-copy" onclick="copyOelspurData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('oelspurForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function copyOelspurData() {
    const data = getFormValues('oelspurForm');
    const text = `**Einsatzdetails Ölspur**

Melder: ${data.melder || ''}
Anrufer: ${data.anrufer || ''}
Telefonnummer: ${data.telefon || ''}
Art der Verunreinigung: ${data.art || ''}
Länge: ${data.laenge || ''} | Breite: ${data.breite || ''}
Absicherung vor Ort Notwendig: ${data.absicherung || ''}
Einsatzkräfte vor Ort?: ${data.einsatzkraefte || ''}
Treffpunkt: ${data.treffpunkt || ''}

**Zusatzinformation:**
${data.zusatzinfo || ''}`;
    
    copyToClipboard(text);
}

// 3. Mobi Form
function renderMobiForm(container, form) {
    container.innerHTML = `
        <form id="mobiForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Auftragsdetails</h4>
                    <div class="form-row">
                        ${createFormField('Auftraggeber:', 'auftraggeber', 'select', {
                            values: ['VW Notdienst', 'Audi Notdienst', 'Skoda Notdienst', 'Seat Notdienst', 'Cupra Notdienst']
                        }).outerHTML}
                        ${createFormField('Vorgangsnummer:', 'vorgangsnummer', 'text').outerHTML}
                        ${createFormField('Anrufername:', 'anrufername', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Fahrzeugdetails</h4>
                    <div class="form-row">
                        ${createFormField('Fahrzeug:', 'fahrzeug', 'select', {
                            values: ['', ...VEHICLE_DATA.map(v => v.brand)]
                        }).outerHTML}
                        ${createFormField('Modell:', 'modell', 'text').outerHTML}
                        ${createFormField('Kennzeichen:', 'kennzeichen', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Fahrgestellnummer:', 'fin', 'text').outerHTML}
                        ${createFormField('Erstzulassung:', 'erstzulassung', 'text').outerHTML}
                        ${createFormField('KM-Stand:', 'kmstand', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Schaden:', 'schaden', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Kundendetails</h4>
                    <div class="form-row">
                        ${createFormField('Kunde vor Ort:', 'kunde', 'text').outerHTML}
                        ${createFormField('Telefonnummer:', 'telefon', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Ortsdetails</h4>
                    <div class="form-row">
                        ${createFormField('Pannenort:', 'pannenort', 'text').outerHTML}
                        ${createFormField('Verbringungsort (Autohaus):', 'verbringungsort', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Zusatzleistungen</h4>
                    <div class="form-row">
                        ${createFormField('Kunde braucht ein Ersatzfahrzeug?:', 'ersatzfahrzeug', 'select', {
                            values: ['Nein', 'Ja']
                        }).outerHTML}
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-primary" style="background: var(--color-red);" onclick="copySafarInfo()">Info (Safar)</button>
                <button type="button" class="btn btn-copy" onclick="copyMobiData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('mobiForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function copySafarInfo() {
    const text = `Mobilitätsgarantie:

* Anrufer:
* Mobi vor Ort Prüfen!!
* FOTO VOM FAHRZEUGSCHEIN MACHEN (LESERLICH)!
* FOTOS VOM FAHRZEUG
* FOTO VON DER LETZTEN INSPEKTION MACHEN!
* FOTO VON DER NÄCHSTEN INSPEKTION MACHEN!
* FOTO VOM KM-STAND MACHEN!
* FOTO VOM MOBI ZETTEL MACHEN!
* FOTO VON DER FIN MACHEN!

Auftrag kam für folgendes Autohaus:


Info an den Fahrer:
* BEI EINER LEERFAHRT BITTE DEN GRUND IM INFO-FELD EINTRAGEN !`;
    
    copyToClipboard(text);
}

function copyMobiData() {
    const data = getFormValues('mobiForm');
    const text = `Auftraggeber: ${data.auftraggeber || ''}
Vorgangsnummer: ${data.vorgangsnummer || ''}
Anrufername: ${data.anrufername || ''}

Fahrzeug: ${data.fahrzeug || ''}
Modell: ${data.modell || ''}
Kennzeichen: ${data.kennzeichen || ''}
Fahrgestellnummer: ${data.fin || ''}
Erstzulassung: ${data.erstzulassung || ''}
KM-Stand: ${data.kmstand || ''}
Schaden: ${data.schaden || ''}

Kunde vor Ort: ${data.kunde || ''}
Telefonnummer: ${data.telefon || ''}

Pannenort: ${data.pannenort || ''}
Verbringungsort (Autohaus): ${data.verbringungsort || ''}

Kunde braucht ein Ersatzfahrzeug?: ${data.ersatzfahrzeug || ''}`;
    
    copyToClipboard(text);
}

// 4. Kilian Form (PKW/GDV/LKW)
function renderKilianForm(container, form) {
    container.innerHTML = `
        <form id="kilianForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Annahme PKW</h4>
                    <div class="form-row">
                        ${createFormField('Auftraggeber:', 'pkw_auftraggeber', 'select', {
                            values: ['Bitte Wählen', 'Polizei', 'Privater Selbstzahler', 'ADAC', 'VW', 'Audi']
                        }).outerHTML}
                        ${createFormField('Auftragsart:', 'pkw_auftragsart', 'select', {
                            values: ['Panne', 'Unfall', 'Sicherstellung']
                        }).outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Anrufer:', 'pkw_anrufer', 'text').outerHTML}
                        ${createFormField('Kunde vor Ort:', 'pkw_kunde', 'text').outerHTML}
                        ${createFormField('Telefonnummer:', 'pkw_telefon', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Fahrzeug:', 'pkw_fahrzeug', 'text').outerHTML}
                        ${createFormField('Modell:', 'pkw_modell', 'text').outerHTML}
                        ${createFormField('Kennzeichen:', 'pkw_kennzeichen', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Schaden:', 'pkw_schaden', 'text').outerHTML}
                        ${createFormField('Pannen-/Unfallort:', 'pkw_ort', 'text').outerHTML}
                        ${createFormField('Verbringungsort:', 'pkw_verbringung', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Annahme GDV</h4>
                    <div class="form-row">
                        <div class="form-field">
                            <label>Fahrzeugtyp:</label>
                            <select name="gdv_typ" id="gdv_typ" onchange="toggleGDVFields()">
                                <option value="PKW">PKW</option>
                                <option value="LKW">LKW</option>
                            </select>
                        </div>
                        ${createFormField('Vorgangsnummer:', 'gdv_vorgangsnummer', 'text').outerHTML}
                        ${createFormField('Auftragsart:', 'gdv_auftragsart', 'select', {
                            values: ['Panne', 'Unfall', 'Sicherstellung']
                        }).outerHTML}
                    </div>
                    <div id="gdv_pkw_fields">
                        <div class="form-row">
                            ${createFormField('Fahrzeug:', 'gdv_fahrzeug', 'text').outerHTML}
                            ${createFormField('Kennzeichen:', 'gdv_kennzeichen', 'text').outerHTML}
                            ${createFormField('Mit Kran:', 'gdv_kran', 'select', {values: ['Nein', 'Ja']}).outerHTML}
                        </div>
                    </div>
                    <div id="gdv_lkw_fields" style="display: none;">
                        <div class="form-row">
                            ${createFormField('Zugmaschine:', 'gdv_zugmaschine', 'text').outerHTML}
                            ${createFormField('Auflieger:', 'gdv_auflieger', 'text').outerHTML}
                            ${createFormField('Kennzeichen:', 'gdv_lkw_kennzeichen', 'text').outerHTML}
                        </div>
                    </div>
                    <div class="form-row">
                        ${createFormField('Einsatzort:', 'gdv_einsatzort', 'text').outerHTML}
                    </div>
                </div>

                <div class="form-section">
                    <h4 style="color: ${form.color}">Fahrer</h4>
                    <div class="form-row">
                        ${createFormField('Fahrer:', 'fahrer', 'select', {
                            values: ['Bitte Wählen', ...Object.keys(FAHRER_DATA)]
                        }).outerHTML}
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-whatsapp" onclick="sendKilianWhatsApp()">Per WhatsApp versenden</button>
                <button type="button" class="btn btn-copy" onclick="copyKilianData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('kilianForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function toggleGDVFields() {
    const typ = document.getElementById('gdv_typ').value;
    const pkwFields = document.getElementById('gdv_pkw_fields');
    const lkwFields = document.getElementById('gdv_lkw_fields');
    
    if (typ === 'PKW') {
        pkwFields.style.display = 'block';
        lkwFields.style.display = 'none';
    } else {
        pkwFields.style.display = 'none';
        lkwFields.style.display = 'block';
    }
}

function copyKilianData() {
    const data = getFormValues('kilianForm');
    let text = `**Annahme Panne | Unfall (PKW)**
Auftraggeber: ${data.pkw_auftraggeber || ''}
Auftragsart: ${data.pkw_auftragsart || ''}
Anrufer: ${data.pkw_anrufer || ''}
Kunde vor Ort: ${data.pkw_kunde || ''}
Telefonnummer: ${data.pkw_telefon || ''}
Fahrzeug: ${data.pkw_fahrzeug || ''}
Modell: ${data.pkw_modell || ''}
Kennzeichen: ${data.pkw_kennzeichen || ''}
Schaden: ${data.pkw_schaden || ''}
Pannen-/Unfallort: ${data.pkw_ort || ''}
Verbringungsort: ${data.pkw_verbringung || ''}

**Annahme GDV**
Fahrzeugtyp: ${data.gdv_typ || 'PKW'}
Vorgangsnummer: ${data.gdv_vorgangsnummer || ''}
Auftragsart: ${data.gdv_auftragsart || ''}`;

    if (data.gdv_typ === 'LKW') {
        text += `
Zugmaschine: ${data.gdv_zugmaschine || ''}
Auflieger: ${data.gdv_auflieger || ''}
Kennzeichen: ${data.gdv_lkw_kennzeichen || ''}`;
    } else {
        text += `
Fahrzeug: ${data.gdv_fahrzeug || ''}
Kennzeichen: ${data.gdv_kennzeichen || ''}
Mit Kran: ${data.gdv_kran || ''}`;
    }

    text += `
Einsatzort: ${data.gdv_einsatzort || ''}`;
    
    copyToClipboard(text);
}

function sendKilianWhatsApp() {
    const data = getFormValues('kilianForm');
    const fahrer = data.fahrer;
    const phone = FAHRER_DATA[fahrer];
    const message = copyKilianData;
    sendWhatsApp(phone, message);
}

// 5. Rudolph Form
function renderRudolphForm(container, form) {
    container.innerHTML = `
        <form id="rudolphForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Auftragsdetails</h4>
                    <div class="form-row">
                        ${createFormField('Auftraggeber:', 'auftraggeber', 'select', {
                            values: ['FUBZ', 'BVG']
                        }).outerHTML}
                        ${createFormField('Auftragsart:', 'auftragsart', 'select', {
                            values: ['Umsetzung', 'Sicherstellung']
                        }).outerHTML}
                        ${createFormField('Vorgangsnummer:', 'vorgangsnummer', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Fahrzeug:', 'fahrzeug', 'text').outerHTML}
                        ${createFormField('Kennzeichen:', 'kennzeichen', 'text').outerHTML}
                        ${createFormField('Standort:', 'standort', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Verbringungsort:', 'verbringungsort', 'text').outerHTML}
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-copy" onclick="copyRudolphData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('rudolphForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function copyRudolphData() {
    const data = getFormValues('rudolphForm');
    const text = `**Annahme Rudolph**

Auftraggeber: ${data.auftraggeber || ''}
Auftragsart: ${data.auftragsart || ''}
Vorgangsnummer: ${data.vorgangsnummer || ''}
Fahrzeug: ${data.fahrzeug || ''}
Kennzeichen: ${data.kennzeichen || ''}
Standort: ${data.standort || ''}
Verbringungsort: ${data.verbringungsort || ''}`;
    
    copyToClipboard(text);
}

// 6. Wehner Motors Form
function renderWehnerForm(container, form) {
    container.innerHTML = `
        <form id="wehnerForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Auftragsdetails</h4>
                    <div class="form-row">
                        ${createFormField('Auftragsart:', 'auftragsart', 'select', {
                            values: ['Bitte Wählen', 'PKW Panne', 'PKW Unfall', 'Polizei', 'LKW', 'Ölspur']
                        }).outerHTML}
                        ${createFormField('Anrufer:', 'anrufer', 'text').outerHTML}
                        ${createFormField('Telefonnummer:', 'telefon', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Fahrzeug:', 'fahrzeug', 'text').outerHTML}
                        ${createFormField('Kennzeichen:', 'kennzeichen', 'text').outerHTML}
                        ${createFormField('Standort:', 'standort', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Verbringungsort:', 'verbringungsort', 'text').outerHTML}
                        ${createFormField('Schaden:', 'schaden', 'text').outerHTML}
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-copy" onclick="copyWehnerData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('wehnerForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function copyWehnerData() {
    const data = getFormValues('wehnerForm');
    const text = `**Annahme Wehner Motors**

Auftragsart: ${data.auftragsart || ''}
Anrufer: ${data.anrufer || ''}
Telefonnummer: ${data.telefon || ''}
Fahrzeug: ${data.fahrzeug || ''}
Kennzeichen: ${data.kennzeichen || ''}
Standort: ${data.standort || ''}
Verbringungsort: ${data.verbringungsort || ''}
Schaden: ${data.schaden || ''}`;
    
    copyToClipboard(text);
}

// 7. Falschparker Form
function renderFalschparkerForm(container, form) {
    const abschleppgruende = [
        "steht auf dem angemieteten Stellplatz",
        "steht in der Feuerwehrzufahrt",
        "steht in der Einfahrt",
        "blockiert die Zufahrt",
        "steht im Halteverbot",
        "ohne gültigen Parkausweis",
        "parkt auf Behindertenparkplatz",
        "parkt auf Frauenparkplatz",
        "parkt auf Eltern-Kind-Parkplatz"
    ];

    container.innerHTML = `
        <form id="falschparkerForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Details zum Falschparker</h4>
                    <div class="form-row">
                        ${createFormField('Anrufer:', 'anrufer', 'text').outerHTML}
                        ${createFormField('Telefonnummer:', 'telefon', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Fahrzeug:', 'fahrzeug', 'text').outerHTML}
                        ${createFormField('Modell:', 'modell', 'text').outerHTML}
                        ${createFormField('Kennzeichen:', 'kennzeichen', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Einsatzort:', 'einsatzort', 'text').outerHTML}
                        ${createFormField('Stellplatz:', 'stellplatz', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Abschleppgrund:', 'abschleppgrund', 'select', {
                            values: ['Bitte Wählen', ...abschleppgruende]
                        }).outerHTML}
                        ${createFormField('Fahrer:', 'fahrer', 'select', {
                            values: ['Bitte Wählen', ...Object.keys(FAHRER_DATA)]
                        }).outerHTML}
                    </div>
                    <div class="form-row">
                        <div class="form-field">
                            <label>
                                <input type="checkbox" name="abtretung" id="abtretung"> Abtretung notwendig
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-whatsapp" onclick="sendFalschparkerWhatsApp()">Per WhatsApp versenden</button>
                <button type="button" class="btn btn-copy" onclick="copyFalschparkerData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('falschparkerForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function copyFalschparkerData() {
    const data = getFormValues('falschparkerForm');
    const text = `**Annahme Falschparker | Privat**

Anrufer: ${data.anrufer || ''}
Telefonnummer: ${data.telefon || ''}
Fahrzeug: ${data.fahrzeug || ''}
Modell: ${data.modell || ''}
Kennzeichen: ${data.kennzeichen || ''}
Abschleppgrund: ${data.abschleppgrund || ''}
Einsatzort: ${data.einsatzort || ''}
Stellplatz: ${data.stellplatz || ''}
${data.abtretung ? 'Abtretung notwendig: Ja' : ''}`;
    
    copyToClipboard(text);
}

function sendFalschparkerWhatsApp() {
    const data = getFormValues('falschparkerForm');
    const fahrer = data.fahrer;
    const phone = FAHRER_DATA[fahrer];
    
    if (!phone) {
        showToast('Bitte zuerst einen Fahrer auswählen', 'error');
        return;
    }
    
    const text = copyFalschparkerData();
    sendWhatsApp(phone, text);
}

// 8. Unterhaslberger Form
function renderUnterhaslbergerForm(container, form) {
    container.innerHTML = `
        <form id="unterhaslbergerForm">
            <div class="form-body">
                <div class="form-section">
                    <h4 style="color: ${form.color}">Auftragsdetails</h4>
                    <div class="form-row">
                        ${createFormField('Auftragsart:', 'auftragsart', 'select', {
                            values: ['Bitte Wählen', 'Panne', 'Unfall', 'Sicherstellung']
                        }).outerHTML}
                        ${createFormField('Anrufer:', 'anrufer', 'text').outerHTML}
                        ${createFormField('Telefonnummer:', 'telefon', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Fahrzeug:', 'fahrzeug', 'text').outerHTML}
                        ${createFormField('Kennzeichen:', 'kennzeichen', 'text').outerHTML}
                        ${createFormField('Standort:', 'standort', 'text').outerHTML}
                    </div>
                    <div class="form-row">
                        ${createFormField('Verbringungsort:', 'verbringungsort', 'text').outerHTML}
                        ${createFormField('Schaden:', 'schaden', 'text').outerHTML}
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-copy" onclick="copyUnterhaslbergerData()">Kopieren</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('unterhaslbergerForm')">Zurücksetzen</button>
            </div>
        </form>
    `;
}

function copyUnterhaslbergerData() {
    const data = getFormValues('unterhaslbergerForm');
    const text = `**Annahme Unterhaslberger**

Auftragsart: ${data.auftragsart || ''}
Anrufer: ${data.anrufer || ''}
Telefonnummer: ${data.telefon || ''}
Fahrzeug: ${data.fahrzeug || ''}
Kennzeichen: ${data.kennzeichen || ''}
Standort: ${data.standort || ''}
Verbringungsort: ${data.verbringungsort || ''}
Schaden: ${data.schaden || ''}`;
    
    copyToClipboard(text);
}

// 9. Safar & BHG Report Form
function renderSafarBHGForm(container, form) {
    const wartezeitOptions = ['Bitte wählen', '30 - 60 Minuten', '60 - 90 Minuten', '90 - 120 Minuten', '2 - 3 Stunden', '3 - 4 Stunden', '5 - 6 Stunden', 'Keine Wartezeit'];
    const wartezeiten = ['16:00 – 18:00 Uhr', '18:00 – 20:00 Uhr', '20:00 – 21:00 Uhr', '21:00 – 23:00 Uhr', 'Ab 23 Uhr'];

    container.innerHTML = `
        <form id="safarBHGForm">
            <div class="form-body" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <div class="form-section">
                        <h4 style="color: ${form.color}">Report Safar</h4>
                        <div class="form-row" style="grid-template-columns: 1fr;">
                            ${createFormField('Offene Aufträge bei der Übergabe:', 'safar_offene', 'text').outerHTML}
                            ${createFormField('Auftragslage bei der Übergabe:', 'safar_lage', 'select', {
                                values: ['Geringes Auftragsvolumen', 'Moderates Auftragsvolumen', 'Hohes Auftragsvolumen']
                            }).outerHTML}
                        </div>
                        
                        <h5 style="margin-top: 20px; margin-bottom: 10px;">Durchschnittliche Wartezeiten</h5>
                        ${wartezeiten.map((zeit, i) => 
                            createFormField(zeit + ':', `safar_wartezeit_${i}`, 'select', {
                                values: wartezeitOptions
                            }).outerHTML
                        ).join('')}
                        
                        <h5 style="margin-top: 20px; margin-bottom: 10px;">Fahrer, Aufträge & Verhalten</h5>
                        ${createFormField('Fahrerplanung:', 'safar_fahrerplanung', 'select', {
                            values: ['Unterbesetzung / Kritisch', 'Ausreichende Besetzung', 'Gute Besetzung', 'Optimale Besetzung']
                        }).outerHTML}
                        ${createFormField('Anzahl der Mobi Aufträge:', 'safar_mobi', 'select', {
                            values: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
                        }).outerHTML}
                        ${createFormField('Anzahl der Ölspuren:', 'safar_oelspur', 'select', {
                            values: ['0', '1', '2', '3', '4', '5', '6']
                        }).outerHTML}
                        ${createFormField('Anzahl der Unfälle:', 'safar_unfaelle', 'select', {
                            values: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
                        }).outerHTML}
                    </div>
                </div>

                <div>
                    <div class="form-section">
                        <h4 style="color: ${form.color}">Report Bad Homburg</h4>
                        <div class="form-row" style="grid-template-columns: 1fr;">
                            ${createFormField('Offene Aufträge bei der Übergabe:', 'bhg_offene', 'text').outerHTML}
                            ${createFormField('Auftragslage bei der Übergabe:', 'bhg_lage', 'select', {
                                values: ['Geringes Auftragsvolumen', 'Normales Auftragsvolumen', 'Hohes Auftragsvolumen', 'Sehr hohes Auftragsvolumen']
                            }).outerHTML}
                            ${createFormField('Fahrerplanung:', 'bhg_fahrerplanung', 'select', {
                                values: ['Unterbesetzung / Kritisch', 'Unterbesetzung', 'Bedarfsgerecht', 'Überbesetzung']
                            }).outerHTML}
                        </div>
                        
                        <h5 style="margin-top: 20px; margin-bottom: 10px;">AP Wartezeit ab 16:00 Uhr</h5>
                        ${wartezeiten.map((zeit, i) => 
                            createFormField(zeit + ':', `bhg_wartezeit_${i}`, 'select', {
                                values: wartezeitOptions
                            }).outerHTML
                        ).join('')}
                        
                        <h5 style="margin-top: 20px; margin-bottom: 10px;">Abgesagte Aufträge</h5>
                        ${createFormField('Abgesagte Aufträge:', 'bhg_abgesagt', 'select', {
                            values: ['Nein', 'Ja']
                        }).outerHTML}
                        <div id="bhg_abgesagt_fields" style="display: none;">
                            ${createFormField('ID:', 'bhg_id', 'text').outerHTML}
                            ${createFormField('Grund:', 'bhg_grund', 'text').outerHTML}
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-copy" onclick="copySafarData()">Kopieren (Safar)</button>
                <button type="button" class="btn btn-copy" onclick="copyBHGData()">Kopieren (BHG)</button>
                <button type="button" class="btn btn-reset" onclick="resetForm('safarBHGForm')">Zurücksetzen</button>
            </div>
        </form>
    `;

    // Add event listener for abgesagt toggle
    const abgesagtSelect = document.getElementById('bhg_abgesagt');
    if (abgesagtSelect) {
        abgesagtSelect.addEventListener('change', function() {
            const fields = document.getElementById('bhg_abgesagt_fields');
            fields.style.display = this.value === 'Ja' ? 'block' : 'none';
        });
    }
}

function copySafarData() {
    const data = getFormValues('safarBHGForm');
    const wartezeiten = ['16:00 – 18:00 Uhr', '18:00 – 20:00 Uhr', '20:00 – 21:00 Uhr', '21:00 – 23:00 Uhr', 'Ab 23 Uhr'];
    
    let text = `**Report Safar**

Offene Aufträge bei der Übergabe: ${data.safar_offene || ''}
Auftragslage bei der Übergabe: ${data.safar_lage || ''}

**Durchschnittliche Wartezeiten (ADAC / Sonstige):**`;
    
    wartezeiten.forEach((zeit, i) => {
        const wert = data[`safar_wartezeit_${i}`];
        if (wert && wert !== 'Bitte wählen') {
            text += `\n${zeit}: ${wert}`;
        }
    });
    
    text += `

**Fahrer, Aufträge & Verhalten:**
Fahrerplanung: ${data.safar_fahrerplanung || ''}
Anzahl der Mobi Aufträge: ${data.safar_mobi || ''}
Anzahl der Ölspuren: ${data.safar_oelspur || ''}
Anzahl der Unfälle: ${data.safar_unfaelle || ''}

**Fahrerverhalten:**
Alle Fahrer haben ihre Aufträge zügig angenommen und sind zeitnah losgefahren.`;
    
    copyToClipboard(text);
}

function copyBHGData() {
    const data = getFormValues('safarBHGForm');
    const wartezeiten = ['16:00 – 18:00 Uhr', '18:00 – 20:00 Uhr', '20:00 – 21:00 Uhr', '21:00 – 23:00 Uhr', 'Ab 23 Uhr'];
    
    let text = `**Report Bad Homburg**

Offene Aufträge bei der Übergabe: ${data.bhg_offene || ''}
Auftragslage bei der Übergabe: ${data.bhg_lage || ''}
Fahrerplanung: ${data.bhg_fahrerplanung || ''}

**AP Wartezeit ab 16:00 Uhr:**`;
    
    wartezeiten.forEach((zeit, i) => {
        const wert = data[`bhg_wartezeit_${i}`];
        if (wert && wert !== 'Bitte wählen') {
            text += `\n${zeit}: ${wert}`;
        }
    });
    
    text += `

**Abgesagte Aufträge:**
Abgesagte Aufträge: ${data.bhg_abgesagt || ''}`;
    
    if (data.bhg_abgesagt === 'Ja') {
        text += `
ID: ${data.bhg_id || ''}
Grund: ${data.bhg_grund || ''}`;
    }
    
    copyToClipboard(text);
}
