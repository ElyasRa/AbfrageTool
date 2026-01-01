import customtkinter
import tkinter
from tkinter import filedialog, simpledialog
from datetime import datetime
import locale
from PIL import Image, UnidentifiedImageError, ImageFont, ImageDraw
import json
import webbrowser
from urllib.parse import quote
import sys
import os

# --- Farbpalette ---
COLOR_RED = "#D32F2F"
COLOR_HOVER_RED = "#a12525"
COLOR_BLUE = "#1976D2"
COLOR_HOVER_BLUE = "#1565C0"
COLOR_YELLOW = "#FFC107"
COLOR_HOVER_YELLOW = "#E0B000"
COLOR_GREEN = "#388E3C"
COLOR_HOVER_GREEN = "#2E7D32" 
COLOR_PURPLE = "#7B1FA2"
COLOR_HOVER_PURPLE = "#6A1B9A"
COLOR_ORANGE = "#F57C00"
COLOR_HOVER_ORANGE = "#E65100"
COLOR_TEAL = "#009688"
COLOR_HOVER_TEAL = "#00796B"
COLOR_DARK_GREY = "#2b2b2b"
COLOR_MEDIUM_GREY = "#333333"
COLOR_LIGHT_GREY = "#4F4F4F"
COLOR_BLACK = "#1c1c1c"


def resource_path(relative_path):
    """ Ermittelt den absoluten Pfad zu einer Ressource, funktioniert für Entwicklung und PyInstaller """
    try:
        # PyInstaller erstellt einen temporären Ordner und speichert den Pfad in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Funktion zum Erstellen eines Bildes aus einem Emoji
def create_emoji_image(emoji, size, text_color="white"):
    try:
        # Versuche, eine Schriftart zu laden, die Emojis unterstützt
        try:
            font = ImageFont.truetype("seguiemj.ttf", size)
        except IOError:
            # Fallback für Systeme ohne Segoe UI Emoji (z.B. macOS, Linux)
            try:
                font = ImageFont.truetype("AppleColorEmoji.ttf", size)
            except IOError:
                # Generischer Fallback
                font = ImageFont.truetype("arial.ttf", size)
    except IOError:
        # Wenn keine Schriftart gefunden wird, ein leeres Bild zurückgeben
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # Erstelle ein Bild mit transparentem Hintergrund
    image = Image.new("RGBA", (size + 5, size + 5), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Zeichne das Emoji auf das Bild
    draw.text((0, -2), emoji, font=font, fill=text_color, embedded_color=True)
    
    return image


# Setzt die Sprache auf Deutsch für die Datumsanzeige (Wochentag, Monat)
try:
    locale.setlocale(locale.LC_TIME, 'de_DE')
except locale.Error:
    print("Deutsches Sprachpaket nicht gefunden, verwende Standard.")

class PasswordDialog(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Passwort erforderlich")
        self.geometry("400x200")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BLACK)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.lift()
        self.focus_force()
        self.grab_set()

        self._result = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = customtkinter.CTkFrame(self, fg_color=COLOR_DARK_GREY, corner_radius=10)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)
        # Removed rowconfigure to let pack manage the layout vertically

        customtkinter.CTkLabel(main_frame, text="Bitte geben Sie das Passwort ein:", font=("Calibri", 16)).pack(pady=(20, 10), padx=20)

        self.password_entry = customtkinter.CTkEntry(main_frame, show="*", border_color=COLOR_RED, width=250)
        self.password_entry.pack(pady=5, padx=20)
        self.password_entry.focus_set()
        self.password_entry.bind("<Return>", self._on_ok)

        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(15, 20))

        customtkinter.CTkButton(button_frame, text="OK", command=self._on_ok, width=100, fg_color=COLOR_RED, hover_color=COLOR_HOVER_RED).pack(side="left", padx=10)
        customtkinter.CTkButton(button_frame, text="Abbrechen", command=self._on_cancel, width=100, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def _on_ok(self, event=None):
        self._result = self.password_entry.get()
        self.grab_release()
        self.destroy()

    def _on_cancel(self):
        self._result = None
        self.grab_release()
        self.destroy()

    def get_password(self):
        self.master.wait_window(self)
        return self._result

def create_form_header(parent, text, icon, color):
    """Erstellt eine einheitliche Kopfzeile für jedes Formular."""
    header_frame = customtkinter.CTkFrame(parent, fg_color=color, corner_radius=0, height=60)
    header_frame.grid(row=0, column=0, sticky="ew")
    header_frame.grid_columnconfigure(0, weight=1)
    
    inner_frame = customtkinter.CTkFrame(header_frame, fg_color="transparent")
    inner_frame.pack(pady=10, padx=20, fill="x")

    text_color = COLOR_BLACK if color == COLOR_YELLOW else "white"

    label = customtkinter.CTkLabel(inner_frame, text=text, image=icon, compound="left", font=("Calibri", 24, "bold"), text_color=text_color, anchor="w")
    label.pack(side="left")
    return header_frame

class MobiForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Annahme Mobi")
        self.geometry("1100x800")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)
        
        self.input_fields = {}
        self.vehicle_data = []
        self.brand_names = []
        self.current_brand_models = []
        self._load_vehicle_data()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        scrollable_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent")
        scrollable_frame.grid(row=0, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure((0, 2), weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=0)

        left_frame = customtkinter.CTkFrame(scrollable_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="new", padx=(0, 10), pady=10)
        left_frame.grid_columnconfigure(0, weight=1)

        separator = customtkinter.CTkFrame(scrollable_frame, width=2, fg_color=COLOR_YELLOW)
        separator.grid(row=0, column=1, sticky="ns", pady=10)

        right_frame = customtkinter.CTkFrame(scrollable_frame, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="new", padx=(10, 0), pady=10)
        right_frame.grid_columnconfigure(0, weight=1)

        self._create_auftraggeber_widgets(left_frame)
        self._create_fahrzeug_widgets(left_frame)
        self._create_kunde_widgets(right_frame)
        self._create_ort_widgets(right_frame)
        self._create_ersatzfahrzeug_widgets(right_frame)
        
        self._create_action_buttons(main_frame)

    def _load_vehicle_data(self):
        try:
            local_vehicle_data = [
                {"brand": "Volkswagen", "models": ["Golf", "Passat", "Tiguan", "Polo", "T-Roc", "Touran"]},
                {"brand": "Audi", "models": ["A3", "A4", "A6", "Q3", "Q5", "e-tron"]},
                {"brand": "Skoda", "models": ["Octavia", "Fabia", "Kodiaq", "Superb", "Enyaq"]},
                {"brand": "Seat", "models": ["Leon", "Ibiza", "Ateca", "Arona"]},
                {"brand": "Cupra", "models": ["Formentor", "Born", "Leon", "Ateca"]},
            ]
            self.vehicle_data = local_vehicle_data
            self.brand_names = sorted([v['brand'] for v in self.vehicle_data])
        except Exception as e:
            print(f"Fehler beim Laden der lokalen Fahrzeugdaten: {e}")
            self.vehicle_data, self.brand_names = [], []

    def _create_section_card(self, parent, title):
        card = customtkinter.CTkFrame(parent, fg_color=COLOR_MEDIUM_GREY, corner_radius=10)
        card.pack(fill="x", expand=True, padx=0, pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)

        header_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10))
        customtkinter.CTkLabel(header_frame, text=title, font=("Calibri", 18, "bold"), anchor="w", text_color=COLOR_YELLOW).pack(fill="x")
        
        separator = customtkinter.CTkFrame(card, fg_color=COLOR_LIGHT_GREY, height=2)
        separator.grid(row=1, column=0, sticky="ew", padx=10)

        content_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        content_frame.grid_columnconfigure(1, weight=1)
        return content_frame

    def _create_auftraggeber_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Auftragsdetails")
        customtkinter.CTkLabel(content_frame, text="Auftraggeber:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["VW Notdienst", "Audi Notdienst", "Skoda Notdienst", "Seat Notdienst", "Cupra Notdienst"], fg_color=COLOR_YELLOW, button_color=COLOR_YELLOW, button_hover_color=COLOR_HOVER_YELLOW, text_color=COLOR_BLACK); w.set("VW Notdienst"); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Auftraggeber"] = w
        customtkinter.CTkLabel(content_frame, text="Vorgangsnummer:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_YELLOW, width=250); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Vorgangsnummer"] = w
        customtkinter.CTkLabel(content_frame, text="Anrufername:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_YELLOW, width=250); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Anrufername"] = w
        
    def _create_fahrzeug_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Fahrzeugdetails")
        customtkinter.CTkLabel(content_frame, text="Fahrzeug:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.brand_combo = customtkinter.CTkComboBox(content_frame, values=self.brand_names, command=self._on_brand_change, width=250, border_color=COLOR_YELLOW, button_color=COLOR_YELLOW, button_hover_color=COLOR_HOVER_YELLOW, dropdown_hover_color=COLOR_HOVER_YELLOW)
        self.brand_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w"); self.brand_combo.set("")
        self.brand_combo.bind("<KeyRelease>", self._on_brand_change)
        self.input_fields["Fahrzeug"] = self.brand_combo
        customtkinter.CTkLabel(content_frame, text="Modell:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.model_combo = customtkinter.CTkComboBox(content_frame, values=[""], state="disabled", width=250, border_color=COLOR_YELLOW, button_color=COLOR_YELLOW, button_hover_color=COLOR_HOVER_YELLOW, command=self.on_model_selected, dropdown_hover_color=COLOR_HOVER_YELLOW)
        self.model_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Modell"] = self.model_combo
        labels = ["Kennzeichen", "Fahrgestellnummer", "Erstzulassung", "KM-Stand", "Schaden"]
        for i, label_text in enumerate(labels, start=2):
            customtkinter.CTkLabel(content_frame, text=f"{label_text}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkEntry(content_frame, border_color=COLOR_YELLOW, width=250); w.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.input_fields[label_text] = w

    def _on_brand_change(self, event_or_choice):
        current_value = self.brand_combo.get()
        filtered_brands = [b for b in self.brand_names if b.lower().startswith(current_value.lower())]
        self.brand_combo.configure(values=filtered_brands)
        models = next((item["models"] for item in self.vehicle_data if item["brand"] == current_value), [])
        self.current_brand_models = sorted(models)
        self.model_combo.configure(values=self.current_brand_models, state="normal" if models else "disabled")
        if not models: self.model_combo.set("")

    def on_model_selected(self, selected_model):
        self.input_fields["Kennzeichen"].focus_set()

    def _create_kunde_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Kundendetails")
        customtkinter.CTkLabel(content_frame, text="Kunde vor Ort:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_YELLOW, width=250); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Kunde vor Ort"] = w
        customtkinter.CTkLabel(content_frame, text="Telefonnummer:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_YELLOW, width=250); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Telefonnummer"] = w

    def _create_ort_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Ortsdetails")
        customtkinter.CTkLabel(content_frame, text="Pannenort:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_YELLOW, width=300); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Pannenort"] = w
        customtkinter.CTkLabel(content_frame, text="Verbringungsort (Autohaus):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_YELLOW, width=300); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Verbringungsort (Autohaus)"] = w

    def _create_ersatzfahrzeug_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Zusatzleistungen")
        customtkinter.CTkLabel(content_frame, text="Kunde braucht ein Ersatzfahrzeug?:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Nein", "Ja"], fg_color=COLOR_YELLOW, button_color=COLOR_YELLOW, button_hover_color=COLOR_HOVER_YELLOW, text_color=COLOR_BLACK); w.set("Nein"); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Kunde braucht ein Ersatzfahrzeug?"] = w
        
    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        center_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        center_frame.pack(anchor="e")
        customtkinter.CTkButton(center_frame, text="Info (Safar)", command=self.copy_safar_info, fg_color=COLOR_RED, hover_color=COLOR_HOVER_RED).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Kopieren", command=self.copy_to_clipboard, fg_color=COLOR_YELLOW, hover_color=COLOR_HOVER_YELLOW, text_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Zurücksetzen", command=self.reset_form, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Schließen", command=self.destroy, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def reset_form(self):
        for widget in self.input_fields.values():
            if isinstance(widget, customtkinter.CTkEntry): widget.delete(0, "end")
            elif isinstance(widget, customtkinter.CTkOptionMenu): widget.set(widget.cget("values")[0])
            elif isinstance(widget, customtkinter.CTkComboBox): widget.set("")
        self.brand_combo.configure(values=self.brand_names)
        self._on_brand_change(None)

    def _get_value(self, label):
        widget = self.input_fields.get(label)
        if not widget: return ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)): return widget.get().strip()
        elif isinstance(widget, customtkinter.CTkEntry): return widget.get().strip()
        return ""

    def copy_safar_info(self):
        safar_text = """Mobilitätsgarantie:

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
* BEI EINER LEERFAHRT BITTE DEN GRUND IM INFO-FELD EINTRAGEN !"""
        self.clipboard_clear()
        self.clipboard_append(safar_text)
        print("Safar Info-Text wurde in die Zwischenablage kopiert.")

    def copy_to_clipboard(self):
        sections = {
            "auftrag": ["Auftraggeber", "Vorgangsnummer", "Anrufername"],
            "fahrzeug": ["Fahrzeug", "Modell", "Kennzeichen", "Fahrgestellnummer", "Erstzulassung", "KM-Stand", "Schaden"],
            "kunde": ["Kunde vor Ort", "Telefonnummer"],
            "ort": ["Pannenort", "Verbringungsort (Autohaus)"]
        }
        output_blocks = []
        for section_keys in sections.values():
            block_lines = [f"{key}: {self._get_value(key)}" for key in section_keys if self._get_value(key)]
            if block_lines: output_blocks.append("\n".join(block_lines))
        
        final_text = "\n\n".join(output_blocks)
        if final_text: final_text += "\n\n"
        final_text += f"Kunde braucht ein Ersatzfahrzeug?: {self._get_value('Kunde braucht ein Ersatzfahrzeug?')}"
        
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Folgender Text wurde kopiert:\n" + final_text)

class OelspurForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Annahme Ölspur")
        self.geometry("1100x750")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)
        
        self.input_fields = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        scrollable_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent")
        scrollable_frame.grid(row=0, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure((0, 2), weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=0)

        left_frame = customtkinter.CTkFrame(scrollable_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="new", padx=(0, 10), pady=10)
        left_frame.grid_columnconfigure(0, weight=1)
        
        separator = customtkinter.CTkFrame(scrollable_frame, width=2, fg_color=COLOR_BLUE)
        separator.grid(row=0, column=1, sticky="ns", pady=10)

        right_frame = customtkinter.CTkFrame(scrollable_frame, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="new", padx=(10, 0), pady=10)
        right_frame.grid_columnconfigure(0, weight=1)

        self._create_melder_anrufer_widgets(left_frame)
        self._create_verunreinigung_widgets(left_frame)
        self._create_absicherung_widgets(right_frame)
        self._create_zusatzinfo_widgets(right_frame)
        
        self._create_action_buttons(main_frame)

    def _create_section_card(self, parent, title):
        card = customtkinter.CTkFrame(parent, fg_color=COLOR_MEDIUM_GREY, corner_radius=10)
        card.pack(fill="x", expand=True, padx=0, pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)

        header_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10))
        customtkinter.CTkLabel(header_frame, text=title, font=("Calibri", 18, "bold"), anchor="w", text_color=COLOR_BLUE).pack(fill="x")
        
        separator = customtkinter.CTkFrame(card, fg_color=COLOR_LIGHT_GREY, height=2)
        separator.grid(row=1, column=0, sticky="ew", padx=10)

        content_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        content_frame.grid_columnconfigure(1, weight=1)
        return content_frame

    def _create_melder_anrufer_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Melder & Anrufer")
        customtkinter.CTkLabel(content_frame, text="Melder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=250); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Melder"] = w
        customtkinter.CTkLabel(content_frame, text="Anrufer:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=250); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Anrufer"] = w
        customtkinter.CTkLabel(content_frame, text="Telefonnummer:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=250); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Telefonnummer"] = w
        
    def _create_verunreinigung_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Details der Verunreinigung")
        customtkinter.CTkLabel(content_frame, text="Art:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=250); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Art der Verunreinigung"] = w
        customtkinter.CTkLabel(content_frame, text="Länge:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=150); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Länge"] = w
        customtkinter.CTkLabel(content_frame, text="Breite:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=150); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Breite"] = w

    def _create_absicherung_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Einsatzort & Absicherung")
        customtkinter.CTkLabel(content_frame, text="Absicherung notwendig:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Nein", "Ja", "Unklar"], fg_color=COLOR_BLUE, button_color=COLOR_BLUE, button_hover_color=COLOR_HOVER_BLUE); w.set("Nein"); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Absicherung vor Ort Notwendig"] = w
        customtkinter.CTkLabel(content_frame, text="Einsatzkräfte vor Ort?:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=250); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Einsatzkräfte vor Ort?"] = w
        customtkinter.CTkLabel(content_frame, text="Verursacher bekannt?:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=250); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Verursacher bekannt?"] = w
        customtkinter.CTkLabel(content_frame, text="Treffpunkt:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_BLUE, width=250); w.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Treffpunkt"] = w

    def _create_zusatzinfo_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Zusatzinformationen")
        content_frame.grid_columnconfigure(0, weight=1) # Make column 0 expandable
        content_frame.grid_columnconfigure(1, weight=0) # Reset weight of column 1
        content_frame.grid_rowconfigure(0, weight=1)
        w = customtkinter.CTkTextbox(content_frame, border_color=COLOR_BLUE, border_width=2, wrap="word", height=150)
        w.grid(row=0, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
        self.input_fields["Zusatzinformation"] = w
        
    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        center_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        center_frame.pack(anchor="e")
        customtkinter.CTkButton(center_frame, text="Kopieren", command=self.copy_to_clipboard, fg_color=COLOR_BLUE, hover_color=COLOR_HOVER_BLUE).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Zurücksetzen", command=self.reset_form, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Schließen", command=self.destroy, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def reset_form(self):
        for widget in self.input_fields.values():
            if isinstance(widget, customtkinter.CTkEntry): widget.delete(0, "end")
            elif isinstance(widget, customtkinter.CTkOptionMenu): widget.set(widget.cget("values")[0])
            elif isinstance(widget, customtkinter.CTkTextbox): widget.delete("1.0", "end")

    def _get_value(self, label):
        widget = self.input_fields.get(label)
        if not widget: return ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)): return widget.get().strip()
        elif isinstance(widget, customtkinter.CTkTextbox): return widget.get("1.0", "end-1c").strip()
        elif isinstance(widget, customtkinter.CTkEntry): return widget.get().strip()
        return ""

    def copy_to_clipboard(self):
        output_lines = ["**Einsatzdetails Ölspur**", ""]
        
        simple_fields = ["Melder", "Anrufer", "Telefonnummer", "Art der Verunreinigung"]
        for label in simple_fields:
            value = self._get_value(label)
            if value: output_lines.append(f"{label}: {value}")

        laenge = self._get_value("Länge")
        breite = self._get_value("Breite")
        if laenge or breite: output_lines.append(f"Länge: {laenge} | Breite: {breite}")

        remaining_fields = ["Absicherung vor Ort Notwendig", "Einsatzkräfte vor Ort?", "Verursacher bekannt?", "Treffpunkt"]
        for label in remaining_fields:
            value = self._get_value(label)
            if value: output_lines.append(f"{label}: {value}")
        
        zusatzinfo = self._get_value("Zusatzinformation")
        if zusatzinfo: output_lines.extend(["", "**Zusatzinformation:**", zusatzinfo])
        
        final_text = "\n".join(output_lines)
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Folgender Text wurde kopiert:\n" + final_text)

class PanneUnfallForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Abklärung Panne | Unfall")
        self.geometry("1200x950")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)
        
        self.input_fields = {}
        self.dynamic_widgets = {}
        self.section_checkboxes = {}

        self.schaden_data = {
            "Bitte Wählen": ["-"],
            "Reifen": [
                "Bitte Wählen", "Reifenpanne (unbekannt)", "Reifenschaden vorne links", "Reifenschaden vorne rechts",
                "Reifenschaden hinten links", "Reifenschaden hinten rechts", "Alle Reifen betroffen", "Abgefahrene Reifen",
                "Reifen durch Steinschlag beschädigt", "Felge beschädigt", "Defektes Reifenventil", "Radschrauben locker/beschädigt"
            ],
            "Motor/Antrieb": [
                "Bitte Wählen", "Motorproblem (allgemein)", "Motor springt nicht an", "Motor überhitzt", "Motor blockiert",
                "Motorstottern / Leistungsverlust", "Kompressionsverlust", "Keilriemen/Zahnriemen gerissen", "Turbolader defekt",
                "Öldruck zu niedrig", "Getriebeschaden", "Kupplungsschaden", "Antriebswelle defekt"
            ],
            "Elektrik/Elektronik": [
                "Bitte Wählen", "Batterie leer/defekt", "Lichtmaschine defekt", "Anlasser defekt", "Defekte Sicherung",
                "Zündprobleme (Zündkerzen/Zündspule)", "Steuergerät defekt", "Fehler in der Elektronik", "Defekter Sensor",
                "Fehlermeldung im Display", "Warnleuchte leuchtet (MKL, ABS, Airbag)", "Beleuchtung defekt", "Bremslichter defekt",
                "Tempomat defekt"
            ],
            "Fahrwerk/Bremse": [
                "Bitte Wählen", "Bremsproblem (allgemein)", "Bremsenversagen", "Bremse fest", "Verzogene Bremsscheiben",
                "Bremsflüssigkeitsverlust", "Bremsschlauch undicht/geplatzt", "Bremskraftverstärker defekt", "ABS-Fehler",
                "Handbremse defekt/fest", "Stoßdämpfer defekt", "Federbruch", "Radlager defekt", "Querlenker defekt",
                "Stabilisator defekt", "Spurstange defekt", "Achs-/Radaufhängungsschaden", "Lagerung verschlissen", "Defekte Achse",
                "Fahrwerksgeometrie verstellt"
            ],
            "Lenkung": [
                "Bitte Wählen", "Lenkungsproblem (allgemein)", "Servolenkung defekt", "Lenkgetriebe defekt", "Lenkungslager defekt"
            ],
            "Kraftstoffsystem": [
                "Bitte Wählen", "Kraftstoffmangel", "Falschbetankung", "Kraftstoffpumpe defekt", "Einspritzdüsen defekt",
                "Kraftstofffilter verstopft", "Kraftstoffleitung undicht", "Luftmassenmesser defekt"
            ],
            "Kühlsystem/Klima": [
                "Bitte Wählen", "Kühlmittelverlust", "Kühler undicht", "Wasserpumpe defekt", "Thermostat defekt",
                "Heizungskern defekt", "Lüftermotor defekt", "Klimaanlage defekt", "Klimakompressor defekt", "Kondensator defekt"
            ],
            "Abgassystem": [
                "Bitte Wählen", "Auspuff defekt/laut", "Katalysator defekt", "Auspuffrohr beschädigt",
                "Partikelfilter verstopft", "Abgasrückführung (AGR) defekt"
            ],
            "Karosserie/Unfall": [
                "Bitte Wählen", "Unfallschaden", "Wildschaden", "Hagelschaden", "Einbruchschaden/Vandalismus",
                "Glasschaden (Scheibenriss etc.)", "Wasserlecks"
            ],
            "Schlüssel / Zugang": [
                "Bitte Wählen", "Ausgesperrt (Schlüssel im Fahrzeug)", "Schlüssel verloren/defekt", "Türschloss defekt",
                "Fensterheber defekt", "Zentralverriegelung defekt"
            ],
            "Sonstiges": [
                "Bitte Wählen", "Maderschaden/Marderfrass", "Scheibenwischer defekt", "Fahrzeug gestohlen", "Fahrzeug festgefahren",
                "Unklares Geräusch", "Airbags defekt"
            ]
        }

        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        # Main container for the two columns
        main_container = customtkinter.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure((0, 1), weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Left and Right scrollable frames
        left_scrollable_frame = customtkinter.CTkScrollableFrame(main_container, fg_color="transparent")
        left_scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_scrollable_frame.grid_columnconfigure(0, weight=1)

        right_scrollable_frame = customtkinter.CTkScrollableFrame(main_container, fg_color="transparent")
        right_scrollable_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_scrollable_frame.grid_columnconfigure(0, weight=1)

        # --- Populate left column ---
        self._create_schaden_widgets(left_scrollable_frame)
        self._create_standort_personen_widgets(left_scrollable_frame)
        self._create_fahrzeugdaten_widgets(left_scrollable_frame)
        
        # --- Populate right column ---
        self._create_dispo_programm_widgets(right_scrollable_frame)
        self._create_termin_widgets(right_scrollable_frame)
        self._create_freigabe_widgets(right_scrollable_frame)
        self._create_schutzbrief_widgets(right_scrollable_frame)
        self._create_unfall_widgets(right_scrollable_frame)

        self._create_action_buttons(self)

    def _create_section_card(self, parent, title, section_key):
        """Creates a container card for a section with a header."""
        card = customtkinter.CTkFrame(parent, fg_color=COLOR_MEDIUM_GREY, corner_radius=10)
        card.pack(fill="x", expand=True, padx=5, pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)

        header_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        checkbox = customtkinter.CTkCheckBox(header_frame, text="", border_color=COLOR_RED, hover_color=COLOR_HOVER_RED, fg_color=COLOR_RED, checkbox_width=18, checkbox_height=18)
        checkbox.grid(row=0, column=0, padx=(0, 10))
        self.section_checkboxes[section_key] = checkbox
        
        label = customtkinter.CTkLabel(header_frame, text=title, font=("Calibri", 18, "bold"), anchor="w", text_color=COLOR_RED)
        label.grid(row=0, column=1, sticky="w")
        
        # Separator line
        separator = customtkinter.CTkFrame(card, fg_color=COLOR_LIGHT_GREY, height=2)
        separator.grid(row=1, column=0, sticky="ew", padx=10)

        # Content frame for widgets
        content_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        content_frame.grid_columnconfigure(1, weight=1)

        return content_frame

    def _create_schaden_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Schaden", "schaden")
        self.schaden_frame = content_frame # For dynamic widgets

        customtkinter.CTkLabel(content_frame, text="Schadensursache:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkComboBox(content_frame, values=list(self.schaden_data.keys()), command=self.on_schadensursache_select, width=220, border_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED, dropdown_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Schadensursache"] = w
        
        customtkinter.CTkLabel(content_frame, text="Schaden:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkComboBox(content_frame, values=["-"], state="disabled", command=self.on_schaden_detail_select, width=220, border_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED, dropdown_hover_color=COLOR_HOVER_RED); w.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Schaden"] = w; self.schaden_detail_combo = w
        
        # Spacer for dynamic fields
        content_frame.grid_rowconfigure(4, minsize=10)

        customtkinter.CTkLabel(content_frame, text="Antriebsart:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Diesel/Benzin", "Gas (LPG/CNG)", "Hybrid", "Elektro"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Antriebsart"] = w

        customtkinter.CTkLabel(content_frame, text="Antriebsachse:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Vorderradantrieb (FWD)", "Hinterradantrieb (RWD)", "Allradantrieb (AWD)"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=9, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Antriebsachse"] = w
        
        customtkinter.CTkLabel(content_frame, text="Getriebe:").grid(row=10, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Schaltgetriebe/Manuell", "Automatik", "Doppelkupplungsgetriebe (DSG)"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=10, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Getriebe"] = w
        
        customtkinter.CTkLabel(content_frame, text="Handbremse:").grid(row=11, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Manuell", "Elektrisch"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=11, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Handbremse"] = w

        customtkinter.CTkLabel(content_frame, text="Fahrzeugstand:").grid(row=12, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Noch rollfähig", "Nicht mehr rollfähig"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=12, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Fahrzeugstand"] = w

    def on_schadensursache_select(self, selection):
        detail_options = self.schaden_data.get(selection, ["-"])
        self.schaden_detail_combo.configure(values=detail_options, state="normal")
        self.schaden_detail_combo.set(detail_options[0])
        self.on_schaden_detail_select(self.schaden_detail_combo.get())

    def on_schaden_detail_select(self, selection):
        for widget_key in ['baujahr_label', 'baujahr_entry', 'pos_label', 'pos_combo']:
            if widget_key in self.dynamic_widgets:
                self.dynamic_widgets[widget_key].destroy()
                del self.dynamic_widgets[widget_key]
        if "Baujahr" in self.input_fields: del self.input_fields["Baujahr"]
        if "Position des Schlüssels" in self.input_fields: del self.input_fields["Position des Schlüssels"]

        if selection == "Ausgesperrt (Schlüssel im Fahrzeug)":
            l = customtkinter.CTkLabel(self.schaden_frame, text="Baujahr des Fahrzeugs:"); l.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            e = customtkinter.CTkEntry(self.schaden_frame, placeholder_text="z.B. 2023", border_color=COLOR_RED); e.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            self.dynamic_widgets['baujahr_label'] = l; self.dynamic_widgets['baujahr_entry'] = e; self.input_fields["Baujahr"] = e
            
            l = customtkinter.CTkLabel(self.schaden_frame, text="Position des Schlüssels:"); l.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            c = customtkinter.CTkComboBox(self.schaden_frame, values=["Bitte Wählen", "Im Kofferraum", "Zündschloss", "Fahrersitz", "Handschuhfach"], border_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED, dropdown_hover_color=COLOR_HOVER_RED); c.set("Bitte Wählen"); c.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
            self.dynamic_widgets['pos_label'] = l; self.dynamic_widgets['pos_combo'] = c; self.input_fields["Position des Schlüssels"] = c

    def _create_standort_personen_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Standort & Personen", "standort")
        self.standort_frame = content_frame # For dynamic widgets

        customtkinter.CTkLabel(content_frame, text="Fahrzeug Standort:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        standort_values = [
            "Bitte Wählen", "Auf der Straße", "Linke Fahrspur", "mittlere Spur", "Nothaltebucht", 
            "Pannenstreifen", "Schnellstraße", "Auf dem Parkplatz", "Parkhaus", 
            "Tiefgarage", "Auf dem Feldweg", "Im Hof"
        ]
        w = customtkinter.CTkComboBox(content_frame, values=standort_values, command=self.on_standort_select, border_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED, dropdown_hover_color=COLOR_HOVER_RED)
        w.set("Bitte Wählen")
        w.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Fahrzeug Standort"] = w

        customtkinter.CTkLabel(content_frame, text="Zugänglichkeit:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkComboBox(content_frame, values=["Bitte Wählen", "steht freizugänglich", "vorne nur zugänglich", "seitlich zugänglich", "hinten zugänglich", "nicht zugänglich"], border_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED, dropdown_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Zugänglichkeit"] = w

        customtkinter.CTkLabel(content_frame, text="Mitnahme von Personen:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen"] + [str(i) for i in range(1, 10)], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Mitnahme von Personen"] = w

        customtkinter.CTkLabel(content_frame, text="Wartezeit Info:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "15-30 Min", "30-45 Min", "45-60 Min", "60-90 Min", "90-120 Min", "2-3 Std", "3-4 Std", "4-5 Std"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Wartezeit Info"] = w

    def on_standort_select(self, selection):
        for widget_key in ['parkhaus_label', 'parkhaus_entry']:
            if widget_key in self.dynamic_widgets:
                self.dynamic_widgets[widget_key].destroy()
                del self.dynamic_widgets[widget_key]
        if "Etage & Parkplatz Nr." in self.input_fields:
            del self.input_fields["Etage & Parkplatz Nr."]

        if selection == "Parkhaus":
            l = customtkinter.CTkLabel(self.standort_frame, text="Etage & Parkplatz Nr.:")
            l.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            e = customtkinter.CTkEntry(self.standort_frame, placeholder_text="z.B. E3, P27", border_color=COLOR_RED)
            e.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            
            self.dynamic_widgets['parkhaus_label'] = l
            self.dynamic_widgets['parkhaus_entry'] = e
            self.input_fields["Etage & Parkplatz Nr."] = e

    def _create_fahrzeugdaten_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Fahrzeugdaten (Transporter)", "transporter")
        customtkinter.CTkLabel(content_frame, text="Länge in mm (18):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, placeholder_text="z.B. 4800", border_color=COLOR_RED); w.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Länge in mm (18)"] = w
        customtkinter.CTkLabel(content_frame, text="Breite in mm (19):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, placeholder_text="z.B. 1800", border_color=COLOR_RED); w.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Breite in mm (19)"] = w
        customtkinter.CTkLabel(content_frame, text="Höhe in mm (20):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, placeholder_text="z.B. 1500", border_color=COLOR_RED); w.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Höhe in mm (20)"] = w
        customtkinter.CTkLabel(content_frame, text="Gewicht in kg (F.2):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, placeholder_text="z.B. 1600", border_color=COLOR_RED); w.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Gewicht in kg (F.2)"] = w
        customtkinter.CTkLabel(content_frame, text="Fahrzeug im Leerzustand:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Ja", "Nein"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Fahrzeug im Leerzustand"] = w

    def _create_dispo_programm_widgets(self, parent):
        card = customtkinter.CTkFrame(parent, fg_color=COLOR_MEDIUM_GREY, corner_radius=10)
        card.pack(fill="x", expand=True, padx=5, pady=(0, 15))
        
        header_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(5, 10))
        label = customtkinter.CTkLabel(header_frame, text="Dispo Programm", font=("Calibri", 18, "bold"), text_color=COLOR_RED)
        label.pack(side="left")

        separator = customtkinter.CTkFrame(card, fg_color=COLOR_LIGHT_GREY, height=2)
        separator.pack(fill="x", padx=10, pady=(0, 5))
        
        checkbox_frame = customtkinter.CTkFrame(card, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=10, pady=5)
        
        self.dispo_checkboxes = {}
        cb_et360 = customtkinter.CTkCheckBox(checkbox_frame, text="ET360", command=lambda: self._handle_checkbox("ET360"), border_color=COLOR_RED, hover_color=COLOR_HOVER_RED, fg_color=COLOR_RED); cb_et360.pack(side="left", padx=10, pady=5)
        cb_bosch = customtkinter.CTkCheckBox(checkbox_frame, text="Bosch", command=lambda: self._handle_checkbox("Bosch"), border_color=COLOR_RED, hover_color=COLOR_HOVER_RED, fg_color=COLOR_RED); cb_bosch.pack(side="left", padx=10, pady=5)
        cb_carry = customtkinter.CTkCheckBox(checkbox_frame, text="Carry", command=lambda: self._handle_checkbox("Carry"), border_color=COLOR_RED, hover_color=COLOR_HOVER_RED, fg_color=COLOR_RED); cb_carry.pack(side="left", padx=10, pady=5)
        
        self.dispo_checkboxes["ET360"] = cb_et360
        self.dispo_checkboxes["Bosch"] = cb_bosch
        self.dispo_checkboxes["Carry"] = cb_carry

    def _handle_checkbox(self, selected_cb_name):
        for name, cb in self.dispo_checkboxes.items():
            if name != selected_cb_name:
                cb.deselect()

    def _create_termin_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Terminvereinbarung", "termin")
        content_frame.grid_columnconfigure((1, 3), weight=1)

        customtkinter.CTkLabel(content_frame, text="Datum:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, placeholder_text="TT.MM.JJJJ", border_color=COLOR_RED); w.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Datum"] = w
        customtkinter.CTkLabel(content_frame, text="Uhrzeit:").grid(row=0, column=2, padx=(10, 5), pady=5, sticky="w")
        w = customtkinter.CTkEntry(content_frame, placeholder_text="HH:MM", border_color=COLOR_RED); w.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.input_fields["Uhrzeit"] = w

    def _create_freigabe_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Freigabe", "freigabe")
        self.freigabe_frame = content_frame 

        customtkinter.CTkLabel(content_frame, text="Freigaben Typ:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "300er Freigabe", "Festpreiswechsel", "Zonen Freigabe"], command=self.on_freigabe_select, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Freigaben Typ"] = w

    def on_freigabe_select(self, selection):
        # --- Clean up all dynamic widgets first ---
        widgets_to_clear = [
            'fp_label', 'fp_menu', 'name_label', 'name_entry', 'phz_label', 'phz_menu',
            'zone_label', 'zone_menu', 'art_freigabe_label', 'art_freigabe_menu',
            'zonen_name_label', 'zonen_name_entry'
        ]
        for widget_key in widgets_to_clear:
            if widget_key in self.dynamic_widgets:
                self.dynamic_widgets[widget_key].destroy()
                del self.dynamic_widgets[widget_key]

        # --- Clean up corresponding input_fields entries ---
        fields_to_clear = [
            "Festpreis", "Name (Freigabe erteilt)", "Pannenhilfszentrale", "Zone",
            "Art der Freigabe", "Name (Freigabe erteilt, Zone)"
        ]
        for field_key in fields_to_clear:
            if field_key in self.input_fields:
                del self.input_fields[field_key]

        # --- Build new UI based on selection ---
        current_row = 1
        phz_values = ["Bitte Wählen", "PHZ Nord", "PHZ West", "PHZ Mitte", "PHZ Süd", "PHZ Ost"]

        if selection == "300er Freigabe":
            l_name = customtkinter.CTkLabel(self.freigabe_frame, text="Name (Freigabe erteilt):")
            l_name.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            e_name = customtkinter.CTkEntry(self.freigabe_frame, border_color=COLOR_RED)
            e_name.grid(row=current_row, column=1, padx=5, pady=5, sticky="ew")
            self.dynamic_widgets['name_label'] = l_name; self.dynamic_widgets['name_entry'] = e_name
            self.input_fields["Name (Freigabe erteilt)"] = e_name
            current_row += 1
            
            l_phz = customtkinter.CTkLabel(self.freigabe_frame, text="Pannenhilfszentrale:")
            l_phz.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            m_phz = customtkinter.CTkOptionMenu(self.freigabe_frame, values=phz_values, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED)
            m_phz.set("Bitte Wählen"); m_phz.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
            self.dynamic_widgets['phz_label'] = l_phz; self.dynamic_widgets['phz_menu'] = m_phz
            self.input_fields["Pannenhilfszentrale"] = m_phz

        elif selection == "Festpreiswechsel":
            l_fp = customtkinter.CTkLabel(self.freigabe_frame, text="Festpreis:")
            l_fp.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            m_fp = customtkinter.CTkOptionMenu(self.freigabe_frame, values=["Bitte Wählen", "FP1", "FP2", "FP3"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED)
            m_fp.set("Bitte Wählen"); m_fp.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
            self.dynamic_widgets['fp_label'] = l_fp; self.dynamic_widgets['fp_menu'] = m_fp
            self.input_fields["Festpreis"] = m_fp
            current_row += 1

            l_name = customtkinter.CTkLabel(self.freigabe_frame, text="Name (Freigabe erteilt):")
            l_name.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            e_name = customtkinter.CTkEntry(self.freigabe_frame, border_color=COLOR_RED)
            e_name.grid(row=current_row, column=1, padx=5, pady=5, sticky="ew")
            self.dynamic_widgets['name_label'] = l_name; self.dynamic_widgets['name_entry'] = e_name
            self.input_fields["Name (Freigabe erteilt)"] = e_name
            current_row += 1

            l_phz = customtkinter.CTkLabel(self.freigabe_frame, text="Pannenhilfszentrale:")
            l_phz.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            m_phz = customtkinter.CTkOptionMenu(self.freigabe_frame, values=phz_values, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED)
            m_phz.set("Bitte Wählen"); m_phz.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
            self.dynamic_widgets['phz_label'] = l_phz; self.dynamic_widgets['phz_menu'] = m_phz
            self.input_fields["Pannenhilfszentrale"] = m_phz

        elif selection == "Zonen Freigabe":
            l_zone = customtkinter.CTkLabel(self.freigabe_frame, text="Zone:")
            l_zone.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            m_zone = customtkinter.CTkOptionMenu(self.freigabe_frame, values=["Bitte Wählen", "Zone I", "Zone II", "Zone III"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED)
            m_zone.set("Bitte Wählen"); m_zone.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
            self.dynamic_widgets['zone_label'] = l_zone; self.dynamic_widgets['zone_menu'] = m_zone
            self.input_fields["Zone"] = m_zone
            current_row += 1

            l_art = customtkinter.CTkLabel(self.freigabe_frame, text="Art der Freigabe:")
            l_art.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            m_art = customtkinter.CTkOptionMenu(self.freigabe_frame, values=["Bitte Wählen", "Elba Portal", "telefonisch"], command=self.on_zonen_freigabe_art_select, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED)
            m_art.set("Bitte Wählen"); m_art.grid(row=current_row, column=1, padx=5, pady=5, sticky="w")
            self.dynamic_widgets['art_freigabe_label'] = l_art; self.dynamic_widgets['art_freigabe_menu'] = m_art
            self.input_fields["Art der Freigabe"] = m_art

    def on_zonen_freigabe_art_select(self, selection):
        # Clean up previous name entry if it exists
        if 'zonen_name_label' in self.dynamic_widgets:
            self.dynamic_widgets['zonen_name_label'].destroy()
            del self.dynamic_widgets['zonen_name_label']
        if 'zonen_name_entry' in self.dynamic_widgets:
            self.dynamic_widgets['zonen_name_entry'].destroy()
            del self.dynamic_widgets['zonen_name_entry']
        if "Name (Freigabe erteilt, Zone)" in self.input_fields:
            del self.input_fields["Name (Freigabe erteilt, Zone)"]

        # Create new name entry if 'telefonisch' is selected
        if selection == "telefonisch":
            # Determine the row after "Art der Freigabe"
            current_row = self.dynamic_widgets['art_freigabe_label'].grid_info()['row'] + 1
            
            l_name = customtkinter.CTkLabel(self.freigabe_frame, text="Name (Freigabe erteilt):")
            l_name.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
            e_name = customtkinter.CTkEntry(self.freigabe_frame, border_color=COLOR_RED)
            e_name.grid(row=current_row, column=1, padx=5, pady=5, sticky="ew")

            self.dynamic_widgets['zonen_name_label'] = l_name
            self.dynamic_widgets['zonen_name_entry'] = e_name
            self.input_fields["Name (Freigabe erteilt, Zone)"] = e_name

    def _create_schutzbrief_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Schutzbriefleistung", "schutzbrief")
        
        customtkinter.CTkLabel(content_frame, text="Kunde braucht Mietwagen?:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Ja", "Nein"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Kunde braucht Mietwagen?"] = w
        
        customtkinter.CTkLabel(content_frame, text="Abklärung:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "Sammler abklären", "Leer Pickup abklären"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Abklärung"] = w
        
        customtkinter.CTkLabel(content_frame, text="Anlieferadresse des Fahrzeugs:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        adresse_entry = customtkinter.CTkEntry(content_frame, border_color=COLOR_RED, width=350); adresse_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.input_fields["Anlieferadresse des Fahrzeugs"] = adresse_entry

    def _create_unfall_widgets(self, parent):
        content_frame = self._create_section_card(parent, "Unfall", "unfall")
        self.unfall_frame = content_frame # For dynamic widgets

        customtkinter.CTkLabel(content_frame, text="Schuldfrage Unfall:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Bitte Wählen", "01 Unfall (Schuld)", "02 Unfall (Nicht Schuld)", "Schuldfrage unklar"], command=self.on_unfall_select, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.set("Bitte Wählen"); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.input_fields["Schuldfrage Unfall"] = w

    def on_unfall_select(self, selection):
        if 'vk_label' in self.dynamic_widgets: self.dynamic_widgets['vk_label'].destroy(); del self.dynamic_widgets['vk_label']
        if 'vk_menu' in self.dynamic_widgets: self.dynamic_widgets['vk_menu'].destroy(); del self.dynamic_widgets['vk_menu']
        if "Fahrzeug ist Vollkasko versichert?" in self.input_fields: self.input_fields.pop("Fahrzeug ist Vollkasko versichert?")
        
        if selection == "01 Unfall (Schuld)":
            l = customtkinter.CTkLabel(self.unfall_frame, text="Fahrzeug ist Vollkasko versichert?:"); l.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            m = customtkinter.CTkOptionMenu(self.unfall_frame, values=["Bitte Wählen", "Ja", "Nein"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); m.set("Bitte Wählen"); m.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.dynamic_widgets['vk_label'] = l; self.dynamic_widgets['vk_menu'] = m; self.input_fields["Fahrzeug ist Vollkasko versichert?"] = m
            
    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        center_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        center_frame.pack(anchor="e")

        customtkinter.CTkButton(center_frame, text="Kopieren", command=self.copy_to_clipboard, fg_color=COLOR_RED, hover_color=COLOR_HOVER_RED).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Zurücksetzen", command=self.reset_form, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Schließen", command=self.destroy, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def reset_form(self):
        # Alle Standard-Widgets zurücksetzen
        for widget in self.input_fields.values():
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, (customtkinter.CTkOptionMenu, customtkinter.CTkComboBox)):
                # 'Bitte Wählen' oder den ersten Wert der Liste setzen
                first_value = widget.cget("values")[0]
                widget.set(first_value)

        # Dynamische Widgets entfernen und zugehörige Comboboxen zurücksetzen
        self.input_fields["Schadensursache"].set("Bitte Wählen")
        self.on_schadensursache_select("Bitte Wählen")
        
        self.input_fields["Fahrzeug Standort"].set("Bitte Wählen")
        self.on_standort_select("Bitte Wählen")

        self.input_fields["Freigaben Typ"].set("Bitte Wählen")
        self.on_freigabe_select("Bitte Wählen")
        
        self.input_fields["Schuldfrage Unfall"].set("Bitte Wählen")
        self.on_unfall_select("Bitte Wählen")

        # Checkboxen zurücksetzen
        for cb in self.dispo_checkboxes.values():
            cb.deselect()
        for cb in self.section_checkboxes.values():
            cb.deselect()

    def _get_value(self, label):
        if label not in self.input_fields: return ""
        widget = self.input_fields[label]
        value = ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)):
            value = widget.get()
            if value in ["Bitte Wählen", "-"]: return ""
        elif isinstance(widget, customtkinter.CTkEntry):
            value = widget.get()
        return value.strip()

    def _get_all_values_for_section(self, section_key, ordered_keys):
        """Helper to get all non-empty values for a section, for Carry format."""
        values = []
        if section_key == "schaden":
            ursache = self._get_value("Schadensursache")
            detail = self._get_value("Schaden")
            if ursache:
                value = f"{ursache}"
                if detail: value += f" | {detail}"
                values.append(value)
        
        for key in ordered_keys:
            if section_key == "schaden" and key in ["Schadensursache", "Schaden"]:
                continue
            value = self._get_value(key)
            if value:
                values.append(value)
        return values

    def _generate_section_block(self, title, ordered_keys):
        """Helper to generate a formatted block of text for a section."""
        section_lines = []
        
        # Special handling for "Schaden"
        if title == "Schaden":
            ursache = self._get_value("Schadensursache")
            detail = self._get_value("Schaden")
            if ursache:
                value = f"{ursache}"
                if detail: value += f" | {detail}"
                section_lines.append(f"Schaden: {value}")
        
        for key in ordered_keys:
            # Skip keys handled elsewhere
            if title == "Schaden" and key in ["Schadensursache", "Schaden"]:
                continue
            if title == "Terminvereinbarung" and key == "Uhrzeit":
                continue # Handled with Datum
            if title == "Freigabe" and key == "Name (Freigabe erteilt, Zone)":
                continue # Handled with Art der Freigabe

            # Combine Datum and Uhrzeit
            if title == "Terminvereinbarung" and key == "Datum":
                datum = self._get_value("Datum")
                uhrzeit = self._get_value("Uhrzeit")
                if datum or uhrzeit:
                    section_lines.append(f"Datum: {datum} Uhrzeit: {uhrzeit}")
                continue

            # Handle conditional name for Zonen Freigabe
            if title == "Freigabe" and key == "Art der Freigabe":
                art_value = self._get_value("Art der Freigabe")
                if art_value:
                    line = f"Art der Freigabe: {art_value}"
                    if art_value == "telefonisch":
                        name_value = self._get_value("Name (Freigabe erteilt, Zone)")
                        if name_value:
                            line += f" | Name: {name_value}"
                    section_lines.append(line)
                continue

            value = self._get_value(key)
            if value:
                section_lines.append(f"{key}: {value}")

        if section_lines:
            return [f"{title}:"] + section_lines
        return []

    def copy_to_clipboard(self):
        is_carry_selected = self.dispo_checkboxes["Carry"].get() == 1
        output_parts = []

        sections_to_check = {
            "schaden": ("Schaden", ["Schadensursache", "Schaden", "Baujahr", "Position des Schlüssels", "Antriebsart", "Antriebsachse", "Getriebe", "Handbremse", "Fahrzeugstand"]),
            "standort": ("Standort & Personen", ["Fahrzeug Standort", "Etage & Parkplatz Nr.", "Zugänglichkeit", "Mitnahme von Personen", "Wartezeit Info"]),
            "transporter": ("Fahrzeugdaten (Transporter)", ["Länge in mm (18)", "Breite in mm (19)", "Höhe in mm (20)", "Gewicht in kg (F.2)", "Fahrzeug im Leerzustand"]),
            "termin": ("Terminvereinbarung", ["Datum", "Uhrzeit"]),
            "freigabe": ("Freigabe", ["Freigaben Typ", "Festpreis", "Name (Freigabe erteilt)", "Pannenhilfszentrale", "Zone", "Art der Freigabe", "Name (Freigabe erteilt, Zone)"]),
            "schutzbrief": ("Schutzbriefleistung", ["Kunde braucht Mietwagen?", "Abklärung", "Anlieferadresse des Fahrzeugs"]),
            "unfall": ("Unfall", ["Schuldfrage Unfall", "Fahrzeug ist Vollkasko versichert?"])
        }

        if is_carry_selected:
            carry_values = []
            block_parts = []
            
            carry_section_keys = ["schaden", "standort", "transporter"]
            exception_section_keys = ["termin", "freigabe", "schutzbrief", "unfall"]

            # Process sections for pipe-separated format
            for section_key in carry_section_keys:
                if self.section_checkboxes.get(section_key) and self.section_checkboxes[section_key].get():
                    title, keys = sections_to_check[section_key]
                    carry_values.extend(self._get_all_values_for_section(section_key, keys))
            
            if carry_values:
                output_parts.append(" | ".join(filter(None, carry_values)))

            # Process exception sections for block format
            for section_key in exception_section_keys:
                 if self.section_checkboxes.get(section_key) and self.section_checkboxes[section_key].get():
                    title, keys = sections_to_check[section_key]
                    block = self._generate_section_block(title, keys)
                    if block:
                        block_parts.append("\n".join(block))
            
            if block_parts:
                # Add a separator if both carry-format and block-format texts exist
                if carry_values:
                    output_parts.append("") # Adds a blank line
                output_parts.extend(block_parts)

        else: # Default block format for all selected sections
            for key, (title, ordered_keys) in sections_to_check.items():
                if self.section_checkboxes.get(key) and self.section_checkboxes[key].get():
                    section_output = self._generate_section_block(title, ordered_keys)
                    if section_output:
                        output_parts.append("\n".join(section_output))

        if output_parts:
            final_text = "\n\n".join(output_parts)
            self.clipboard_clear()
            self.clipboard_append(final_text)
            print("Folgender Text wurde kopiert:\n" + final_text)

class KilianForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Annahme Kilian")
        self.geometry("1500x750")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)

        self.einsatzzentrale_fields = {}
        self.gdv_fields = {}
        self.bus_fields = {}
        self.vehicle_data = []
        self.brand_names = []
        self.current_ez_brand_models = []
        self._load_vehicle_data()

        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure((0, 2, 4), weight=1)
        main_frame.grid_columnconfigure((1, 3), weight=0)

        left_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self._create_einsatzzentrale_widgets(left_frame)

        separator1 = customtkinter.CTkFrame(main_frame, width=2, fg_color=COLOR_GREEN)
        separator1.grid(row=0, column=1, sticky="ns", pady=10)

        middle_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        middle_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self._create_gdv_bayern_widgets(middle_frame)

        separator2 = customtkinter.CTkFrame(main_frame, width=2, fg_color=COLOR_GREEN)
        separator2.grid(row=0, column=3, sticky="ns", pady=10)

        right_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        right_frame.grid(row=0, column=4, sticky="nsew", padx=10, pady=10)
        self._create_bus_widgets(right_frame)
        
        self._create_action_buttons(self)

    def _load_vehicle_data(self):
        try:
            # Ersetzt Firebase durch lokale Daten
            local_vehicle_data = [
                {"brand": "Volkswagen", "models": ["Golf", "Passat", "Tiguan", "Polo", "T-Roc", "Touran"]},
                {"brand": "Audi", "models": ["A3", "A4", "A6", "Q3", "Q5", "e-tron"]},
                {"brand": "Skoda", "models": ["Octavia", "Fabia", "Kodiaq", "Superb", "Enyaq"]},
                {"brand": "Seat", "models": ["Leon", "Ibiza", "Ateca", "Arona"]},
                {"brand": "Cupra", "models": ["Formentor", "Born", "Leon", "Ateca"]},
                {"brand": "MAN", "models": ["TGX", "TGS", "TGL", "TGM"]},
                {"brand": "Mercedes-Benz", "models": ["Actros", "Arocs", "Atego", "eActros"]},
                {"brand": "Scania", "models": ["R-Series", "S-Series", "G-Series"]},
            ]
            self.vehicle_data = local_vehicle_data
            brand_set = set(v['brand'] for v in self.vehicle_data)
            self.brand_names = sorted(list(brand_set))
            print("Fahrzeugdaten erfolgreich lokal für KilianForm geladen.")
        except Exception as e:
            print(f"Fehler beim Laden der lokalen Fahrzeugdaten: {e}")
            self.vehicle_data = []
            self.brand_names = []

    def _create_section_label(self, parent, text, anchor="w"):
        label = customtkinter.CTkLabel(parent, text=text, font=("Calibri", 18, "bold", "underline"), anchor=anchor, text_color=COLOR_GREEN)
        label.pack(fill="x", pady=(5, 10), padx=5)

    def _create_einsatzzentrale_widgets(self, parent):
        self._create_section_label(parent, "Annahme Einsatzzentrale")
        frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=5)

        customtkinter.CTkLabel(frame, text="Auftraggeber:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkLabel(frame, text="Polizei Verwahrstelle", anchor="w")
        w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.einsatzzentrale_fields["Auftraggeber"] = w

        customtkinter.CTkLabel(frame, text="Auftragsart:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["VV Vereinfachtes Verfahren", "Polizei vor Ort", "Sicherstellung"], fg_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.einsatzzentrale_fields["Auftragsart"] = w

        customtkinter.CTkLabel(frame, text="In Vertretung:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Nein", "Ja"], fg_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN); w.set("Nein"); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.einsatzzentrale_fields["In Vertretung"] = w

        customtkinter.CTkLabel(frame, text="Fahrzeug:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        brand_combo = customtkinter.CTkComboBox(frame, values=self.brand_names, command=self._on_ez_brand_change, width=250, border_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN)
        brand_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w"); brand_combo.set("")
        brand_combo.bind("<KeyRelease>", self._on_ez_brand_change)
        self.einsatzzentrale_fields["Fahrzeug"] = brand_combo
        self.ez_brand_combo = brand_combo

        customtkinter.CTkLabel(frame, text="Modell:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        model_combo = customtkinter.CTkComboBox(frame, values=[""], state="disabled", width=250, border_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN)
        model_combo.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        model_combo.bind("<KeyRelease>", self._on_ez_model_change)
        self.einsatzzentrale_fields["Modell"] = model_combo
        self.ez_model_combo = model_combo

        customtkinter.CTkLabel(frame, text="Kennzeichen:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=250); w.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.einsatzzentrale_fields["Kennzeichen"] = w

        customtkinter.CTkLabel(frame, text="Annahmezeit:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, placeholder_text="HH:MM", border_color=COLOR_GREEN, width=250); w.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.einsatzzentrale_fields["Annahmezeit"] = w

        customtkinter.CTkLabel(frame, text="Einsatzort:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=250); w.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        self.einsatzzentrale_fields["Einsatzort"] = w

        customtkinter.CTkLabel(frame, text="Verbringungsort:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkLabel(frame, text="Verwahrstelle", anchor="w"); w.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        self.einsatzzentrale_fields["Verbringungsort"] = w

        button_container = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_container.pack(pady=20, padx=5)
        customtkinter.CTkButton(button_container, text="Kopieren", command=self.copy_einsatzzentrale, fg_color=COLOR_GREEN, hover_color=COLOR_HOVER_GREEN).pack(side="left", padx=5)
        customtkinter.CTkButton(button_container, text="Report", command=self.report_einsatzzentrale, fg_color=COLOR_GREEN, hover_color=COLOR_HOVER_GREEN).pack(side="left", padx=5)


    def _on_ez_brand_change(self, event_or_choice):
        current_value = self.ez_brand_combo.get()
        filtered_brands = [b for b in self.brand_names if b.lower().startswith(current_value.lower())]
        self.ez_brand_combo.configure(values=filtered_brands)

        if current_value in self.brand_names:
            models = []
            for item in self.vehicle_data:
                if item["brand"] == current_value:
                    models = sorted(item["models"])
                    break
            self.current_ez_brand_models = models
            if self.ez_model_combo.cget("state") == "disabled":
                self.ez_model_combo.configure(state="normal")
            self.ez_model_combo.configure(values=self.current_ez_brand_models)
        else:
            self.current_ez_brand_models = []
            self.ez_model_combo.configure(values=[], state="disabled")
            self.ez_model_combo.set("")

    def _on_ez_model_change(self, event):
        current_value = self.ez_model_combo.get()
        filtered_models = [m for m in self.current_ez_brand_models if m.lower().startswith(current_value.lower())]
        self.ez_model_combo.configure(values=filtered_models)

    def _create_gdv_bayern_widgets(self, parent):
        self._create_section_label(parent, "Annahme GDV Bayern")
        frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=5)

        customtkinter.CTkLabel(frame, text="Vorgangsnummer:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=250); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.gdv_fields["Vorgangsnummer"] = w

        customtkinter.CTkLabel(frame, text="Auftragsart:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Panne", "Unfall", "Sicherstellung"], fg_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.gdv_fields["Auftragsart"] = w

        customtkinter.CTkLabel(frame, text="Fahrzeug:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=250); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.gdv_fields["Fahrzeug"] = w

        customtkinter.CTkLabel(frame, text="Kennzeichen:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=250); w.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.gdv_fields["Kennzeichen"] = w
        
        customtkinter.CTkLabel(frame, text="Mit Kran:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Nein", "Ja"], fg_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN); w.set("Nein"); w.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.gdv_fields["Mit Kran"] = w

        customtkinter.CTkLabel(frame, text="Einsatzort:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=250); w.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.gdv_fields["Einsatzort"] = w

        button_container = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_container.pack(pady=20, padx=5)
        customtkinter.CTkButton(button_container, text="Kopieren", command=self.copy_gdv, fg_color=COLOR_GREEN, hover_color=COLOR_HOVER_GREEN).pack(side="left", padx=5)
        customtkinter.CTkButton(button_container, text="Report", command=self.report_gdv, fg_color=COLOR_GREEN, hover_color=COLOR_HOVER_GREEN).pack(side="left", padx=5)


    def _create_bus_widgets(self, parent):
        self._create_section_label(parent, "Annahme Bus & LKW")
        frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=5)

        customtkinter.CTkLabel(frame, text="Auftraggeber:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        auftraggeber_values = ["", "MVG Bus Betriebshof Moosach", "MVG Bus Betriebshof Ost", "Autobus Oberbayern", "Scania München/Oberschleißheim", "MAN Neufahrn"]
        w = customtkinter.CTkComboBox(frame, values=auftraggeber_values, border_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN, width=300); w.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Auftraggeber"] = w

        customtkinter.CTkLabel(frame, text="Auftragsart:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Panne", "Unfall"], fg_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN); w.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Auftragsart"] = w

        customtkinter.CTkLabel(frame, text="Bus Modell:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Solo bus", "Gelenkbus", "Elektro Bus", "Zugmaschine + Aufliger", "Zugmaschine Solo"], fg_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Bus Modell"] = w

        customtkinter.CTkLabel(frame, text="Kennzeichen:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=300); w.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Kennzeichen"] = w

        customtkinter.CTkLabel(frame, text="Schaden:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=300); w.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Schaden"] = w

        customtkinter.CTkLabel(frame, text="Ansprechpartner:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=300); w.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Ansprechpartner"] = w

        customtkinter.CTkLabel(frame, text="Telefonnummer:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=300); w.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Telefonnummer"] = w

        customtkinter.CTkLabel(frame, text="Pannenort:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_GREEN, width=300); w.grid(row=7, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Pannenort"] = w

        customtkinter.CTkLabel(frame, text="Verbringungsort:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        verbringungsort_values = [
            "", "Hanauer Str. 24, 80992 München | MVG Bus Betriebshof Moosach",
            "Truderinger Str. 2, 81677 München | MVG Bus Betriebshof Ost",
            "Heidemannstraße 220, 80939 München | Autobus Oberbayern",
            "Waldmeisterstraße 84, 80935 München | Autobus Oberbayern",
            "Hicklstr. 4, 85764 Oberschleißheim | Scania München/Oberschleißheim",
            "Philipp-Reis-Straße 3, 85375 Neufahrn bei Freising | MAN Neufahrn"
        ]
        w = customtkinter.CTkComboBox(frame, values=verbringungsort_values, border_color=COLOR_GREEN, button_color=COLOR_GREEN, button_hover_color=COLOR_HOVER_GREEN, width=300); w.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        self.bus_fields["Verbringungsort"] = w

        button_container = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_container.pack(pady=20, padx=5)
        customtkinter.CTkButton(button_container, text="Kopieren", command=self.copy_bus, fg_color=COLOR_GREEN, hover_color=COLOR_HOVER_GREEN).pack(side="left", padx=5)
        customtkinter.CTkButton(button_container, text="Report", command=self.report_bus, fg_color=COLOR_GREEN, hover_color=COLOR_HOVER_GREEN).pack(side="left", padx=5)


    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=5, sticky="ew", padx=10, pady=(10, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        
        center_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        center_frame.pack()
        
        customtkinter.CTkButton(center_frame, text="Zurücksetzen", command=self.reset_form, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Schließen", command=self.destroy, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def reset_form(self):
        # Alle drei Field-Dictionaries durchgehen
        for field_dict in [self.einsatzzentrale_fields, self.gdv_fields, self.bus_fields]:
            for widget in field_dict.values():
                if isinstance(widget, customtkinter.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, customtkinter.CTkOptionMenu):
                    widget.set(widget.cget("values")[0])
                elif isinstance(widget, customtkinter.CTkComboBox):
                    widget.set(widget.cget("values")[0]) # Setzt auf leeren String oder ersten Wert
        
        # Spezielles Reset für Fahrzeug/Modell in Einsatzzentrale
        self.ez_brand_combo.set("")
        self.ez_brand_combo.configure(values=self.brand_names)
        self._on_ez_brand_change(None)

    def _get_field_value(self, field_dict, label):
        if label not in field_dict: return ""
        widget = field_dict[label]
        value = ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)):
            value = widget.get()
        elif isinstance(widget, customtkinter.CTkEntry):
            value = widget.get()
        elif isinstance(widget, customtkinter.CTkLabel):
            value = widget.cget("text")
        return value.strip()

    def copy_einsatzzentrale(self):
        output_lines = []
        ordered_keys = ["Auftraggeber", "Auftragsart", "In Vertretung", "Fahrzeug", "Modell", "Kennzeichen", "Annahmezeit", "Einsatzort"]
        
        data_to_copy = []
        for key in ordered_keys:
            value = self._get_field_value(self.einsatzzentrale_fields, key)
            if value and (key != "In Vertretung" or value != "Nein"):
                data_to_copy.append(f"{key}: {value}")
        
        if data_to_copy:
            data_to_copy.append(f"Verbringungsort: {self._get_field_value(self.einsatzzentrale_fields, 'Verbringungsort')}")
            
        if data_to_copy:
            output_lines.extend(data_to_copy)

            final_text = "\n".join(output_lines)
            self.clipboard_clear()
            self.clipboard_append(final_text)
            print("Folgender Text wurde kopiert:\n" + final_text)

    def copy_gdv(self):
        output_lines = []
        ordered_keys = ["Vorgangsnummer", "Auftragsart", "Fahrzeug", "Kennzeichen", "Mit Kran", "Einsatzort"]
        
        data_to_copy = []
        for key in ordered_keys:
            value = self._get_field_value(self.gdv_fields, key)
            if value:
                data_to_copy.append(f"{key}: {value}")
        
        if data_to_copy:
            output_lines.append("Auftraggeber: GDV Bayern")
            output_lines.append("")
            output_lines.extend(data_to_copy)

            final_text = "\n".join(output_lines)
            self.clipboard_clear()
            self.clipboard_append(final_text)
            print("Folgender Text wurde kopiert:\n" + final_text)

    def copy_bus(self):
        output_lines = []
        ordered_keys = [
            "Auftraggeber", "Auftragsart", "Bus Modell", "Kennzeichen", 
            "Schaden", "Ansprechpartner", "Telefonnummer", "Pannenort", "Verbringungsort"
        ]
        
        data_to_copy = []
        auftraggeber = self._get_field_value(self.bus_fields, "Auftraggeber")
        if auftraggeber:
            output_lines.append(f"Auftraggeber: {auftraggeber}")
            output_lines.append("")

        for key in ordered_keys:
            if key == "Auftraggeber": continue
            value = self._get_field_value(self.bus_fields, key)
            if value:
                data_to_copy.append(f"{key}: {value}")
        
        if data_to_copy:
            output_lines.extend(data_to_copy)
            final_text = "\n".join(output_lines)
            self.clipboard_clear()
            self.clipboard_append(final_text)
            print("Folgender Text wurde kopiert:\n" + final_text)

    def report_einsatzzentrale(self):
        name = self._get_field_value(self.einsatzzentrale_fields, 'Auftraggeber')
        annahmezeit = self._get_field_value(self.einsatzzentrale_fields, 'Annahmezeit')
        einsatzort = self._get_field_value(self.einsatzzentrale_fields, 'Einsatzort')
        fahrzeug = self._get_field_value(self.einsatzzentrale_fields, 'Fahrzeug')
        modell = self._get_field_value(self.einsatzzentrale_fields, 'Modell')
        fzg_marke = f"{fahrzeug} {modell}".strip()
        kennzeichen = self._get_field_value(self.einsatzzentrale_fields, 'Kennzeichen')
        auftragsart = self._get_field_value(self.einsatzzentrale_fields, 'Auftragsart')
        verbringungsort = self._get_field_value(self.einsatzzentrale_fields, 'Verbringungsort')

        # Excel-Format mit Tabulatoren
        final_text = f"{name}\t{annahmezeit}\t{einsatzort}\t{fzg_marke}\t{kennzeichen}\t{auftragsart}\t{verbringungsort}"
        
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Einsatzzentrale Report wurde kopiert:\n" + final_text)

    def report_gdv(self):
        name = "GDV Bayern"
        vorgangsnummer = self._get_field_value(self.gdv_fields, 'Vorgangsnummer')
        einsatzort = self._get_field_value(self.gdv_fields, 'Einsatzort')
        fzg_marke = self._get_field_value(self.gdv_fields, 'Fahrzeug')
        kennzeichen = self._get_field_value(self.gdv_fields, 'Kennzeichen')
        auftragsart = self._get_field_value(self.gdv_fields, 'Auftragsart')
        
        # Excel-Format mit Tabulatoren
        final_text = f"{name}\t\t{einsatzort}\t{fzg_marke}\t{kennzeichen}\t{auftragsart}\t\t{vorgangsnummer}"

        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("GDV Report wurde kopiert:\n" + final_text)

    def report_bus(self):
        auftraggeber = self._get_field_value(self.bus_fields, 'Auftraggeber')
        pannenort = self._get_field_value(self.bus_fields, 'Pannenort')
        fzg_marke = self._get_field_value(self.bus_fields, 'Bus Modell')
        kennzeichen = self._get_field_value(self.bus_fields, 'Kennzeichen')
        schaden = self._get_field_value(self.bus_fields, 'Schaden')
        verbringungsort = self._get_field_value(self.bus_fields, 'Verbringungsort')

        # Excel-Format mit Tabulatoren
        final_text = f"{auftraggeber}\t\t{pannenort}\t{fzg_marke}\t{kennzeichen}\t{schaden}\t{verbringungsort}"

        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Bus & LKW Report wurde kopiert:\n" + final_text)


class RudolphForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Annahme Rudolph")
        self.geometry("800x850")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)

        self.fahrer_list = sorted(["22er", "23er", "26er", "33er", "34er", "38er", "39er", "40er", "41er", "42er", "43er", "45er", "48er", "54er", "56er", "59er", "65er", "66er", "69er"])
        self.fahrer_telefonbuch = {
            "22er": "491708285284", "23er": "491708285285", "26er": "491708285287",
            "33er": "491708285289", "34er": "491708285290", "38er": "491708285291",
            "39er": "491708285292", "40er": "491708285293", "41er": "491708285299",
            "42er": "491708285300", "43er": "491708285301", "45er": "491708285296",
            "48er": "491708285288", "54er": "491708285302", "56er": "491708285295",
            "59er": "491708285294", "65er": "491708285297", "66er": "491708285298",
            "69er": "491708285286"
        }
        self.fubz_anrufer_list = sorted([
            "Akyüreck", "Antoch", "Bähring", "Bauch", "Böckh", "Bohn", "Cetin", "Cybulla", 
            "Diecow", "Erbert", "Evert", "Forstreuter", "Fricke", "Genge", "Gierow", 
            "Görülü", "Guttmann", "Hammer", "Hentschke", "Herrmann", "Hertwig", "Idziak", 
            "Jeckel", "Kandziorra", "Kawrewksk", "Kipphahn", "Kleineberg", "Krause", 
            "Kühnel", "Landweer", "Leege", "Lehmann", "Manthei", "Mollack", "Narim", 
            "Nehls", "Reineke", "Runge", "Sander", "Scheerer", "Scherf", "Schiller", 
            "Schönfelder", "Schröder", "Schrom", "Schulz", "Schwarzlose", "Steinbeck", 
            "Steinberg", "Tebert", "Walther", "Waßmuth", "Wawrzinek", "Wessolek", "Wolf", 
            "Zajac", "Zebek", "Zimmer", "Zimmermann"
        ])
        self.fubz_los_list = [
            "Los 3 - Bezirk Pankow", "Los 3 - Bezirk Mitte", "Los 3 - Bezirk Friedrichshain-Kreuzberg",
            "Los 3 - Bezirk Lichtenberg / Los B - Bezirk Pankow", "Los B - Bezirk Lichtenberg",
            "Los B - Bezirk Marzahn-Hellersdorf"
        ]
        self.bvg_los_list = [
            "Los 6N - Bezirk Pankow-Nord", "Los 6 - Bezirk Pankow-Süd", "Los 7 - Bezirk Lichtenberg",
            "Los 8 - Bezirk Friedrichshain | Kreuzberg", "Los 9 - Bezirk Marzahn | Hellersdorf"
        ]

        self.fubz_fields = {}
        self.fubz_sicherstellung_widgets = []
        self.fubz_rolle_neu_widgets = []
        self.bvg_fields = {}

        self.auftraggeber_type = tkinter.StringVar(value="FUBZ")
        self.fubz_auftragsart = tkinter.StringVar(value="Rolle Neu")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        top_frame = customtkinter.CTkFrame(main_frame, fg_color=COLOR_BLACK, corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)
        
        top_inner_frame = customtkinter.CTkFrame(top_frame, fg_color="transparent")
        top_inner_frame.pack(pady=10, padx=20, fill="x")
        
        customtkinter.CTkLabel(top_inner_frame, text="Auftraggeber:", font=("Calibri", 16, "bold")).pack(side="left")
        customtkinter.CTkRadioButton(top_inner_frame, text="FUBZ | Ausfast", variable=self.auftraggeber_type, value="FUBZ", command=self._switch_main_form, fg_color=COLOR_PURPLE, hover_color=COLOR_HOVER_PURPLE, font=("Calibri", 14, "bold")).pack(side="left", padx=15)
        customtkinter.CTkRadioButton(top_inner_frame, text="BVG", variable=self.auftraggeber_type, value="BVG", command=self._switch_main_form, fg_color=COLOR_PURPLE, hover_color=COLOR_HOVER_PURPLE, font=("Calibri", 14, "bold")).pack(side="left", padx=15)

        self.fubz_container = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        self.bvg_container = customtkinter.CTkFrame(main_frame, fg_color="transparent")

        self._create_fubz_widgets(self.fubz_container)
        self._create_bvg_widgets(self.bvg_container)
        
        self._create_action_buttons(main_frame)

        self._switch_main_form()

    def _create_fubz_widgets(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        fubz_type_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        fubz_type_frame.grid(row=0, column=0, pady=(10,0), padx=0, sticky="ew")
        customtkinter.CTkLabel(fubz_type_frame, text="Auftragsart:", font=("Calibri", 14, "bold")).pack(side="left", padx=(0, 10))
        customtkinter.CTkRadioButton(fubz_type_frame, text="Rolle Neu | Umsetzung", variable=self.fubz_auftragsart, value="Rolle Neu", command=self._switch_fubz_form, fg_color=COLOR_PURPLE, hover_color=COLOR_HOVER_PURPLE).pack(side="left", padx=10)
        customtkinter.CTkRadioButton(fubz_type_frame, text="Sicherstellung", variable=self.fubz_auftragsart, value="Sicherstellung", command=self._switch_fubz_form, fg_color=COLOR_PURPLE, hover_color=COLOR_HOVER_PURPLE).pack(side="left", padx=10)
        
        scrollable_frame = customtkinter.CTkScrollableFrame(parent, fg_color="transparent", label_text="FUBZ | Ausfast Details", label_text_color=COLOR_PURPLE)
        scrollable_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        row_counter = 0
        
        customtkinter.CTkLabel(scrollable_frame, text="Auftraggeber:").grid(row=row_counter, column=0, padx=5, pady=8, sticky="w")
        w_auftraggeber = customtkinter.CTkLabel(scrollable_frame, text="FUBZ | Ausfast", font=("Calibri", 14))
        w_auftraggeber.grid(row=row_counter, column=1, padx=5, pady=8, sticky="w")
        self.fubz_fields["Auftraggeber"] = w_auftraggeber
        row_counter += 1

        customtkinter.CTkLabel(scrollable_frame, text="Anrufer:").grid(row=row_counter, column=0, padx=5, pady=8, sticky="w")
        w_anrufer = customtkinter.CTkComboBox(scrollable_frame, values=[""] + self.fubz_anrufer_list, border_color=COLOR_PURPLE, button_color=COLOR_PURPLE, button_hover_color=COLOR_HOVER_PURPLE, width=300)
        w_anrufer.grid(row=row_counter, column=1, padx=5, pady=8, sticky="w")
        self.fubz_fields["Anrufer"] = w_anrufer
        row_counter += 1

        labels_part1 = ["Anrufzeit", "Los", "Fahrzeug", "Kennzeichen", "Anzahl der Fahrzeuge", "Einsatzort"]
        for label_text in labels_part1:
            label = customtkinter.CTkLabel(scrollable_frame, text=f"{label_text}:")
            label.grid(row=row_counter, column=0, padx=5, pady=8, sticky="w")
            if label_text == "Los":
                w = customtkinter.CTkComboBox(scrollable_frame, values=[""] + self.fubz_los_list, border_color=COLOR_PURPLE, button_color=COLOR_PURPLE, button_hover_color=COLOR_HOVER_PURPLE, width=300)
            else:
                w = customtkinter.CTkEntry(scrollable_frame, border_color=COLOR_PURPLE, width=300)
            w.grid(row=row_counter, column=1, padx=5, pady=8, sticky="w")
            self.fubz_fields[label_text] = w
            
            if label_text == "Anzahl der Fahrzeuge":
                self.fubz_rolle_neu_widgets.extend([label, w])

            row_counter += 1
            
        label_zielort = customtkinter.CTkLabel(scrollable_frame, text="Zielort:")
        entry_zielort = customtkinter.CTkEntry(scrollable_frame, border_color=COLOR_PURPLE, width=300)
        label_zielort.grid(row=row_counter, column=0, padx=5, pady=8, sticky="w")
        entry_zielort.grid(row=row_counter, column=1, padx=5, pady=8, sticky="w")
        self.fubz_fields["Zielort"] = entry_zielort
        self.fubz_sicherstellung_widgets.extend([label_zielort, entry_zielort])
        row_counter += 1

        labels_part2 = ["Uhrzeit der Weiterleitung an Fahrer", "Fahrer"]
        for label_text in labels_part2:
            customtkinter.CTkLabel(scrollable_frame, text=f"{label_text}:").grid(row=row_counter, column=0, padx=5, pady=8, sticky="w")
            if label_text == "Fahrer":
                w = customtkinter.CTkOptionMenu(scrollable_frame, values=["Bitte Wählen"] + self.fahrer_list, fg_color=COLOR_PURPLE, button_color=COLOR_PURPLE, button_hover_color=COLOR_HOVER_PURPLE, width=300); w.set("Bitte Wählen")
            else:
                w = customtkinter.CTkEntry(scrollable_frame, border_color=COLOR_PURPLE, width=300)
            w.grid(row=row_counter, column=1, padx=5, pady=8, sticky="w")
            self.fubz_fields[label_text] = w
            row_counter += 1

        sicherstellung_labels_rest = ["Listen Nummer", "Grüne Punkt Nummer"]
        for label_text in sicherstellung_labels_rest:
            label = customtkinter.CTkLabel(scrollable_frame, text=f"{label_text}:")
            entry = customtkinter.CTkEntry(scrollable_frame, border_color=COLOR_PURPLE, width=300)
            label.grid(row=row_counter, column=0, padx=5, pady=8, sticky="w")
            entry.grid(row=row_counter, column=1, padx=5, pady=8, sticky="w")
            self.fubz_fields[label_text] = entry
            self.fubz_sicherstellung_widgets.extend([label, entry])
            row_counter += 1
        
        self._switch_fubz_form()

    def _create_bvg_widgets(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        scrollable_frame = customtkinter.CTkScrollableFrame(parent, fg_color="transparent", label_text="BVG Details", label_text_color=COLOR_PURPLE)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=10)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        bvg_layout = [
            ("Auftraggeber:", {"type": "label", "text": "BVG"}),
            ("Auftragart:", {"type": "label", "text": "Umsetzung"}),
            ("Anrufer:", {"type": "combobox", "values": self.fubz_anrufer_list}),
            ("Los:", {"type": "combobox", "values": self.bvg_los_list}),
            ("Anrufzeit:", {"type": "entry"}),
            ("Fahrzeug:", {"type": "entry"}),
            ("Kennzeichen:", {"type": "entry"}),
            ("Anzahl der Fahrzeuge:", {"type": "entry"}),
            ("Einsatzort:", {"type": "entry"}),
            ("Fahrer:", {"type": "menu", "values": self.fahrer_list}),
            ("Uhrzeit der Weiterleitung an Fahrer:", {"type": "entry"})
        ]

        for row, (label_text, config) in enumerate(bvg_layout):
            customtkinter.CTkLabel(scrollable_frame, text=label_text).grid(row=row, column=0, padx=5, pady=8, sticky="w")
            widget_type = config.get("type")
            
            if widget_type == "label":
                w = customtkinter.CTkLabel(scrollable_frame, text=config.get("text", ""), font=("Calibri", 14))
            elif widget_type == "menu":
                options = ["Bitte Wählen"] + config.get("values", [])
                w = customtkinter.CTkOptionMenu(scrollable_frame, values=options, fg_color=COLOR_PURPLE, button_color=COLOR_PURPLE, button_hover_color=COLOR_HOVER_PURPLE, width=300)
                w.set(options[0])
            elif widget_type == "combobox":
                options = [""] + config.get("values", [])
                w = customtkinter.CTkComboBox(scrollable_frame, values=options, border_color=COLOR_PURPLE, button_color=COLOR_PURPLE, button_hover_color=COLOR_HOVER_PURPLE, width=300)
            else:
                w = customtkinter.CTkEntry(scrollable_frame, border_color=COLOR_PURPLE, width=300)
            
            w.grid(row=row, column=1, padx=5, pady=8, sticky="w")
            self.bvg_fields[label_text.strip(":")] = w

    def _switch_main_form(self):
        if self.auftraggeber_type.get() == "FUBZ":
            self.bvg_container.grid_forget()
            self.fubz_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        else:
            self.fubz_container.grid_forget()
            self.bvg_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)

    def _switch_fubz_form(self):
        is_sicherstellung = self.fubz_auftragsart.get() == "Sicherstellung"
        for widget in self.fubz_sicherstellung_widgets:
            if is_sicherstellung:
                widget.grid()
            else:
                widget.grid_remove()
        
        for widget in self.fubz_rolle_neu_widgets:
            if not is_sicherstellung:
                widget.grid()
            else:
                widget.grid_remove()

    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        button_frame.grid_columnconfigure(0, weight=1)
        center_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent"); center_frame.pack()
        
        try:
            whatsapp_image_data = Image.open(resource_path("whatsapp_icon.png"))
            whatsapp_image = customtkinter.CTkImage(light_image=whatsapp_image_data, dark_image=whatsapp_image_data, size=(20, 20))
            customtkinter.CTkButton(center_frame, text="Auftrag an Fahrer senden", image=whatsapp_image, compound="left", command=self.send_whatsapp_message, height=35, font=("Calibri", 14, "bold"), fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)
        except (FileNotFoundError, UnidentifiedImageError, tkinter.TclError):
            print("WhatsApp Icon konnte nicht geladen werden, Button wird ohne Icon angezeigt.")
            customtkinter.CTkButton(center_frame, text="Auftrag an Fahrer senden", command=self.send_whatsapp_message, height=35, font=("Calibri", 14, "bold"), fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)

        customtkinter.CTkButton(center_frame, text="Kopieren", command=self.copy_to_clipboard, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_PURPLE, hover_color=COLOR_HOVER_PURPLE).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Report", command=self.report, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_PURPLE, hover_color=COLOR_HOVER_PURPLE).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Zurücksetzen", command=self.reset_form, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Schließen", command=self.destroy, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def reset_form(self):
        # FUBZ- und BVG-Felder zurücksetzen
        for field_dict in [self.fubz_fields, self.bvg_fields]:
            for widget in field_dict.values():
                if isinstance(widget, customtkinter.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, customtkinter.CTkOptionMenu):
                    widget.set(widget.cget("values")[0])
                elif isinstance(widget, customtkinter.CTkComboBox):
                    widget.set(widget.cget("values")[0])
        
        # Radiobuttons auf Standard zurücksetzen
        self.auftraggeber_type.set("FUBZ")
        self.fubz_auftragsart.set("Rolle Neu")
        self._switch_main_form()
        self._switch_fubz_form()

    def _get_field_value(self, field_dict, label):
        if label not in field_dict: return ""
        widget = field_dict[label]
        value = ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)):
            value = widget.get()
            if value == "Bitte Wählen": value = ""
        elif isinstance(widget, customtkinter.CTkEntry):
            value = widget.get()
        elif isinstance(widget, customtkinter.CTkLabel):
            value = widget.cget("text")
        return value.strip()

    def _generate_copy_text(self):
        if self.auftraggeber_type.get() == "FUBZ":
            return self._generate_fubz_text()
        else:
            return self._generate_bvg_text()

    def _generate_fubz_text(self):
        form_type = self.fubz_auftragsart.get()
        output_lines = []
        data_to_copy = {key: self._get_field_value(self.fubz_fields, key) for key in self.fubz_fields}

        if form_type == "Rolle Neu":
            output_lines.extend(["Auftraggeber: FUBZ | Ausfast", "", "Auftragsart: Rolle Neu | Umsetzung"])
            order = ["Anrufer", "Anrufzeit", "Los", "Fahrzeug", "Kennzeichen", "Anzahl der Fahrzeuge", "Einsatzort"]
            for key in order:
                if data_to_copy.get(key): output_lines.append(f"{key}: {data_to_copy[key]}")
            output_lines.append("")
            order_after = ["Fahrer", "Uhrzeit der Weiterleitung an Fahrer"]
            for key in order_after:
                if data_to_copy.get(key): output_lines.append(f"{key}: {data_to_copy[key]}")
        elif form_type == "Sicherstellung":
            output_lines.extend(["Auftraggeber: FUBZ | Ausfast", "", "Auftragsart: Sicherstellung"])
            order = ["Anrufer", "Anrufzeit", "Los", "Fahrzeug", "Kennzeichen", "Einsatzort", "Zielort"]
            for key in order:
                if data_to_copy.get(key): output_lines.append(f"{key}: {data_to_copy[key]}")
            output_lines.append("")
            order_after = ["Fahrer", "Uhrzeit der Weiterleitung an Fahrer", "Listen Nummer", "Grüne Punkt Nummer"]
            for key in order_after:
                if data_to_copy.get(key): output_lines.append(f"{key}: {data_to_copy[key]}")
        
        return "\n".join(output_lines)

    def _generate_bvg_text(self):
        output_lines = []
        data_to_copy = {key: self._get_field_value(self.bvg_fields, key) for key in self.bvg_fields}

        output_lines.append("Auftraggeber: BVG\n")
        group1 = ["Auftragart", "Los", "Anrufer", "Anrufzeit"]
        for key in group1:
            if data_to_copy.get(key): output_lines.append(f"{key}: {data_to_copy[key]}")
        output_lines.append("")

        group2 = ["Fahrzeug", "Kennzeichen", "Anzahl der Fahrzeuge"]
        for key in group2:
            if data_to_copy.get(key): output_lines.append(f"{key}: {data_to_copy[key]}")
        output_lines.append("")

        group3 = ["Fahrer", "Uhrzeit der Weiterleitung an Fahrer"]
        for key in group3:
            if data_to_copy.get(key): output_lines.append(f"{key}: {data_to_copy[key]}")
        output_lines.append("")

        if data_to_copy.get("Einsatzort"): output_lines.append(f"Einsatzort: {data_to_copy['Einsatzort']}")
        return "\n".join(output_lines)

    def copy_to_clipboard(self):
        final_text = self._generate_copy_text()
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Folgender Text wurde kopiert:\n" + final_text)

    def send_whatsapp_message(self):
        active_fields = self.bvg_fields if self.auftraggeber_type.get() == "BVG" else self.fubz_fields
        fahrer = self._get_field_value(active_fields, "Fahrer")
        
        if not fahrer or fahrer == "Bitte Wählen":
            print("Fehler: Bitte zuerst einen Fahrer auswählen.")
            return

        phone_number = self.fahrer_telefonbuch.get(fahrer)
        if not phone_number:
            print(f"Fehler: Keine Telefonnummer für Fahrer '{fahrer}' hinterlegt.")
            return

        message = self._generate_copy_text()
        encoded_message = quote(message)
        
        url = f"https.me/{phone_number}?text={encoded_message}"
        
        webbrowser.open(url)
        print(f"WhatsApp-Link für Fahrer {fahrer} geöffnet.")

    def report(self):
        report_parts = []
        if self.auftraggeber_type.get() == "BVG":
            data = self.bvg_fields
            anrufer = self._get_field_value(data, "Anrufer"); anrufzeit = self._get_field_value(data, "Anrufzeit")
            los = self._get_field_value(data, "Los"); fahrzeug = self._get_field_value(data, "Fahrzeug")
            anzahl = self._get_field_value(data, "Anzahl der Fahrzeuge"); einsatzort = self._get_field_value(data, "Einsatzort")
            
            report_parts = [f"Anrufer: {anrufer}", f"Anrufzeit: {anrufzeit}", f"Los: {los}", f"Fahrzeug: {fahrzeug}", f"Anzahl: {anzahl}", f"Einsatzort: {einsatzort}", f"{einsatzort}"]
        elif self.auftraggeber_type.get() == "FUBZ":
            data = self.fubz_fields
            form_type = self.fubz_auftragsart.get()
            
            anrufer = self._get_field_value(data, "Anrufer"); anrufzeit = self._get_field_value(data, "Anrufzeit")
            los = self._get_field_value(data, "Los"); fahrzeug = self._get_field_value(data, "Fahrzeug")
            anzahl = self._get_field_value(data, "Anzahl der Fahrzeuge"); einsatzort = self._get_field_value(data, "Einsatzort")

            report_parts = [f"Anrufer: {anrufer}", f"Anrufzeit: {anrufzeit}", f"Los: {los}", f"Fahrzeug: {fahrzeug}"]
            if form_type == "Rolle Neu":
                report_parts.append(f"Anzahl: {anzahl}")
            
            report_parts.extend([f"Einsatzort: {einsatzort}", f"{einsatzort}"])
            
            if form_type == "Sicherstellung":
                zielort = self._get_field_value(data, "Zielort"); listen_nr = self._get_field_value(data, "Listen Nummer")
                punkt_nr = self._get_field_value(data, "Grüne Punkt Nummer")
                report_parts.extend([f"Zielort: {zielort}", f"Nummer: {listen_nr}", f"Nummer: {punkt_nr}"])

        final_text = " | ".join(filter(lambda x: ': ' in x and x.split(': ')[1], report_parts))
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Folgender Report wurde kopiert:\n" + final_text)


class WehnerForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Annahme Wehner Motors")
        self.geometry("1600x950")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)

        # Data
        self.pkw_fields = {}
        self.pkw_dynamic_widgets = {}
        self.polizei_fields = {}
        self.lkw_fields = {}
        self.oelspur_fields = {}
        self.fahrer_fields = {}
        self.section_checkboxes = {}

        self.fahrer_list = sorted([
            "Marco Auth", "Thorsten Bech", "Nikolas Blum", "Viktor Greb", 
            "Markus Heller", "Mike Herbert", "Johann Martens", "Wehner Motors Notfallmanager", 
            "Alex Rizea", "Andre Sorg", "Thomas Stojanovski", "Jessica Stupp", 
            "Nino Unger", "Nicolas Wallentin Dispo/BL", "Nicolas Wehner GF", "Mario Zipper"
        ])
        self.fahrer_telefonbuch = {
            "Marco Auth": "4915129806716", "Thorsten Bech": "491719392100",
            "Nikolas Blum": "4915117647208", "Viktor Greb": "491709338889",
            "Markus Heller": "491753832420", "Mike Herbert": "4915158267501",
            "Johann Martens": "4915158267493", "Wehner Motors Notfallmanager": "49974281000",
            "Alex Rizea": "4917645776293", "Andre Sorg": "4916096227939",
            "Thomas Stojanovski": "4915167197630", "Jessica Stupp": "4915152252100",
            "Nino Unger": "491754167064", "Nicolas Wallentin Dispo/BL": "4915170610164",
            "Nicolas Wehner GF": "4915158267500", "Mario Zipper": "4917641019301"
        }

        # --- Layout ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure((0, 2, 4, 6), weight=1)
        main_frame.grid_columnconfigure((1, 3, 5), weight=0)
        
        pkw_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent")
        pkw_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self._create_pkw_widgets(pkw_frame)

        separator1 = customtkinter.CTkFrame(main_frame, width=2, fg_color=COLOR_ORANGE); separator1.grid(row=0, column=1, sticky="ns", pady=10)
        
        polizei_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent")
        polizei_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self._create_polizei_widgets(polizei_frame)
        
        separator2 = customtkinter.CTkFrame(main_frame, width=2, fg_color=COLOR_ORANGE); separator2.grid(row=0, column=3, sticky="ns", pady=10)
        
        lkw_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent")
        lkw_frame.grid(row=0, column=4, sticky="nsew", padx=10, pady=10)
        self._create_lkw_widgets(lkw_frame)

        separator3 = customtkinter.CTkFrame(main_frame, width=2, fg_color=COLOR_ORANGE); separator3.grid(row=0, column=5, sticky="ns", pady=10)
        
        oelspur_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent")
        oelspur_frame.grid(row=0, column=6, sticky="nsew", padx=10, pady=10)
        self._create_oelspur_widgets(oelspur_frame)

        self._create_action_buttons(self)

    def _create_section_header(self, parent, text, section_key):
        header_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 10), padx=5)

        label = customtkinter.CTkLabel(header_frame, text=text, font=("Calibri", 18, "bold", "underline"), anchor="w", text_color=COLOR_ORANGE)
        label.pack(side="left", fill="x", expand=True)
        
        checkbox = customtkinter.CTkCheckBox(header_frame, text="", border_color=COLOR_ORANGE, hover_color=COLOR_HOVER_ORANGE, fg_color=COLOR_ORANGE)
        checkbox.pack(side="right")
        self.section_checkboxes[section_key] = checkbox

    def _create_pkw_widgets(self, parent):
        self._create_section_header(parent, "Auftragsannahme PKW", "pkw")
        frame = customtkinter.CTkFrame(parent, fg_color="transparent"); frame.pack(fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)
        
        row_idx = 0

        auftraggeber_values = ["Privater Selbstzahler", "Autohaus Scheller", "deisenroth & soehne", "Atzert & Weber Autowelt Fulda", "Autohaus-Kircher-Ludwig Das Autohaus", "VW Notdienst", "Skoda Notdienst", "Seat Notdienst", "Audi Notdienst"]
        customtkinter.CTkLabel(frame, text="Auftraggeber:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkComboBox(frame, values=auftraggeber_values, border_color=COLOR_ORANGE, button_color=COLOR_ORANGE, button_hover_color=COLOR_HOVER_ORANGE, width=220); w.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.pkw_fields["Auftraggeber"] = w
        row_idx += 1

        customtkinter.CTkLabel(frame, text="Auftragsart:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Panne", "Unfall", "Mobi"], command=self._toggle_pkw_fields, fg_color=COLOR_ORANGE, button_color=COLOR_ORANGE, button_hover_color=COLOR_HOVER_ORANGE); w.grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")
        self.pkw_fields["Auftragsart"] = w
        row_idx += 1

        pkw_labels_1 = ["Anrufer", "Kunde vor Ort", "Telefonnummer", "Fahrzeug", "Modell", "Kennzeichen"]
        for text in pkw_labels_1:
            customtkinter.CTkLabel(frame, text=f"{text}:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
            self.pkw_fields[text] = w
            row_idx += 1
        
        mobi_labels = ["Fahrgestellnummer", "Erstzulassung", "KM-Stand"]
        for text in mobi_labels:
            l = customtkinter.CTkLabel(frame, text=f"{text}:"); l.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
            e = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); e.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
            self.pkw_fields[text] = e; self.pkw_dynamic_widgets[text] = (l, e)
            row_idx += 1
        
        customtkinter.CTkLabel(frame, text="Schaden:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.pkw_fields["Schaden"] = w
        row_idx += 1

        customtkinter.CTkLabel(frame, text="Pannen-/Unfallort:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.pkw_fields["Pannen-/Unfallort"] = w
        row_idx += 1

        verbringungsort_values = ["", "Autohaus Scheller : Dr.-Raabe-Straße 7, 36043 Fulda", "deisenroth & soehne | Volkswagen : Fuldaer Str. 8+11, 36088 Hünfeld", "Atzert & Weber Autowelt Fulda : Leipziger Str. 151, 36039 Fulda", "Autohaus-Kircher-Ludwig Das Autohaus : Dr.-Raabe-Straße 3, 36043 Fulda"]
        customtkinter.CTkLabel(frame, text="Verbringungsort:").grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkComboBox(frame, values=verbringungsort_values, border_color=COLOR_ORANGE, button_color=COLOR_ORANGE, button_hover_color=COLOR_HOVER_ORANGE); w.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.pkw_fields["Verbringungsort"] = w
        row_idx += 1

        l = customtkinter.CTkLabel(frame, text="Preisinfo:"); l.grid(row=row_idx, column=0, padx=5, pady=5, sticky="w")
        e = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); e.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
        self.pkw_fields["Preisinfo"] = e; self.pkw_dynamic_widgets["Preisinfo"] = (l, e)
        row_idx += 1
        
        self._toggle_pkw_fields()

    def _toggle_pkw_fields(self, auftragsart=None):
        if auftragsart is None:
            auftragsart = self.pkw_fields["Auftragsart"].get()

        is_mobi = auftragsart == "Mobi"
        for key in ["Fahrgestellnummer", "Erstzulassung", "KM-Stand"]:
            l, e = self.pkw_dynamic_widgets[key]
            if is_mobi: l.grid(); e.grid()
            else: l.grid_remove(); e.grid_remove()
        
        is_panne_unfall = auftragsart in ["Panne", "Unfall"]
        l, e = self.pkw_dynamic_widgets["Preisinfo"]
        if is_panne_unfall: l.grid(); e.grid()
        else: l.grid_remove(); e.grid_remove()

    def _create_polizei_widgets(self, parent):
        self._create_section_header(parent, "Polizei Auftrag", "polizei")
        frame = customtkinter.CTkFrame(parent, fg_color="transparent"); frame.pack(fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)

        labels = ["Auftraggeber", "Einsatznummer"]
        for i, text in enumerate(labels):
            customtkinter.CTkLabel(frame, text=f"{text}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.polizei_fields[text] = w

        customtkinter.CTkLabel(frame, text="Auftragsart:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Panne", "Unfall", "Sicherstellung"], fg_color=COLOR_ORANGE, button_color=COLOR_ORANGE, button_hover_color=COLOR_HOVER_ORANGE); w.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.polizei_fields["Auftragsart"] = w

        labels_after = ["Fahrzeug", "Kennzeichen"]
        for i, text in enumerate(labels_after, start=3):
            customtkinter.CTkLabel(frame, text=f"{text}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.polizei_fields[text] = w
            
        customtkinter.CTkLabel(frame, text="Mit Kran:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Nein", "Ja"], fg_color=COLOR_ORANGE, button_color=COLOR_ORANGE, button_hover_color=COLOR_HOVER_ORANGE); w.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.polizei_fields["Mit Kran"] = w

        customtkinter.CTkLabel(frame, text="Einsatzort:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        self.polizei_fields["Einsatzort"] = w

    def _create_lkw_widgets(self, parent):
        self._create_section_header(parent, "Auftragsannahme LKW", "lkw")
        frame = customtkinter.CTkFrame(parent, fg_color="transparent"); frame.pack(fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)

        labels = ["Auftraggeber", "Anrufer", "Ansprechpartner", "Telefonnummer", "LKW Modell", "Kennzeichen", "Schaden", "Einsatzort", "Verbringungsort"]
        for i, text in enumerate(labels):
            customtkinter.CTkLabel(frame, text=f"{text}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.lkw_fields[text] = w

    def _create_oelspur_widgets(self, parent):
        self._create_section_header(parent, "Auftragsannahme Ölspur", "oelspur")
        frame = customtkinter.CTkFrame(parent, fg_color="transparent"); frame.pack(fill="both", expand=True)
        frame.grid_columnconfigure(1, weight=1)

        labels = ["Melder", "Anrufer", "Telefonnummer", "Art der Verunreinigung"]
        for i, text in enumerate(labels):
            customtkinter.CTkLabel(frame, text=f"{text}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.oelspur_fields[text] = w
        
        customtkinter.CTkLabel(frame, text="Länge | Breite:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        sub_frame = customtkinter.CTkFrame(frame, fg_color="transparent"); sub_frame.grid(row=4, column=1, padx=0, pady=5, sticky="ew")
        sub_frame.grid_columnconfigure((0,2), weight=1)
        w_l = customtkinter.CTkEntry(sub_frame, border_color=COLOR_ORANGE, placeholder_text="Länge"); w_l.grid(row=0, column=0, padx=(0,5), sticky="ew")
        customtkinter.CTkLabel(sub_frame, text="|").grid(row=0, column=1)
        w_b = customtkinter.CTkEntry(sub_frame, border_color=COLOR_ORANGE, placeholder_text="Breite"); w_b.grid(row=0, column=2, padx=(5,0), sticky="ew")
        self.oelspur_fields["Länge"] = w_l; self.oelspur_fields["Breite"] = w_b

        customtkinter.CTkLabel(frame, text="Absicherung notwendig:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(frame, values=["Nein", "Ja"], fg_color=COLOR_ORANGE, button_color=COLOR_ORANGE, button_hover_color=COLOR_HOVER_ORANGE); w.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.oelspur_fields["Absicherung notwendig"] = w

        labels_after = ["Einsatzkräfte vor Ort?", "Verursacher bekannt?", "Treffpunkt"]
        for i, text in enumerate(labels_after, start=6):
            customtkinter.CTkLabel(frame, text=f"{text}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkEntry(frame, border_color=COLOR_ORANGE); w.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.oelspur_fields[text] = w

        customtkinter.CTkLabel(frame, text="Zusatzinformation:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkTextbox(frame, border_color=COLOR_ORANGE, border_width=2, height=100); w.grid(row=9, column=1, padx=5, pady=5, sticky="ew")
        self.oelspur_fields["Zusatzinformation"] = w

    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color=COLOR_DARK_GREY, corner_radius=0)
        button_frame.grid(row=2, column=0, columnspan=7, sticky="ew", padx=10, pady=(10, 20))
        
        customtkinter.CTkLabel(button_frame, text="Fahrer:", font=("Calibri", 14, "bold")).pack(side="left", padx=(10,5))
        w = customtkinter.CTkOptionMenu(button_frame, values=["Bitte Wählen"] + self.fahrer_list, fg_color=COLOR_ORANGE, button_color=COLOR_ORANGE, button_hover_color=COLOR_HOVER_ORANGE); w.set("Bitte Wählen")
        w.pack(side="left", padx=(0, 20))
        self.fahrer_fields["Fahrer"] = w

        try:
            whatsapp_image_data = Image.open(resource_path("whatsapp_icon.png"))
            whatsapp_image = customtkinter.CTkImage(light_image=whatsapp_image_data, dark_image=whatsapp_image_data, size=(20, 20))
            customtkinter.CTkButton(button_frame, text="Auftrag versenden", image=whatsapp_image, compound="left", command=self.send_whatsapp_message, fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)
        except (FileNotFoundError, UnidentifiedImageError, tkinter.TclError):
            customtkinter.CTkButton(button_frame, text="Auftrag versenden", command=self.send_whatsapp_message, fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)

        right_button_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        right_button_frame.pack(side="right", padx=10)
        customtkinter.CTkButton(right_button_frame, text="Kopieren", command=self.copy_to_clipboard, fg_color=COLOR_ORANGE, hover_color=COLOR_HOVER_ORANGE).pack(side="left", padx=10)
        customtkinter.CTkButton(right_button_frame, text="Zurücksetzen", command=self.reset_form, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(right_button_frame, text="Schließen", command=self.destroy, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def _get_field_value(self, field_dict, label):
        if label not in field_dict: return ""
        widget = field_dict[label]
        value = ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)):
            value = widget.get()
            if value in ["Bitte Wählen", ""]: return ""
        elif isinstance(widget, customtkinter.CTkTextbox):
            value = widget.get("1.0", "end-1c")
        elif isinstance(widget, customtkinter.CTkEntry):
            value = widget.get()
        return value.strip()

    def reset_form(self):
        all_dicts = [self.pkw_fields, self.polizei_fields, self.lkw_fields, self.oelspur_fields, self.fahrer_fields]
        for field_dict in all_dicts:
            for widget in field_dict.values():
                if isinstance(widget, customtkinter.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, customtkinter.CTkTextbox):
                    widget.delete("1.0", "end")
                elif isinstance(widget, (customtkinter.CTkOptionMenu, customtkinter.CTkComboBox)):
                    widget.set(widget.cget("values")[0])
        for checkbox in self.section_checkboxes.values():
            checkbox.deselect()
        self._toggle_pkw_fields()

    def _generate_pkw_text(self):
        """Generates the text for the PKW section based on the user's specified format."""
        lines = []
        
        # Helper to add a line if the value exists
        def add_line(lines_list, label, value):
            if value:
                lines_list.append(f"{label}: {value}")

        # Helper to add a block of lines followed by a blank line if the block has content
        def add_block(block_lines):
            if any(line for line in block_lines):
                lines.extend(block_lines)
                lines.append("")

        # Block 1: Auftraggeber
        auftraggeber_block = []
        add_line(auftraggeber_block, "Auftraggeber", self._get_field_value(self.pkw_fields, "Auftraggeber"))
        add_block(auftraggeber_block)

        # Block 2: Auftragsart, Anrufer
        auftragsart_block = []
        add_line(auftragsart_block, "Auftragsart", self._get_field_value(self.pkw_fields, "Auftragsart"))
        add_line(auftragsart_block, "Anrufer", self._get_field_value(self.pkw_fields, "Anrufer"))
        add_block(auftragsart_block)
        
        # Block 3: Kunde
        kunde_block = []
        add_line(kunde_block, "Kunde vor Ort", self._get_field_value(self.pkw_fields, "Kunde vor Ort"))
        add_line(kunde_block, "Telefonnummer", self._get_field_value(self.pkw_fields, "Telefonnummer"))
        add_block(kunde_block)
        
        # Block 4: Fahrzeugdetails
        fahrzeug_block = []
        add_line(fahrzeug_block, "Fahrzeug", self._get_field_value(self.pkw_fields, "Fahrzeug"))
        add_line(fahrzeug_block, "Modell", self._get_field_value(self.pkw_fields, "Modell"))
        add_line(fahrzeug_block, "Kennzeichen", self._get_field_value(self.pkw_fields, "Kennzeichen"))
        
        # Mobi-specific fields
        if self.pkw_fields["Auftragsart"].get() == "Mobi":
            add_line(fahrzeug_block, "Fahrgestellnummer", self._get_field_value(self.pkw_fields, "Fahrgestellnummer"))
            add_line(fahrzeug_block, "Erstzulassung", self._get_field_value(self.pkw_fields, "Erstzulassung"))
            add_line(fahrzeug_block, "KM-Stand", self._get_field_value(self.pkw_fields, "KM-Stand"))
        add_block(fahrzeug_block)

        # Block 5: Schaden
        schaden_block = []
        add_line(schaden_block, "Schaden", self._get_field_value(self.pkw_fields, "Schaden"))
        add_block(schaden_block)
        
        # Block 6: Orte
        orte_block = []
        add_line(orte_block, "Pannen-/Unfallort", self._get_field_value(self.pkw_fields, "Pannen-/Unfallort"))
        add_line(orte_block, "Verbringungsort", self._get_field_value(self.pkw_fields, "Verbringungsort"))
        add_block(orte_block)

        # Block 7: Preisinfo
        preisinfo_block = []
        if self.pkw_fields["Auftragsart"].get() in ["Panne", "Unfall"]:
             add_line(preisinfo_block, "Preisinfo", self._get_field_value(self.pkw_fields, "Preisinfo"))
        add_block(preisinfo_block)
        
        # Clean up trailing newlines
        return "\n".join(lines).strip()

    def _generate_text_for_section(self, title, field_dict, order):
        lines = []
        has_content = False
        
        active_pkw_auftragsart = self.pkw_fields["Auftragsart"].get()
        
        for key in order:
            if key in ["Fahrgestellnummer", "Erstzulassung", "KM-Stand"] and active_pkw_auftragsart != "Mobi":
                continue
            if key == "Preisinfo" and active_pkw_auftragsart not in ["Panne", "Unfall"]:
                continue

            value = self._get_field_value(field_dict, key)
            if value:
                lines.append(f"{key}: {value}")
                has_content = True
        
        if has_content:
            return [f"--- {title} ---"] + lines
        return []

    def copy_to_clipboard(self):
        full_text = self._build_full_message()
        if full_text:
            self.clipboard_clear()
            self.clipboard_append(full_text)
            print("Folgender Text wurde kopiert:\n" + full_text)
            
    def _build_full_message(self):
        output_parts = []
        
        if self.section_checkboxes["pkw"].get():
            pkw_text = self._generate_pkw_text()
            if pkw_text:
                output_parts.append(pkw_text)

        if self.section_checkboxes["polizei"].get():
            polizei_order = ["Auftraggeber", "Einsatznummer", "Auftragsart", "Fahrzeug", "Kennzeichen", "Mit Kran", "Einsatzort"]
            polizei_text = self._generate_text_for_section("Polizei Auftrag", self.polizei_fields, polizei_order)
            if polizei_text:
                output_parts.append("\n".join(polizei_text))

        if self.section_checkboxes["lkw"].get():
            lkw_order = ["Auftraggeber", "Anrufer", "Ansprechpartner", "Telefonnummer", "LKW Modell", "Kennzeichen", "Schaden", "Einsatzort", "Verbringungsort"]
            lkw_text = self._generate_text_for_section("Auftragsannahme LKW", self.lkw_fields, lkw_order)
            if lkw_text:
                output_parts.append("\n".join(lkw_text))

        if self.section_checkboxes["oelspur"].get():
            oelspur_order = ["Melder", "Anrufer", "Telefonnummer", "Art der Verunreinigung", "Länge", "Breite", "Absicherung notwendig", "Einsatzkräfte vor Ort?", "Verursacher bekannt?", "Treffpunkt", "Zusatzinformation"]
            oelspur_text_list = self._generate_text_for_section("Auftragsannahme Ölspur", self.oelspur_fields, oelspur_order)
            if oelspur_text_list:
                laenge = self._get_field_value(self.oelspur_fields, "Länge")
                breite = self._get_field_value(self.oelspur_fields, "Breite")
                # Rebuild the text to handle the combined length/width field correctly
                oelspur_text_final = [oelspur_text_list[0]] # Title
                for line in oelspur_text_list[1:]:
                    if line.startswith("Länge:") or line.startswith("Breite:"):
                        continue
                    oelspur_text_final.append(line)
                
                if laenge or breite:
                    try:
                        index = [i for i, s in enumerate(oelspur_text_final) if s.startswith("Art der Verunreinigung:")][0]
                        oelspur_text_final.insert(index + 1, f"Länge | Breite: {laenge} | {breite}")
                    except IndexError: # If 'Art der Verunreinigung' is empty, just append
                        oelspur_text_final.append(f"Länge | Breite: {laenge} | {breite}")
                
                output_parts.append("\n".join(oelspur_text_final))

        return "\n\n".join(output_parts)

    def send_whatsapp_message(self):
        fahrer = self._get_field_value(self.fahrer_fields, "Fahrer")
        if not fahrer:
            print("Fehler: Bitte zuerst einen Fahrer auswählen.")
            return

        phone_number = self.fahrer_telefonbuch.get(fahrer)
        if not phone_number:
            print(f"Fehler: Keine Telefonnummer für Fahrer '{fahrer}' hinterlegt.")
            return
            
        message = self._build_full_message()
        if not message:
            print("Keine Daten zum Senden vorhanden. Bitte eine Sektion auswählen.")
            return

        encoded_message = quote(message)
        url = f"https.me/{phone_number}?text={encoded_message}"
        
        webbrowser.open(url)
        print(f"WhatsApp-Link für Fahrer {fahrer} geöffnet.")

class UnterhaslbergerForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Annahme Unterhaslberger")
        self.geometry("1100x900")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)

        # --- Data Dictionaries ---
        self.pkw_fields = {}
        self.gdv_fields = {}
        self.fahrer_fields = {}
        self.section_checkboxes = {}
        self.dynamic_widgets = {}

        self.gdv_fahrzeug_typ = tkinter.StringVar(value="PKW")
        
        self.fahrer_list = sorted([
            "Mike Ahlsdorf", "Siegfried Bonhorst", "Slavisa Bosic", "Catalin Dogariu, Ionut", "Dubravac, Antomir", 
            "Grosse, Manfred", "Koal, Christian", "Matzka, Stefan", "Rumpfinger, Josef", "Srbeny, Daniel", 
            "Unterhaslberger, Karl (Jr.)", "Unterhaslberger, Karl (Sr.)", "Fahrzeug: MÜ-KU35", "Fahrzeug: MÜ-KU54", 
            "Fahrzeug: MÜ-KU81", "Fahrzeug: MÜ-KU90", "Fahrzeug: MÜ-KU95", "Fahrzeug: MÜ-KU20", "Peters, Werner", 
            "Wegmann, Alexander", "Witter, Gerhard", "Zaremba, Gerhard"
        ])
        self.fahrer_telefonbuch = {
            "Mike Ahlsdorf": "4915776782500", "Siegfried Bonhorst": "4915758060246", "Slavisa Bosic": "4915228451147", 
            "Catalin Dogariu, Ionut": "4915124403201", "Dubravac, Antomir": "4917657700078", "Grosse, Manfred": "491723163737", 
            "Koal, Christian": "491724307812", "Matzka, Stefan": "491728847293", "Rumpfinger, Josef": "491793725011", 
            "Srbeny, Daniel": "4917661262817", "Unterhaslberger, Karl (Jr.)": "4915155114000", "Unterhaslberger, Karl (Sr.)": "4915118204800", 
            "Fahrzeug: MÜ-KU35": "4915155113981", "Fahrzeug: MÜ-KU54": "4915155113985", "Fahrzeug: MÜ-KU81": "4915155113991", 
            "Fahrzeug: MÜ-KU90": "4915146315540", "Fahrzeug: MÜ-KU95": "4915155113988", "Fahrzeug: MÜ-KU20": "4915155113992", 
            "Peters, Werner": "4915735738486", "Wegmann, Alexander": "491622794763", "Witter, Gerhard": "4915566625775", 
            "Zaremba, Gerhard": "491777947935"
        }

        # --- Layout ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure((0, 2), weight=1)
        main_frame.grid_columnconfigure(1, weight=0)

        # --- Frames for sections ---
        pkw_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent", corner_radius=0)
        pkw_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        pkw_frame.grid_columnconfigure(0, weight=1)

        separator = customtkinter.CTkFrame(main_frame, width=2, fg_color=COLOR_TEAL)
        separator.grid(row=0, column=1, sticky="ns", pady=10)

        gdv_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent", corner_radius=0)
        gdv_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        gdv_frame.grid_columnconfigure(0, weight=1)

        # --- Populate sections ---
        self._create_pkw_widgets(pkw_frame)
        self._create_gdv_widgets(gdv_frame)
        
        self._create_action_buttons(self)

    def _create_section_header(self, parent, text, section_key):
        header_frame = customtkinter.CTkFrame(parent, fg_color=COLOR_MEDIUM_GREY, corner_radius=8)
        header_frame.pack(fill="x", pady=(5, 10), padx=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        label = customtkinter.CTkLabel(header_frame, text=text, font=("Calibri", 18, "bold"), text_color=COLOR_TEAL)
        label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        checkbox = customtkinter.CTkCheckBox(header_frame, text="", border_color=COLOR_TEAL, hover_color=COLOR_HOVER_TEAL, fg_color=COLOR_TEAL)
        checkbox.grid(row=0, column=1, padx=15, pady=10, sticky="e")
        self.section_checkboxes[section_key] = checkbox

        content_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="x", padx=5, pady=(0, 15))
        content_frame.grid_columnconfigure(1, weight=1)
        return content_frame

    def _create_pkw_widgets(self, parent):
        content_frame = self._create_section_header(parent, "Annahme Panne | Unfall (PKW)", "pkw")
        self.dynamic_widgets['pkw_preisinfo'] = [] # To store Preisinfo label and entry

        row = 0
        customtkinter.CTkLabel(content_frame, text="Auftraggeber:").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        auftraggeber_values = ["", "Privater Selbstzahler", "AVG Auto-Vertrieb-GmbH", "Auto Grill", "Autohaus Ostermaier GmbH", "Autohaus Ebersberg", "VW Notdienst", "Audi Notdienst", "Seat Notdienst", "Skoda Notdienst"]
        w = customtkinter.CTkComboBox(content_frame, values=auftraggeber_values, border_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL, command=self._toggle_preisinfo, width=300)
        w.grid(row=row, column=1, padx=5, pady=8, sticky="ew")
        self.pkw_fields["Auftraggeber"] = w
        row += 1

        customtkinter.CTkLabel(content_frame, text="Auftragsart:").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Panne", "Mobi", "Unfall"], fg_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL)
        w.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        self.pkw_fields["Auftragsart"] = w
        row += 1
        
        pkw_labels = ["Anrufer", "Kunde vor Ort", "Telefonnummer", "Fahrzeug", "Modell", "Kennzeichen", "Schaden", "Pannen-/Unfallort"]
        for label_text in pkw_labels:
            customtkinter.CTkLabel(content_frame, text=f"{label_text}:").grid(row=row, column=0, padx=5, pady=8, sticky="w")
            w = customtkinter.CTkEntry(content_frame, border_color=COLOR_TEAL)
            w.grid(row=row, column=1, padx=5, pady=8, sticky="ew")
            self.pkw_fields[label_text] = w
            row += 1

        customtkinter.CTkLabel(content_frame, text="Verbringungsort:").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        verbringungsort_values = [
            "",
            "Privater Selbstzahler",
            "Staudhamer Feld 4, 83512 Wasserburg am Inn | AVG Auto-Vertrieb-GmbH",
            "Schwabener Str. 26, 85560 Ebersberg | Auto Grill",
            "Teplitzer Str. 25, 84478 Waldkraiburg | Autohaus Ostermaier GmbH",
            "Gewerbepark Nord-Ost 1, 85560 Ebersberg | Autohaus Ebersberg (Audi)", 
            "Gewerbepark Nord-Ost 3, 85560 Ebersberg | Autohaus Ebersberg (Seat)", 
            "Gewerbepark Nord-Ost 4, 85560 Ebersberg | Autohaus Ebersberg (Skoda)", 
            "Gewerbepark Nord-Ost 2, 85560 Ebersberg | Autohaus Ebersberg (VW)", 
            "Münchener Str. 46, 83527 Haag in Oberbayern | Autohaus Haag Zweigniederlassung AH Ebersberg"
        ]
        w = customtkinter.CTkComboBox(content_frame, values=verbringungsort_values, border_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL)
        w.grid(row=row, column=1, padx=5, pady=8, sticky="ew")
        self.pkw_fields["Verbringungsort"] = w
        row += 1
        
        # Conditional Preisinfo
        preis_label = customtkinter.CTkLabel(content_frame, text="Preisinfo:")
        preis_entry = customtkinter.CTkEntry(content_frame, border_color=COLOR_TEAL)
        self.pkw_fields["Preisinfo"] = preis_entry
        self.dynamic_widgets['pkw_preisinfo'].extend([preis_label, preis_entry])
        
        # Initially hide it
        self._toggle_preisinfo()

    def _toggle_preisinfo(self, selection=None):
        preis_label, preis_entry = self.dynamic_widgets['pkw_preisinfo']
        if self.pkw_fields["Auftraggeber"].get() == "Privater Selbstzahler":
            row_index = len(self.pkw_fields) # Place it at the end
            preis_label.grid(row=row_index, column=0, padx=5, pady=8, sticky="w")
            preis_entry.grid(row=row_index, column=1, padx=5, pady=8, sticky="ew")
        else:
            preis_label.grid_remove()
            preis_entry.grid_remove()

    def _create_gdv_widgets(self, parent):
        content_frame = self._create_section_header(parent, "Annahme GDV", "gdv")
        self.dynamic_widgets['gdv_pkw'] = []
        self.dynamic_widgets['gdv_lkw'] = []
        
        # Radio buttons for PKW/LKW
        radio_frame = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        radio_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=8, sticky="w")
        customtkinter.CTkRadioButton(radio_frame, text="PKW", variable=self.gdv_fahrzeug_typ, value="PKW", command=self._toggle_gdv_fields, fg_color=COLOR_TEAL, hover_color=COLOR_HOVER_TEAL).pack(side="left", padx=(0, 15))
        customtkinter.CTkRadioButton(radio_frame, text="LKW", variable=self.gdv_fahrzeug_typ, value="LKW", command=self._toggle_gdv_fields, fg_color=COLOR_TEAL, hover_color=COLOR_HOVER_TEAL).pack(side="left")

        # --- Common GDV Fields ---
        row = 1
        customtkinter.CTkLabel(content_frame, text="Auftraggeber:").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        w = customtkinter.CTkLabel(content_frame, text="GDV Bayern", font=("Calibri", 14, "bold")); w.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        self.gdv_fields["Auftraggeber"] = w
        row += 1

        common_labels = ["Vorgangsnummer"]
        for label_text in common_labels:
            customtkinter.CTkLabel(content_frame, text=f"{label_text}:").grid(row=row, column=0, padx=5, pady=8, sticky="w")
            w = customtkinter.CTkEntry(content_frame, border_color=COLOR_TEAL); w.grid(row=row, column=1, padx=5, pady=8, sticky="ew")
            self.gdv_fields[label_text] = w
            row+=1
            
        customtkinter.CTkLabel(content_frame, text="Auftragsart:").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        w = customtkinter.CTkOptionMenu(content_frame, values=["Panne", "Unfall", "Sicherstellung"], fg_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL)
        w.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        self.gdv_fields["Auftragsart"] = w
        row += 1
        
        # This will be the starting row for dynamic fields
        dynamic_row_start = row

        # --- PKW Specific Fields ---
        pkw_row = dynamic_row_start
        pkw_labels = ["Fahrzeug", "Kennzeichen"]
        for label_text in pkw_labels:
            l = customtkinter.CTkLabel(content_frame, text=f"{label_text}:")
            e = customtkinter.CTkEntry(content_frame, border_color=COLOR_TEAL)
            l.grid(row=pkw_row, column=0, padx=5, pady=8, sticky="w")
            e.grid(row=pkw_row, column=1, padx=5, pady=8, sticky="ew")
            self.gdv_fields[f"pkw_{label_text}"] = e
            self.dynamic_widgets['gdv_pkw'].extend([l, e])
            pkw_row += 1
            
        l_kran = customtkinter.CTkLabel(content_frame, text="Mit Kran:")
        m_kran = customtkinter.CTkOptionMenu(content_frame, values=["Nein", "Ja"], fg_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL)
        l_kran.grid(row=pkw_row, column=0, padx=5, pady=8, sticky="w")
        m_kran.grid(row=pkw_row, column=1, padx=5, pady=8, sticky="w")
        self.gdv_fields["pkw_Mit Kran"] = m_kran
        self.dynamic_widgets['gdv_pkw'].extend([l_kran, m_kran])
        pkw_row += 1

        # --- LKW Specific Fields ---
        lkw_row = dynamic_row_start
        lkw_labels = ["Zugmaschine", "Auflieger", "Kennzeichen"]
        for label_text in lkw_labels:
            l = customtkinter.CTkLabel(content_frame, text=f"{label_text}:")
            e = customtkinter.CTkEntry(content_frame, border_color=COLOR_TEAL)
            l.grid(row=lkw_row, column=0, padx=5, pady=8, sticky="w")
            e.grid(row=lkw_row, column=1, padx=5, pady=8, sticky="ew")
            self.gdv_fields[f"lkw_{label_text}"] = e
            self.dynamic_widgets['gdv_lkw'].extend([l, e])
            lkw_row += 1
        
        # --- Final common field ---
        # The final row is the max of where PKW or LKW fields ended
        final_row = max(pkw_row, lkw_row)
        customtkinter.CTkLabel(content_frame, text="Einsatzort:").grid(row=final_row, column=0, padx=5, pady=8, sticky="w")
        w = customtkinter.CTkEntry(content_frame, border_color=COLOR_TEAL); w.grid(row=final_row, column=1, padx=5, pady=8, sticky="ew")
        self.gdv_fields["Einsatzort"] = w

        self._toggle_gdv_fields()

    def _toggle_gdv_fields(self):
        is_pkw = self.gdv_fahrzeug_typ.get() == "PKW"

        for widget in self.dynamic_widgets['gdv_pkw']:
            if is_pkw: widget.grid()
            else: widget.grid_remove()
        
        for widget in self.dynamic_widgets['gdv_lkw']:
            if not is_pkw: widget.grid()
            else: widget.grid_remove()

    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=15)
        
        # Fahrer
        customtkinter.CTkLabel(button_frame, text="Fahrer:", font=("Calibri", 14, "bold")).pack(side="left", padx=(10,5))
        w = customtkinter.CTkOptionMenu(button_frame, values=["Bitte Wählen"] + self.fahrer_list, fg_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL, width=250)
        w.pack(side="left", padx=(0, 20))
        self.fahrer_fields["Fahrer"] = w

        # WhatsApp Button
        try:
            whatsapp_image_data = Image.open(resource_path("whatsapp_icon.png"))
            whatsapp_image = customtkinter.CTkImage(light_image=whatsapp_image_data, dark_image=whatsapp_image_data, size=(20, 20))
            customtkinter.CTkButton(button_frame, text="Per WhatsApp versenden", image=whatsapp_image, compound="left", command=self.send_whatsapp_message, height=35, font=("Calibri", 14, "bold"), fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)
        except (FileNotFoundError, UnidentifiedImageError, tkinter.TclError):
            customtkinter.CTkButton(button_frame, text="Per WhatsApp versenden", command=self.send_whatsapp_message, height=35, font=("Calibri", 14, "bold"), fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)

        # Right-aligned buttons
        right_button_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        right_button_frame.pack(side="right", padx=10)
        customtkinter.CTkButton(right_button_frame, text="Kopieren", command=self.copy_to_clipboard, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_TEAL, hover_color=COLOR_HOVER_TEAL).pack(side="left", padx=10)
        customtkinter.CTkButton(right_button_frame, text="Zurücksetzen", command=self.reset_form, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(right_button_frame, text="Schließen", command=self.destroy, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def _get_value(self, field_dict, label):
        if label not in field_dict: return ""
        widget = field_dict[label]
        value = ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)):
            value = widget.get()
            if value == "Bitte Wählen" or value == "": return ""
        elif isinstance(widget, customtkinter.CTkEntry):
            value = widget.get()
        elif isinstance(widget, customtkinter.CTkLabel):
            value = widget.cget("text")
        return value.strip()
        
    def reset_form(self):
        for field_dict in [self.pkw_fields, self.gdv_fields, self.fahrer_fields]:
            for widget in field_dict.values():
                if isinstance(widget, customtkinter.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, (customtkinter.CTkOptionMenu, customtkinter.CTkComboBox)):
                    widget.set(widget.cget("values")[0])
        
        for cb in self.section_checkboxes.values():
            cb.deselect()
            
        self.gdv_fahrzeug_typ.set("PKW")
        self._toggle_gdv_fields()
        self._toggle_preisinfo()

    def _generate_pkw_text(self):
        lines = ["**Annahme Panne | Unfall (PKW)**"]
        order = ["Auftraggeber", "Auftragsart", "Anrufer", "Kunde vor Ort", "Telefonnummer", "Fahrzeug", "Modell", "Kennzeichen", "Schaden", "Pannen-/Unfallort", "Verbringungsort", "Preisinfo"]
        
        has_content = False
        for key in order:
            if key == "Preisinfo" and self.pkw_fields["Auftraggeber"].get() != "Privater Selbstzahler":
                continue
            value = self._get_value(self.pkw_fields, key)
            if value:
                lines.append(f"{key}: {value}")
                has_content = True
        
        return "\n".join(lines) if has_content else ""

    def _generate_gdv_text(self):
        is_pkw = self.gdv_fahrzeug_typ.get() == "PKW"
        
        if is_pkw:
            lines = ["**Annahme GDV**", "Fahrzeugtyp: PKW"]
            order = ["Auftraggeber", "Vorgangsnummer", "Auftragsart", "pkw_Fahrzeug", "pkw_Kennzeichen", "pkw_Mit Kran", "Einsatzort"]
            has_content = False
            for key in order:
                display_key = key.replace("pkw_", "")
                value = self._get_value(self.gdv_fields, key)
                if value:
                    lines.append(f"{display_key}: {value}")
                    has_content = True
            return "\n".join(lines) if has_content else ""
        else: # LKW
            lines = ["**Annahme GDV**"]
            has_content = False
            
            # Helper to add a line if value exists
            def add_gdv_line(key, display_key=None):
                nonlocal has_content
                value = self._get_value(self.gdv_fields, key)
                if value:
                    lines.append(f"{(display_key or key)}: {value}")
                    has_content = True

            add_gdv_line("Vorgangsnummer")
            add_gdv_line("Auftragsart")
            lines.append("") # Blank line
            add_gdv_line("lkw_Zugmaschine", "Zugmaschine")
            add_gdv_line("lkw_Auflieger", "Auflieger")
            add_gdv_line("lkw_Kennzeichen", "Kennzeichen")
            lines.append("") # Blank line
            add_gdv_line("Einsatzort")

            return "\n".join(lines) if has_content else ""

    def _build_full_message(self):
        output_parts = []
        if self.section_checkboxes["pkw"].get():
            pkw_text = self._generate_pkw_text()
            if pkw_text:
                output_parts.append(pkw_text)
        
        if self.section_checkboxes["gdv"].get():
            gdv_text = self._generate_gdv_text()
            if gdv_text:
                output_parts.append(gdv_text)
        
        return "\n\n".join(output_parts)

    def copy_to_clipboard(self):
        final_text = self._build_full_message()
        if final_text:
            self.clipboard_clear()
            self.clipboard_append(final_text)
            print("Folgender Text wurde kopiert:\n" + final_text)

    def send_whatsapp_message(self):
        fahrer = self._get_value(self.fahrer_fields, "Fahrer")
        if not fahrer:
            print("Fehler: Bitte zuerst einen Fahrer auswählen.")
            return

        phone_number = self.fahrer_telefonbuch.get(fahrer)
        if not phone_number:
            print(f"Fehler: Keine Telefonnummer für Fahrer '{fahrer}' hinterlegt.")
            return
            
        message = self._build_full_message()
        if not message:
            print("Keine Daten zum Senden vorhanden. Bitte eine Sektion auswählen.")
            return

        encoded_message = quote(message)
        url = f"https.me/{phone_number}?text={encoded_message}"
        
        webbrowser.open(url)
        print(f"WhatsApp-Link für Fahrer {fahrer} geöffnet.")

class FalschparkerPrivatForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Annahme Falschparker | Privat")
        self.geometry("700x700")
        self.resizable(True, True)
        self.configure(fg_color=COLOR_DARK_GREY)

        self.input_fields = {}

        # --- Data ---
        self.abschleppgrund_values = [
            "steht auf dem angemieteten Stellplatz",
            "steht in der Feuerwehrzufahrt",
            "steht in der Einfahrt",
            "blockiert die Zufahrt",
            "steht im Halteverbot",
            "ohne gültigen Parkausweis",
            "parkt auf Behindertenparkplatz",
            "parkt auf Frauenparkplatz",
            "parkt auf Eltern-Kind-Parkplatz"
        ]
        self.fahrer_list = sorted(["Gökhan Balkan", "Denise Balkan"])
        self.fahrer_telefonbuch = {
            "Gökhan Balkan": "4915122088986",
            "Denise Balkan": "4917641448898"
        }

        # --- Layout ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        scrollable_frame = customtkinter.CTkScrollableFrame(main_frame, fg_color="transparent", label_text="Details zum Falschparker", label_text_color=COLOR_TEAL)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        # --- Widgets ---
        labels = ["Anrufer", "Telefonnummer", "Fahrzeug", "Modell", "Kennzeichen", "Einsatzort", "Stellplatz"]
        for i, text in enumerate(labels):
            customtkinter.CTkLabel(scrollable_frame, text=f"{text}:").grid(row=i, column=0, padx=5, pady=8, sticky="w")
            w = customtkinter.CTkEntry(scrollable_frame, border_color=COLOR_TEAL, width=300)
            w.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
            self.input_fields[text] = w

        customtkinter.CTkLabel(scrollable_frame, text="Abschleppgrund:").grid(row=len(labels), column=0, padx=5, pady=8, sticky="w")
        w = customtkinter.CTkOptionMenu(scrollable_frame, values=["Bitte Wählen"] + self.abschleppgrund_values, fg_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL, width=300)
        w.set("Bitte Wählen")
        w.grid(row=len(labels), column=1, padx=5, pady=8, sticky="w")
        self.input_fields["Abschleppgrund"] = w

        customtkinter.CTkLabel(scrollable_frame, text="Fahrer:").grid(row=len(labels)+1, column=0, padx=5, pady=8, sticky="w")
        w = customtkinter.CTkOptionMenu(scrollable_frame, values=["Bitte Wählen"] + self.fahrer_list, fg_color=COLOR_TEAL, button_color=COLOR_TEAL, button_hover_color=COLOR_HOVER_TEAL, width=300)
        w.set("Bitte Wählen")
        w.grid(row=len(labels)+1, column=1, padx=5, pady=8, sticky="w")
        self.input_fields["Fahrer"] = w

        w = customtkinter.CTkCheckBox(scrollable_frame, text="Abtretung notwendig", border_color=COLOR_TEAL, hover_color=COLOR_HOVER_TEAL, fg_color=COLOR_TEAL)
        w.grid(row=len(labels)+2, column=1, padx=5, pady=15, sticky="w")
        self.input_fields["Abtretung notwendig"] = w

        self._create_action_buttons(main_frame)

    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=15)
        button_frame.grid_columnconfigure(0, weight=1)
        center_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        center_frame.pack()

        try:
            whatsapp_image_data = Image.open(resource_path("whatsapp_icon.png"))
            whatsapp_image = customtkinter.CTkImage(light_image=whatsapp_image_data, dark_image=whatsapp_image_data, size=(20, 20))
            customtkinter.CTkButton(center_frame, text="Per WhatsApp versenden", image=whatsapp_image, compound="left", command=self.send_whatsapp_message, height=35, font=("Calibri", 14, "bold"), fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)
        except (FileNotFoundError, UnidentifiedImageError, tkinter.TclError):
            customtkinter.CTkButton(center_frame, text="Per WhatsApp versenden", command=self.send_whatsapp_message, height=35, font=("Calibri", 14, "bold"), fg_color="#25D366", hover_color="#1EAE54").pack(side="left", padx=10)

        customtkinter.CTkButton(center_frame, text="Kopieren", command=self.copy_to_clipboard, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_TEAL, hover_color=COLOR_HOVER_TEAL).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Zurücksetzen", command=self.reset_form, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Schließen", command=self.destroy, height=35, font=("Calibri", 14, "bold"), fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def reset_form(self):
        for widget in self.input_fields.values():
            if isinstance(widget, customtkinter.CTkEntry):
                widget.delete(0, "end")
            elif isinstance(widget, customtkinter.CTkOptionMenu):
                widget.set(widget.cget("values")[0])
            elif isinstance(widget, customtkinter.CTkCheckBox):
                widget.deselect()

    def _get_value(self, label):
        if label not in self.input_fields: return ""
        widget = self.input_fields[label]
        value = ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)):
            value = widget.get()
            if value == "Bitte Wählen": value = ""
        elif isinstance(widget, customtkinter.CTkEntry):
            value = widget.get()
        elif isinstance(widget, customtkinter.CTkCheckBox):
            value = "Ja" if widget.get() == 1 else "Nein"
        return value.strip()

    def _generate_copy_text(self):
        output_lines = ["**Annahme Falschparker | Privat**", ""]
        
        ordered_keys = ["Anrufer", "Telefonnummer", "Fahrzeug", "Modell", "Kennzeichen", "Abschleppgrund", "Einsatzort", "Stellplatz"]
        for key in ordered_keys:
            value = self._get_value(key)
            if value:
                output_lines.append(f"{key}: {value}")
        
        if self.input_fields["Abtretung notwendig"].get() == 1:
            output_lines.append("Abtretung notwendig: Ja")

        return "\n".join(output_lines)

    def copy_to_clipboard(self):
        final_text = self._generate_copy_text()
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Folgender Text wurde kopiert:\n" + final_text)

    def send_whatsapp_message(self):
        fahrer = self._get_value("Fahrer")
        if not fahrer:
            print("Fehler: Bitte zuerst einen Fahrer auswählen.")
            return

        phone_number = self.fahrer_telefonbuch.get(fahrer)
        if not phone_number:
            print(f"Fehler: Keine Telefonnummer für Fahrer '{fahrer}' hinterlegt.")
            return

        message = self._generate_copy_text()
        encoded_message = quote(message)
        
        url = f"https.me/{phone_number}?text={encoded_message}"
        
        webbrowser.open(url)
        print(f"WhatsApp-Link für Fahrer {fahrer} geöffnet.")
        
class SafarBHGReportForm(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        header_text = kwargs.pop("header_text")
        header_icon = kwargs.pop("header_icon")
        header_color = kwargs.pop("header_color")
        super().__init__(*args, **kwargs)
        self.title("Report Safar & BHG")
        self.geometry("1100x900") 
        self.resizable(False, False)
        self.configure(fg_color=COLOR_DARK_GREY)

        self.safar_fields = {}
        self.bhg_fields = {}
        self.bhg_dynamic_widgets = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        create_form_header(self, header_text, header_icon, header_color)

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)

        safar_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        safar_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        
        separator = customtkinter.CTkFrame(main_frame, width=2, fg_color=COLOR_RED)
        separator.grid(row=0, column=1, sticky="ns", pady=10)

        bhg_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        bhg_frame.grid(row=0, column=2, sticky="nsew", padx=20, pady=10)
        
        self._create_safar_widgets(safar_frame)
        self._create_bhg_widgets(bhg_frame)

        self._create_action_buttons(self)

    def _create_section_label(self, parent, text, color=COLOR_RED):
        label = customtkinter.CTkLabel(parent, text=text, font=("Calibri", 18, "bold", "underline"), anchor="w", text_color=color)
        return label

    def _create_safar_widgets(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        
        title_label = self._create_section_label(parent, "Report Safar")
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 10))

        row = 1
        customtkinter.CTkLabel(parent, text="Offene Aufträge bei der Übergabe:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkEntry(parent, border_color=COLOR_RED, width=300); w.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        self.safar_fields["Offene Aufträge bei der Übergabe"] = w
        row += 1
        
        customtkinter.CTkLabel(parent, text="Auftragslage bei der Übergabe:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=["Geringes Auftragsvolumen", "Moderates Auftragsvolumen", "Hohes Auftragsvolumen"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["Auftragslage bei der Übergabe"] = w
        row += 1

        label_wartezeit = self._create_section_label(parent, "Durchschnittliche Wartezeiten (ADAC / Sonstige)")
        label_wartezeit.grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5), padx=5)
        row += 1
        
        wartezeit_options = ["Bitte wählen", "30 - 60 Minuten", "60 - 90 Minuten", "90 - 120 Minuten", "2 - 3 Stunden", "3 - 4 Stunden", "5 - 6 Stunden", "Keine Wartezeit"]
        wartezeiten = ["16:00 – 18:00 Uhr", "18:00 – 20:00 Uhr", "20:00 – 21:00 Uhr", "21:00 – 23:00 Uhr", "Ab 23 Uhr"]
        for zeit in wartezeiten:
            customtkinter.CTkLabel(parent, text=f"{zeit}:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkOptionMenu(parent, values=wartezeit_options, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED, width=250); w.set("Bitte wählen"); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
            self.safar_fields[f"Wartezeit {zeit}"] = w
            row += 1

        label_fahrer = self._create_section_label(parent, "Fahrer, Aufträge & Verhalten")
        label_fahrer.grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5), padx=5)
        row += 1
        
        customtkinter.CTkLabel(parent, text="Fahrerplanung:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=["Unterbesetzung / Kritisch", "Ausreichende Besetzung", "Gute Besetzung", "Optimale Besetzung"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["Fahrerplanung"] = w
        row += 1

        customtkinter.CTkLabel(parent, text="Anzahl der Mobi Aufträge:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=[str(i) for i in range(16)], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["Anzahl der Mobi Aufträge"] = w
        row += 1
        
        customtkinter.CTkLabel(parent, text="durchschn. Wartezeit Mobi:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=["15 - 30 Minuten", "30 - 45 Minuten", "45 - 60 Minuten", "60 - 90 Minuten"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["durchschn. Wartezeit Mobi"] = w
        row += 1

        customtkinter.CTkLabel(parent, text="Anzahl der Ölspuren:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=[str(i) for i in range(7)], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["Anzahl der Ölspuren"] = w
        row += 1
        
        customtkinter.CTkLabel(parent, text="Anzahl der Unfälle:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=[str(i) for i in range(16)], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["Anzahl der Unfälle"] = w
        row += 1

        label_sva = self._create_section_label(parent, "SVA Frankfurt")
        label_sva.grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5), padx=5)
        row += 1

        sva_anzahl_values = [str(i) for i in range(21)]
        customtkinter.CTkLabel(parent, text="Anzahl der Aufträge:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=sva_anzahl_values, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["SVA Anzahl der Aufträge"] = w
        row += 1

        customtkinter.CTkLabel(parent, text="Anzahl der Leerfahrten:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=sva_anzahl_values, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["SVA Anzahl der Leerfahrten"] = w
        row += 1

        customtkinter.CTkLabel(parent, text="Fahrerverhalten:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkLabel(parent, text="Alle Fahrer haben ihre Aufträge zügig angenommen und sind zeitnah losgefahren.", wraplength=350, justify="left")
        w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.safar_fields["Fahrerverhalten"] = w

    def _create_bhg_widgets(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        
        title_label = self._create_section_label(parent, "Report Bad Homburg")
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 10))
        
        row = 1
        
        # Hinzugefügte Widgets für BHG Report basierend auf den Bildern
        customtkinter.CTkLabel(parent, text="Offene Aufträge bei der Übergabe:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w_open_orders = customtkinter.CTkEntry(parent, border_color=COLOR_RED, width=300)
        w_open_orders.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        self.bhg_fields["Offene Aufträge bei der Übergabe"] = w_open_orders
        row += 1

        customtkinter.CTkLabel(parent, text="Auftragslage bei der Übergabe:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w_order_situation = customtkinter.CTkOptionMenu(parent, values=["Geringes Auftragsvolumen", "Normales Auftragsvolumen", "Hohes Auftragsvolumen", "Sehr hohes Auftragsvolumen"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED)
        w_order_situation.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.bhg_fields["Auftragslage bei der Übergabe"] = w_order_situation
        row += 1

        customtkinter.CTkLabel(parent, text="Fahrerplanung:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w_driver_planning = customtkinter.CTkOptionMenu(parent, values=["Unterbesetzung / Kritisch", "Unterbesetzung", "Bedarfsgerecht", "Überbesetzung"], fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED)
        w_driver_planning.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.bhg_fields["Fahrerplanung"] = w_driver_planning
        row += 1


        label_wartezeit = self._create_section_label(parent, "AP Wartezeit ab 16:00 Uhr")
        label_wartezeit.grid(row=row, column=0, columnspan=2, sticky="w", pady=(15,5), padx=5)
        row += 1

        wartezeit_options = ["Bitte wählen", "30 - 60 Minuten", "60 - 90 Minuten", "90 - 120 Minuten", "2 - 3 Stunden", "3 - 4 Stunden", "5 - 6 Stunden", "Keine Wartezeit"]
        wartezeiten = ["16:00 – 18:00 Uhr", "18:00 – 20:00 Uhr", "20:00 – 21:00 Uhr", "21:00 – 23:00 Uhr", "Ab 23 Uhr"]
        for zeit in wartezeiten:
            customtkinter.CTkLabel(parent, text=f"{zeit}:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            w = customtkinter.CTkOptionMenu(parent, values=wartezeit_options, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED, width=250); w.set("Bitte wählen"); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
            self.bhg_fields[f"Wartezeit {zeit}"] = w
            row += 1

        label_abgesagt = self._create_section_label(parent, "Abgesagte Aufträge")
        label_abgesagt.grid(row=row, column=0, columnspan=2, sticky="w", pady=(15, 5), padx=5)
        row += 1

        customtkinter.CTkLabel(parent, text="Abgesagte Aufträge:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        w = customtkinter.CTkOptionMenu(parent, values=["Nein", "Ja"], command=self._toggle_bhg_fields, fg_color=COLOR_RED, button_color=COLOR_RED, button_hover_color=COLOR_HOVER_RED); w.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.bhg_fields["Abgesagte Aufträge"] = w
        row += 1

        l_id = customtkinter.CTkLabel(parent, text="ID:"); e_id = customtkinter.CTkEntry(parent, border_color=COLOR_RED)
        l_grund = customtkinter.CTkLabel(parent, text="Grund:"); e_grund = customtkinter.CTkEntry(parent, border_color=COLOR_RED)
        
        l_id.grid(row=row, column=0, padx=5, pady=5, sticky="w"); e_id.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        self.bhg_fields["ID"] = e_id; self.bhg_dynamic_widgets["ID"] = (l_id, e_id)
        row += 1

        l_grund.grid(row=row, column=0, padx=5, pady=5, sticky="w"); e_grund.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        self.bhg_fields["Grund"] = e_grund; self.bhg_dynamic_widgets["Grund"] = (l_grund, e_grund)
        row += 1
        
        self._toggle_bhg_fields()
        
        copy_button_bhg = customtkinter.CTkButton(parent, text="Kopieren (BHG)", command=self.copy_bhg, fg_color=COLOR_RED, hover_color=COLOR_HOVER_RED)
        copy_button_bhg.grid(row=row, column=1, sticky="w", pady=(20, 10), padx=5)

    def _toggle_bhg_fields(self, selection=None):
        show = self.bhg_fields["Abgesagte Aufträge"].get() == "Ja"
        for key in ["ID", "Grund"]:
            label, entry = self.bhg_dynamic_widgets[key]
            if show:
                label.grid(); entry.grid()
            else:
                label.grid_remove(); entry.grid_remove()

    def _create_action_buttons(self, parent):
        button_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=(15,20))
        button_frame.grid_columnconfigure(1, weight=1) # Center column for alignment
        
        customtkinter.CTkButton(button_frame, text="Kopieren", command=self.copy_safar, fg_color=COLOR_RED, hover_color=COLOR_HOVER_RED).grid(row=0, column=0, padx=10, sticky="w")
        
        center_frame = customtkinter.CTkFrame(button_frame, fg_color="transparent")
        center_frame.grid(row=0, column=1)
        customtkinter.CTkButton(center_frame, text="Zurücksetzen", command=self.reset_form, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)
        customtkinter.CTkButton(center_frame, text="Schließen", command=self.destroy, fg_color=COLOR_MEDIUM_GREY, hover_color=COLOR_BLACK).pack(side="left", padx=10)

    def _get_value(self, field_dict, label):
        if label not in field_dict: return ""
        widget = field_dict[label]
        value = ""
        if isinstance(widget, (customtkinter.CTkComboBox, customtkinter.CTkOptionMenu)):
            value = widget.get()
            if value == "Bitte wählen": return ""
        elif isinstance(widget, customtkinter.CTkEntry):
            value = widget.get()
        elif isinstance(widget, customtkinter.CTkLabel):
            value = widget.cget("text")
        return value.strip()

    def reset_form(self):
        for field_dict in [self.safar_fields, self.bhg_fields]:
            for widget in field_dict.values():
                if isinstance(widget, customtkinter.CTkEntry):
                    widget.delete(0, "end")
                elif isinstance(widget, customtkinter.CTkOptionMenu):
                    first_value = widget.cget("values")[0]
                    widget.set(first_value)
        
        self._toggle_bhg_fields()

    def _generate_safar_text(self):
        lines = ["**Report Safar**", ""]
        lines.append(f"Offene Aufträge bei der Übergabe: {self._get_value(self.safar_fields, 'Offene Aufträge bei der Übergabe')}")
        lines.append(f"Auftragslage bei der Übergabe: {self._get_value(self.safar_fields, 'Auftragslage bei der Übergabe')}")
        lines.append("\n**Durchschnittliche Wartezeiten (ADAC / Sonstige):**")
        wartezeiten = ["16:00 – 18:00 Uhr", "18:00 – 20:00 Uhr", "20:00 – 21:00 Uhr", "21:00 – 23:00 Uhr", "Ab 23 Uhr"]
        for zeit in wartezeiten:
            value = self._get_value(self.safar_fields, f'Wartezeit {zeit}')
            if value: lines.append(f"{zeit}: {value}")

        lines.append("\n**Fahrer, Aufträge & Verhalten:**")
        lines.append(f"Fahrerplanung: {self._get_value(self.safar_fields, 'Fahrerplanung')}")
        lines.append(f"Anzahl der Mobi Aufträge: {self._get_value(self.safar_fields, 'Anzahl der Mobi Aufträge')}")
        lines.append(f"durchschnittliche Wartezeit: {self._get_value(self.safar_fields, 'durchschn. Wartezeit Mobi')}")
        lines.append(f"Anzahl der Ölspuren: {self._get_value(self.safar_fields, 'Anzahl der Ölspuren')}")
        lines.append(f"Anzahl der Unfälle: {self._get_value(self.safar_fields, 'Anzahl der Unfälle')}")

        lines.append("\n**SVA Frankfurt:**")
        lines.append(f"Anzahl der Aufträge: {self._get_value(self.safar_fields, 'SVA Anzahl der Aufträge')}")
        lines.append(f"Anzahl der Leerfahrten: {self._get_value(self.safar_fields, 'SVA Anzahl der Leerfahrten')}")
        
        lines.append("\n**Fahrerverhalten:**")
        lines.append(self._get_value(self.safar_fields, "Fahrerverhalten"))
        return "\n".join(lines)
        
    def copy_safar(self):
        final_text = self._generate_safar_text()
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("Safar Report wurde kopiert:\n" + final_text)

    def _generate_bhg_text(self):
        lines = ["**Report Bad Homburg**", ""]
        
        bhg_order = ["Offene Aufträge bei der Übergabe", "Auftragslage bei der Übergabe", "Fahrerplanung"]
        for key in bhg_order:
            value = self._get_value(self.bhg_fields, key)
            if value:
                lines.append(f"{key}: {value}")

        lines.append("\n**AP Wartezeit ab 16:00 Uhr:**")
        wartezeiten = ["16:00 – 18:00 Uhr", "18:00 – 20:00 Uhr", "20:00 – 21:00 Uhr", "21:00 – 23:00 Uhr", "Ab 23 Uhr"]
        for zeit in wartezeiten:
            value = self._get_value(self.bhg_fields, f'Wartezeit {zeit}')
            if value: lines.append(f"{zeit}: {value}")
        
        lines.append("\n**Abgesagte Aufträge:**")
        lines.append(f"Abgesagte Aufträge: {self._get_value(self.bhg_fields, 'Abgesagte Aufträge')}")
        if self._get_value(self.bhg_fields, "Abgesagte Aufträge") == "Ja":
            lines.append(f"ID: {self._get_value(self.bhg_fields, 'ID')}")
            lines.append(f"Grund: {self._get_value(self.bhg_fields, 'Grund')}")
        return "\n".join(lines)

    def copy_bhg(self):
        final_text = self._generate_bhg_text()
        self.clipboard_clear()
        self.clipboard_append(final_text)
        print("BHG Report wurde kopiert:\n" + final_text)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("NightDUTY Abfragetool")
        self.geometry("1200x800")
        self.configure(fg_color=COLOR_BLACK)
        self.open_toplevels = []
        self.nav_buttons = {}
        self.icon_images = {}

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Navigationsleiste (Sidebar) ---
        self.sidebar_frame = customtkinter.CTkFrame(self, width=250, corner_radius=0, fg_color=COLOR_DARK_GREY)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1) # Spacer row

        # Logo in der Sidebar
        try:
            logo_image_data = Image.open(resource_path("logo.png"))
            logo_image = customtkinter.CTkImage(light_image=logo_image_data, dark_image=logo_image_data, size=(200, 50))
            logo_label = customtkinter.CTkLabel(self.sidebar_frame, image=logo_image, text="")
            logo_label.grid(row=0, column=0, padx=20, pady=(20, 15))
        except (FileNotFoundError, UnidentifiedImageError, tkinter.TclError):
            logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="NIGHTDUTY", font=("Impact", 30), text_color=COLOR_RED)
            logo_label.grid(row=0, column=0, padx=20, pady=(20, 15))

        # --- Navigations-Buttons ---
        buttons_data = [
            ("Abklärung Panne/Unfall", "🔧", PanneUnfallForm, COLOR_RED, "Umfassende Abklärung von Pannen und Unfällen."),
            ("Annahme Ölspur", "💧", OelspurForm, COLOR_BLUE, "Erfassung von Ölspuren und Umwelteinsätzen."),
            ("Annahme Mobi", "📱", MobiForm, COLOR_YELLOW, "Bearbeitung von Mobilitätsgarantie-Fällen."),
            ("Annahme Kilian", "🚛", KilianForm, COLOR_GREEN, "Aufträge für die Polizei, GDV und Bus/LKW."),
            ("Annahme Rudolph", "👮", RudolphForm, COLOR_PURPLE, "Umsetzungen und Sicherstellungen für FUBZ/BVG."),
            ("Annahme Wehner Motors", "🛠️", WehnerForm, COLOR_ORANGE, "PKW, Polizei, LKW und Ölspur Aufträge."),
            ("Falschparker | Privat", "🅿️", FalschparkerPrivatForm, COLOR_TEAL, "Private Falschparker-Meldungen."),
            ("Annahme Unterhaslberger", "🏗️", UnterhaslbergerForm, COLOR_TEAL, "Pannen, Unfälle und Sicherstellungen."),
            ("Report Safar & BHG", "📊", SafarBHGReportForm, COLOR_RED, "Tägliche Reports für Safar und Bad Homburg.", "Ilias")
        ]
        
        hover_map = {
            COLOR_RED: COLOR_HOVER_RED,
            COLOR_BLUE: COLOR_HOVER_BLUE,
            COLOR_YELLOW: COLOR_HOVER_YELLOW,
            COLOR_GREEN: COLOR_HOVER_GREEN,
            COLOR_PURPLE: COLOR_HOVER_PURPLE,
            COLOR_ORANGE: COLOR_HOVER_ORANGE,
            COLOR_TEAL: COLOR_HOVER_TEAL,
        }

        for i, (text, icon, form_class, color, desc, *pw) in enumerate(buttons_data, start=1):
            password = pw[0] if pw else None
            hover_color = hover_map.get(color, COLOR_LIGHT_GREY)
            text_color = COLOR_BLACK if color == COLOR_YELLOW else "white"

            # Emoji als Bild erstellen
            emoji_img = create_emoji_image(icon, 20, text_color)
            ctk_emoji_img = customtkinter.CTkImage(light_image=emoji_img, dark_image=emoji_img, size=(20, 20))
            self.icon_images[text] = ctk_emoji_img # Referenz behalten

            button = customtkinter.CTkButton(
                self.sidebar_frame,
                text=text,
                image=ctk_emoji_img,
                compound="left",
                font=("Calibri", 17, "bold"),
                anchor="w",
                height=50,
                corner_radius=8,
                fg_color=color,
                hover_color=hover_color,
                text_color=text_color,
                command=lambda fc=form_class, pw=password, txt=text, ic=ctk_emoji_img, clr=color: self.open_form(fc, pw, txt, ic, clr)
            )
            button.grid(row=i, column=0, sticky="ew", padx=15, pady=8)
            self.nav_buttons[text] = button

        # Zeit-Anzeige in der Sidebar
        self.time_label = customtkinter.CTkLabel(self.sidebar_frame, text="", font=("Calibri", 12), text_color="gray")
        self.time_label.grid(row=11, column=0, padx=15, pady=15, sticky="s")

        # --- Hauptbereich (Content Area) ---
        self.main_frame = customtkinter.CTkFrame(self, fg_color=COLOR_BLACK, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Willkommens-Nachricht im Hauptbereich (NEUES HAMMER-DESIGN)
        self.create_awesome_welcome_screen()

        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.update_time()

    def create_awesome_welcome_screen(self):
        """Erstellt den neuen, professionelleren und 'geileren' Willkommensbildschirm."""
        
        # Container für das gesamte Layout, um es zentriert zu halten
        welcome_container = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        welcome_container.pack(expand=True, padx=50, pady=30)

        # --- Titel Sektion ---
        title_frame = customtkinter.CTkFrame(welcome_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 5))
        
        # Haupttitel "Willkommen"
        title_label = customtkinter.CTkLabel(title_frame, text="Willkommen", font=("Calibri", 72, "bold"), text_color="white", anchor="w")
        title_label.pack(anchor="w")
        
        # Rote Akzentlinie
        accent_line = customtkinter.CTkFrame(title_frame, fg_color=COLOR_RED, height=4, width=150, corner_radius=2)
        accent_line.pack(anchor="w", pady=(0, 25))

        # Untertitel
        subtitle_label = customtkinter.CTkLabel(title_frame, text="im NightDUTY Abfragetool. Effizient. Strukturiert. Professionell.", font=("Calibri", 20), text_color=COLOR_LIGHT_GREY, anchor="w")
        subtitle_label.pack(anchor="w")

        # --- Haupt-Inhalt (zweigeteilt) ---
        content_frame = customtkinter.CTkFrame(welcome_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=40)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # --- Linke Seite: Quick Access Panel ---
        quick_access_panel = customtkinter.CTkFrame(content_frame, fg_color=COLOR_DARK_GREY, corner_radius=15, border_width=1, border_color=COLOR_MEDIUM_GREY)
        quick_access_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 25))
        
        customtkinter.CTkLabel(quick_access_panel, text="Quick Access", font=("Calibri", 22, "bold"), text_color="white").pack(pady=(20, 15), padx=25, anchor="w")

        # Funktion zum Erstellen der Listeneinträge
        def create_access_item(parent, icon, title, description):
            item_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
            item_frame.pack(fill="x", padx=25, pady=12)
            customtkinter.CTkLabel(item_frame, text=icon, font=("Segoe UI Emoji", 24), text_color=COLOR_RED).pack(side="left", padx=(0, 15))
            text_frame = customtkinter.CTkFrame(item_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x")
            customtkinter.CTkLabel(text_frame, text=title, font=("Calibri", 16, "bold"), anchor="w").pack(fill="x")
            customtkinter.CTkLabel(text_frame, text=description, font=("Calibri", 13), text_color=COLOR_LIGHT_GREY, anchor="w").pack(fill="x")

        create_access_item(quick_access_panel, "🔧", "Abklärung Panne/Unfall", "Geführte Erfassung aller relevanten Details.")
        create_access_item(quick_access_panel, "💧", "Annahme Ölspur", "Erfassung von Ölspuren und Umwelteinsätzen.")
        create_access_item(quick_access_panel, "📱", "Annahme Mobi", "Schnelle Bearbeitung von Mobilitätsfällen.")

        # --- Rechte Seite: Maskottchen ---
        mascot_stage = customtkinter.CTkFrame(content_frame, fg_color="transparent")
        mascot_stage.grid(row=0, column=1, sticky="nsew", padx=(25, 0))

        try:
            mascot_image_data = Image.open(resource_path("maskottchen.png"))
            mascot_image = customtkinter.CTkImage(light_image=mascot_image_data, dark_image=mascot_image_data, size=(320, 320)) 
            mascot_label = customtkinter.CTkLabel(mascot_stage, image=mascot_image, text="")
            mascot_label.pack(expand=True, anchor="center")
        except (FileNotFoundError, UnidentifiedImageError, tkinter.TclError) as e:
            print(f"Maskottchen-Bild konnte nicht geladen werden: {e}")
            error_label = customtkinter.CTkLabel(mascot_stage, text="Maskottchen\nnicht gefunden.", font=("Calibri", 16))
            error_label.pack(expand=True, anchor="center")

    def update_time(self):
        jetzt = datetime.now()
        zeit_string = jetzt.strftime("%A, %d. %B %Y | %H:%M:%S")
        self.time_label.configure(text=zeit_string)
        self.after(1000, self.update_time)

    def open_form(self, form_class, password, header_text, header_icon, header_color):
        if not form_class:
            return

        if password:
            dialog = PasswordDialog(self)
            entered_password = dialog.get_password()
            if entered_password != password:
                return

        new_window = form_class(
            master=self,
            header_text=header_text,
            header_icon=header_icon,
            header_color=header_color
        )
        self.open_toplevels.append(new_window)
        new_window.protocol("WM_DELETE_WINDOW", lambda w=new_window: self.on_window_close(w))
        new_window.after(10, new_window.lift)
        new_window.after(20, new_window.focus_force)

    def on_window_close(self, window):
        self.open_toplevels.remove(window)
        window.destroy()
    
    def on_app_close(self):
        for window in self.open_toplevels:
            window.destroy()
        self.destroy()


if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    app = App()
    app.mainloop()