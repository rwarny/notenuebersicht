import tkinter as tk
from constants import *
from storage import load_subjects, save_subjects
from tkinter import ttk, messagebox, filedialog
from grade import Grade
from subject import Subject
import csv
import os
import json

class GradesUI():
    """Hauptfenster der Notenübersicht-Anwendung mit allen Tabs und Funktionen"""
    def __init__(self):
        # Hauptfenster erstellen
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.config(bg=COLORS['bg'])

        self.subjects = load_subjects(JSON_FILENAME)
        self.laod_saved_thresholds()

        # Tab Container
        self.notebook = ttk.Notebook(self.root)
        lek_tab = tk.Frame(self.notebook, bg=COLORS['bg'])
        self.notebook.add(lek_tab, text="LEK hinzufügen")

        uebersicht_tab = tk.Frame(self.notebook, bg=COLORS['bg'])
        self.notebook.add(uebersicht_tab, text="Übersicht")

        fdetails_tab = tk.Frame(self.notebook, bg=COLORS['bg'])
        self.notebook.add(fdetails_tab, text="Fach Details")

        statistik_tab = tk.Frame(self.notebook, bg=COLORS['bg'])
        self.notebook.add(statistik_tab, text="Statistiken")

        einstellungen_tab = tk.Frame(self.notebook, bg=COLORS['bg'])
        self.notebook.add(einstellungen_tab, text="Einstellungen")

        self.notebook.pack(fill='both', expand=True)

        # Tabs aufrufen
        self.setup_lek_tab(lek_tab)
        self.setup_uebersicht_tab(uebersicht_tab)
        self.setup_fdetails_tab(fdetails_tab)
        self.setup_statistik_tab(statistik_tab)
        self.setup_einstellungen_tab(einstellungen_tab)
    
    def run(self):
        self.root.mainloop()

    def auto_save(self):
        erfolg = save_subjects(self.subjects, JSON_FILENAME)
        if not erfolg:
            messagebox.showerror("FEHLER", "Daten konnten nicht gespeichert werdedn")

    def setup_lek_tab(self, lek_tab):

        # Horizontal Zentrieren: Leere Spalten Links und recht mit Gewichtung
        lek_tab.grid_columnconfigure(0, weight=1)
        lek_tab.grid_columnconfigure(3, weight=1)

        # Vertikal Zentrieren: Leere Zeilen oben und unten
        lek_tab.grid_rowconfigure(0, weight=1)
        lek_tab.grid_rowconfigure(6, weight=1)

        faecher = [s.name for s in self.subjects] + ["Neues Fach..."]

        # Label
        self.fach_label = tk.Label(lek_tab, text="Fach:", bg=COLORS['bg'], fg=COLORS['fg'])
        self.fach_label.grid(row=1, column=1, padx=10, pady=10)
        
        # Combobox
        self.fach_combo = ttk.Combobox(lek_tab, values=faecher, state='readonly')
        self.fach_combo.bind("<<ComboboxSelected>>", self.on_fach_selected)
        self.fach_combo.grid(row=1, column=2, padx=10, pady=10)
        
        # Entry (wird später platziert, wenn es benötigt wird)
        self.new_fach_entry = tk.Entry(lek_tab, bg=COLORS['bg'], fg=COLORS['fg'])

        # Maximale Puntke
        max_label = tk.Label(lek_tab, text="Maximale Punkte:", bg=COLORS['bg'], fg=COLORS['fg'])
        max_label.grid(row=2, column=1, padx=10, pady=10)

        self.max_points_entry = tk.Entry(lek_tab, bg=COLORS['bg'], fg=COLORS['fg'])
        self.max_points_entry.grid(row=2, column=2, padx=10, pady=10)

        # Erreichte Punkte
        achieved_label = tk.Label(lek_tab, text="Erreichte Punkte:", bg=COLORS['bg'], fg=COLORS['fg'])
        achieved_label.grid(row=3, column=1, padx=10, pady=10)

        self.achieved_points_entry = tk.Entry(lek_tab, bg=COLORS['bg'], fg=COLORS['fg'])
        self.achieved_points_entry.grid(row=3, column=2, padx=10, pady=10)

        # Live-Vorschau
        self.preview_label = tk.Label(lek_tab, text="", bg=COLORS['bg'], fg=COLORS['fg'], font=(FONT_FAMILY, FONT_SIZES['large']))
        self.preview_label.grid(row=4, column=1, columnspan=2, pady=20)

        self.max_points_entry.bind("<KeyRelease>", self.update_preview)
        self.achieved_points_entry.bind("<KeyRelease>", self.update_preview)

        # Hinzufügen button
        add_button = tk.Button(lek_tab, text="LEK hinzufügen",
                               command=self.add_lek,
                               bg=COLORS['button'], fg="white",
                               font=(FONT_FAMILY, FONT_SIZES['large']),
                               padx=20, pady=10)
        add_button.grid(row=5, column=1, columnspan=2, pady=20)

    def update_preview(self, event=None):
        achieved_points = self.achieved_points_entry.get()
        max_points = self.max_points_entry.get()

        # Beide Felder leer oder ungültige: Vorschau leeren
        if not achieved_points or not max_points:
            self.preview_label.config(text="")
            return
        
        try:
            # Umwandeln in Zahlen
            achieved = float(achieved_points)
            max_p = float(max_points)

            # Validierung: Erreichte <= Maximale
            if achieved > max_p:
                self.preview_label.config(text="Erreichte Punkte können nicht größer als Maximale Punkte sein!", fg="red")
                return
            
            # Grade-Objekt erstellen
            temp_grade = Grade(max_p, achieved)

            # Text erstellen
            text = f"{temp_grade.percentage}% -> Note {temp_grade.grade} ({temp_grade.get_grade_name()})"

            # Anzeigen mit Farbcodierung
            self.preview_label.config(text=text, fg=GRADE_COLORS[temp_grade.grade])
        
        except ValueError:
            self.preview_label.config(text="Bitte nur Zahlen eingeben", fg="red")

    def add_lek(self):
        # Eingaben holen
        fach = self.fach_combo.get()
        max_points = self.max_points_entry.get()
        achieved_points = self.achieved_points_entry.get()

        # Wenn 'Neues Fach...' ...
        if fach == "Neues Fach...":
            fach = self.new_fach_entry.get().strip()

        # Validiereung
        if not fach:
            messagebox.showerror("FEHLER", "Bitte Fach auswählen!")
            return
        
        if not max_points or not achieved_points:
            messagebox.showerror("FEHLER", "Bitte beide Punktzahlen eingeben!")
            return
        
        try:
            max_p = float(max_points)
            if max_p <= 0:
                messagebox.showerror("Fehler", "Maximale Punkte müssen größer als 0 sein!")

            achieved = float(achieved_points)

            if achieved > max_p:
                messagebox.showerror("FEHLER", "Erreichte Punkte können nicht größer als Maximale Punkte sein!")
                return
            
            # Grade erstellen
            grade = Grade(max_p, achieved)

            # Subject finden oder erstellen
            subject = None
            for s in self.subjects:
                if s.name == fach:
                    subject = s
                    break

            if subject is None:
                # Neues Subject erstellen
                from subject import Subject
                subject = Subject(fach)
                self.subjects.append(subject)

            # Grade hinzufügen
            subject.add_grade(grade)

            # Speichern
            self.auto_save()
            self.populate_uebersicht_table()
            self.update_fach_dropdown()
            self.update_statistik_cards()

            # Erfolgsmeldung
            messagebox.showinfo("Erfolg", f"LEK hinzugefügt!\n{grade.percentage}% -> Note {grade.grade}")

            # Felder leeren
            self.max_points_entry.delete(0, tk.END)
            self.achieved_points_entry.delete(0, tk.END)
            self.preview_label.config(text="")
            self.new_fach_entry.delete(0, tk.END)
            self.new_fach_entry.grid_remove()

        except ValueError:
            messagebox.showerror("FEHLER", "Bitte Zahlen eingeben!")

    def setup_uebersicht_tab(self, uebersicht_tab):
        # Style für Dark Mode
        style = ttk.Style()
        style.theme_use("default")

        # Treeview Zeilen
        style.configure("Treeview",
                        background="#1a1a2e",
                        foreground=COLORS['fg'],
                        fieldbackground='#1a1a2e',
                        rowheight=30)
        
        
        # Trwwview Überschriften
        style.configure("Treeview.Heading",
                        background=COLORS['button'],
                        foreground="white",
                        font=(FONT_FAMILY, FONT_SIZES['normal'], "bold"))

        # Spelten-IDs definieren (interne Namen)
        spalten = ("fach", "anzahl", "durchschnitt", "beste", "schlechteste")

        # Treeview erstellen
        tree_frame = tk.Frame(uebersicht_tab, bg=COLORS['bg'])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.uebersicht_tree = ttk.Treeview(tree_frame, columns=spalten, show="headings", height=20)
        self.uebersicht_tree.bind("<Double-1>", self.on_fach_doppelklick)

        # Farben für Noten-Tags definieren
        for note, farbe in GRADE_COLORS.items():
            self.uebersicht_tree.tag_configure(f"note_{note}", background=farbe, foreground="black")

        # Spaltenüberschriften setzen
        self.uebersicht_tree.heading("fach", text="Fach")
        self.uebersicht_tree.heading("anzahl", text="Anzahl LEKs")
        self.uebersicht_tree.heading("durchschnitt", text="Durchschnitt")
        self.uebersicht_tree.heading("beste", text="Beste Note")
        self.uebersicht_tree.heading("schlechteste", text="Schlechteste Note")

        # Spaltenbreiten einstellen
        self.uebersicht_tree.column("fach", width=250, anchor="center")
        self.uebersicht_tree.column("anzahl", width=120, anchor="center")
        self.uebersicht_tree.column("durchschnitt", width=120, anchor="center")
        self.uebersicht_tree.column("beste", width=120, anchor="center")
        self.uebersicht_tree.column("schlechteste", width=150, anchor="center")


        # Scrollbar erstellen
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.uebersicht_tree.yview)
        self.uebersicht_tree.configure(yscrollcommand=scrollbar.set)

        # Treeview und Scrollbar platzieren
        self.uebersicht_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Gesamtdurchschnitt Label
        self.gesamt_label = tk.Label(uebersicht_tab,
                                     text="Gesamtdurchschnitt: -",
                                     bg=COLORS['bg'],
                                     fg=COLORS['accent'],
                                     font=(FONT_FAMILY, FONT_SIZES['title'], 'bold'))
        self.gesamt_label.pack(pady=20)

        self.populate_uebersicht_table()

    def populate_uebersicht_table(self):
        self.uebersicht_tree.delete(*self.uebersicht_tree.get_children())

        for subject in self.subjects:
            # Prüfen ob Fach LEKs hat
            if len(subject.grades) > 0:
                beste = subject.get_best_grade()
                schlechteste = subject.get_worst_grade()
            else:
                beste = "-"
                schlechteste = "-"

            # Zeile einfügen - was kommt in die Klammer?
            # Finde den passenden Tag basierend auf Durchschnitt
            if subject.average:
                note_gerundet = round(subject.average)
                tag = f"note_{note_gerundet}"
            else:
                tag = ""
            self.uebersicht_tree.insert("", "end", values=(subject.name, len(subject.grades), subject.average, beste, schlechteste), tags=(tag,))

        self.update_gesamt_durchschnitt()

    def on_fach_selected(self, event:None):
        if self.fach_combo.get() == "Neues Fach...":
            # Entry-Feld anzeigen
            self.new_fach_entry.grid(row=1, column=3, padx=10, pady=10)
        else:
            # Entry-Feld verstecken
            self.new_fach_entry.grid_remove() 

    def update_fach_dropdown(self):
        faecher = [s.name for s in self.subjects] + ["Neues Fach..."]
        self.fach_combo['values'] = faecher
        self.update_detail_fach_dropdown()

    def update_gesamt_durchschnitt(self):
        durchschnitte = []
        for subject in self.subjects:
            if subject.average:
                durchschnitte.append(subject.average)

        if len(durchschnitte) == 0:
            self.gesamt_label.config(text="Gesamtdurchschnitt: -")
            return

        ergebnis = sum(durchschnitte) / len(durchschnitte)
        self.gesamt_label.config(text=f"Gesamtdurchschnitt: {ergebnis}")
    
    def on_fach_doppelklick(self, event):
        # Welche Zeile wurde angeklickt?
        selection = self.uebersicht_tree.selection()

        # Prüfen ob was ausgewählt ist
        if not selection:
            return
        
        # Werte der ausgewählten Zeile holen
        item = self.uebersicht_tree.item(selection[0])
        fach_name = item['values'][0]

        # Zu Tab 3 wechseln
        self.notebook.select(2)

        # Fach im Dropdown auswählen
        self.detail_fach_combo.set(fach_name)

        # LEK Tabelle und Stats laden
        for subject in self.subjects:
            if subject.name == fach_name:
                self.populate_lek_table(subject)
                self.update_fach_stats(subject)
                self.draw_grade_chart(subject)
                break

    def setup_fdetails_tab(self, fdetails_tab):
        # Oben Fach-Auswahl
        auswahl_frame = tk.Frame(fdetails_tab, bg=COLORS['bg'])
        auswahl_frame.pack(fill="x", padx=20, pady=20)

        # Label
        fach_label = tk.Label(auswahl_frame, text="Fach auswählen.",
                              bg=COLORS['bg'], fg=COLORS['fg'],
                              font=(FONT_FAMILY, FONT_SIZES['normal']))
        fach_label.pack(side="left", padx=(0, 10))

        # Combobox
        self.detail_fach_combo=ttk.Combobox(auswahl_frame, state='readonly', width=30)
        self.detail_fach_combo.pack(side="left")
        self.detail_fach_combo.bind("<<ComboboxSelected>>", self.on_detail_fach_selected)


        self.update_detail_fach_dropdown()

        # Frame für LEK-Tabelle
        lek_frame = tk.Frame(fdetails_tab, bg=COLORS['bg'])
        lek_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # LEk-Treeview
        lek_spalten = ("nr", "max", "erreicht", "prozent", "note")
        self.lek_tree = ttk.Treeview(lek_frame, columns=lek_spalten, show="headings", height=15)

        # Überschriften
        self.lek_tree.heading("nr", text="#")
        self.lek_tree.heading("max", text="Max Puntke")
        self.lek_tree.heading("erreicht", text="Erreicht")
        self.lek_tree.heading("prozent", text="Prozent")
        self.lek_tree.heading("note", text="Note")

        # Spaltenbreiten
        self.lek_tree.column("nr", width=50, anchor="center")
        self.lek_tree.column("max", width=100, anchor="center")
        self.lek_tree.column("erreicht", width=100, anchor="center")
        self.lek_tree.column("prozent", width=100, anchor="center")
        self.lek_tree.column("note", width=100, anchor="center")

        # Platzieren
        self.lek_tree.pack(side="left", fill="both", expand=True)

        # Farben für Noten-Tags definieren
        for note, farbe in GRADE_COLORS.items():
            self.lek_tree.tag_configure(f"note_{note}", background=farbe, foreground='black')

        # Button Frame
        button_frame = tk.Frame(fdetails_tab, bg=COLORS['bg'])
        button_frame.pack(fill="x", padx=20, pady=10)

        # Bearbeiten Button
        edit_button = tk.Button(button_frame, text="LEK bearbeiten",
                                command=self.edit_lek,
                                bg=COLORS['button'], fg='white',
                                font=(FONT_FAMILY, FONT_SIZES['normal']),
                                padx=15, pady=5)
        edit_button.pack(side="left", padx=(0, 10))

        # Löschen Button
        delete_button = tk.Button(button_frame, text="LEK löschen",
                                  command=self.delete_lek,
                                  bg="#F44336", fg="white",
                                  font=(FONT_FAMILY, FONT_SIZES['normal']),
                                  padx=15, pady=5)
        delete_button.pack(side="left")

        # Statistik Frame
        stats_frame = tk.Frame(fdetails_tab, bg=COLORS['bg'])
        stats_frame.pack(fill="x", padx=20, pady=20)

        # Durchschnitt Label
        self.fach_durchschnitt_label = tk.Label(stats_frame, text="Durchschnitt: -",
                                                bg=COLORS['bg'], fg=COLORS['accent'],
                                                font=(FONT_FAMILY, FONT_SIZES['large'], 'bold'))
        self.fach_durchschnitt_label.pack(side="left", padx=(0, 30))

        # Anzahl LEK Label
        self.fach_anzahl_label = tk.Label(stats_frame, text="Anzahl LEKs: -",
                                          bg=COLORS['bg'], fg=COLORS['fg'],
                                          font=(FONT_FAMILY, FONT_SIZES['normal']))
        self.fach_anzahl_label.pack(side="left", padx=(0, 30))

        # Beste Note Label
        self.fach_beste_label = tk.Label(stats_frame, text="Beste: -",
                                         bg=COLORS['bg'], fg=COLORS['fg'],
                                         font=(FONT_FAMILY, FONT_SIZES['normal']))
        self.fach_beste_label.pack(side="left", padx=(0, 30))

        self.fach_schlechteste_label = tk.Label(stats_frame, text="Schlechteste: -",
                                                bg=COLORS['bg'], fg=COLORS['fg'],
                                                font=(FONT_FAMILY, FONT_SIZES['normal']))
        self.fach_schlechteste_label.pack(side="left", padx=(0, 30))

        # Chart Frame
        chart_frame = tk.Frame(fdetails_tab, bg=COLORS['bg'])
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Chart Label
        chart_label = tk.Label(chart_frame, text="📈 Notenentwicklung:",
                               bg=COLORS['bg'], fg=COLORS['fg'],
                               font=(FONT_FAMILY, FONT_SIZES['normal']))
        chart_label.pack(anchor="w")

        # Canvas für Chart
        self.chart_canvas = tk.Canvas(chart_frame, bg='#1a1a2e', width=1000, height=150, highlightthickness=0)
        self.chart_canvas.pack(fill="x", pady=10)

    def on_detail_fach_selected(self, event=None):
        fach_name = self.detail_fach_combo.get()

        # Subject finden
        for subject in self.subjects:
            if subject.name == fach_name:
                self.populate_lek_table(subject)
                self.update_fach_stats(subject)
                self.draw_grade_chart(subject)
                return
            
    def update_detail_fach_dropdown(self):
        faecher = [s.name for s in self.subjects]
        self.detail_fach_combo['values'] = faecher

    def populate_lek_table(self, subject):
        #Alte Einträge lsöchen
        self.lek_tree.delete(*self.lek_tree.get_children())

        # Alle LEKs des Fachs durchlaufen
        for i, grade in enumerate(subject.grades, start=1):
            # Tag für Farbcodierung
            tag = f"note_{grade.grade}"

            # Zeile einfügen
            self.lek_tree.insert("", "end", values=(i, grade.max_points, grade.achieved_points, f"{grade.percentage}%", grade.grade), tags=(tag,))

    def edit_lek(self):
        # Prüfen ob LEK ausgewählt
        selection = self.lek_tree.selection()
        if not selection:
            messagebox.showerror("FEHLER!", "Bitte eine LEK auswählen!")
            return
        
        # Welches Fach ist ausgewählt?
        fach_name = self.detail_fach_combo.get()
        if not fach_name:
            return
        
        # Subject finden
        subject = None
        for s in self.subjects:
            if s.name == fach_name:
                subject = s
                break

        # Index der ausgewählten LEK
        item = self.lek_tree.item(selection[0])
        lek_nr = item['values'][0]
        index = lek_nr - 1

        # Aktuelle Werte holen
        grade = subject.grades[index]

        # Popup-Fenster erstellen
        popup = tk.Toplevel(self.root)
        popup.title(f"LEK #{lek_nr} bearbeiten")
        popup.geometry("300x200")
        popup.config(bg=COLORS['bg'])

        # Max Punkte
        tk.Label(popup, text="Max Punkte:", bg=COLORS['bg'], fg=COLORS['fg']).grid(row=0, column=0, padx=10, pady=10)
        max_entry=tk.Entry(popup, bg=COLORS['bg'], fg=COLORS['fg'])
        max_entry.insert(0, str(grade.max_points))
        max_entry.grid(row=0, column=1, padx=10, pady=10)

        # Erreichte Punkte
        tk.Label(popup, text="Erreicht:", bg=COLORS['bg'], fg=COLORS['fg']).grid(row=1, column=0, padx=10, pady=10)
        achieved_entry=tk.Entry(popup, bg=COLORS['bg'], fg=COLORS['fg'])
        achieved_entry.insert(0, str(grade.achieved_points))
        achieved_entry.grid(row=1, column=1, padx=10, pady=10)

        # Speichern Button
        def speichern():
            try:
                new_max = float(max_entry.get())
                new_achieved = float(achieved_entry.get())

                if new_achieved > new_max:
                    messagebox.showerror("FEHLER", "Erreichte Punkte können nicht größer als Maximale Punkte sein!")
                    return
                
                # Neue Grade erstellen und ersetzen
                new_grade = Grade(new_max, new_achieved)
                subject.grades[index] = new_grade
                subject.calculate_average()

                # Speichern und aktualisieren
                self.auto_save()
                self.populate_lek_table(subject)
                self.populate_uebersicht_table()
                popup.destroy()

            except ValueError:
                messagebox.showerror("FEHLER", "Bitte nur Zahlen eingeben!")

        save_button = tk.Button(popup, text="Speichern", command=speichern,
                                bg=COLORS['button'], fg='white')
        save_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.update_statistik_cards()

    def delete_lek(self):
        # Prüfen ob LEK ausgewählt
        selection = self.lek_tree.selection()
        if not selection:
            messagebox.showerror("FEHLER", "Bitte eine LEK auswählen!")
            return
        
        # Welches Fach ist ausgewählt?
        fach_name = self.detail_fach_combo.get()
        if not fach_name:
            return
        
        # Subject finden
        subject = None
        for s in self.subjects:
            if s.name == fach_name:
                subject = s
                break

        # Index der ausgewählten LEK
        item = self.lek_tree.item(selection[0])
        lek_nr = item['values'][0]
        index = lek_nr - 1

        # Bestätigen
        if not messagebox.askyesno("Löschen?", f"LEK #{lek_nr} wirklich löschen?"):
            return
        
        # Löschen
        subject.remove_grade(index)

        # Speichern und aktualisieren
        self.auto_save()
        self.populate_lek_table(subject)
        self.populate_uebersicht_table()
        self.update_statistik_cards()
    
    def update_fach_stats(self, subject):
        # Durchschnitt mit Farbcodierung
        if subject.average:
            note_gerundet = round(subject.average)
            farbe = GRADE_COLORS[note_gerundet]
            self.fach_durchschnitt_label.config(text=f"📊 Durchschnitt: {subject.average}", fg=farbe)
        else:
            self.fach_durchschnitt_label.config(text="📊 Durchschnitt: -", fg=COLORS['accent'])
        
        self.fach_anzahl_label.config(text=f"📝 Anzahl LEKs: {len(subject.grades)}")
        
        # Prüfen ob LEKs vorhanden
        if len(subject.grades) > 0:
            beste = subject.get_best_grade()
            schlechteste = subject.get_worst_grade()
            self.fach_beste_label.config(text=f"🏆 Beste: {beste}", fg=GRADE_COLORS[beste])
            self.fach_schlechteste_label.config(text=f"⚠️ Schlechteste: {schlechteste}", fg=GRADE_COLORS[schlechteste])
        else:
            self.fach_beste_label.config(text="🏆 Beste: -", fg=COLORS['fg'])
            self.fach_schlechteste_label.config(text="⚠️ Schlechteste: -", fg=COLORS['fg'])

    def draw_grade_chart(self, subject):
        # Canvas leeren
        self.chart_canvas.delete("all")

        # Wenn keine Noten, nichts zeichnen
        if len(subject.grades) == 0:
            return
        
        # Canvas-Größe holen
        self.chart_canvas.update_idletasks()
        width = 1000
        height = 150

        # Padding
        padding = 30
        chart_width = width - (2 * padding)
        chart_height = height - (2 * padding)

        # Noten holen
        noten = subject.get_grade_history()

        # Punkte berechnen
        punkte = []
        for i, note in enumerate(noten):
            # X: gleichmäßig verteilen
            if len(noten) > 1:
                   x = padding + (i * chart_width / len(noten) - 1)
            else:
                x = width / 2


            # Y: Note 1 oben, Note 6 unten
            y = padding + ((note - 1) / 5) * chart_height

            punkte.append((x, y))

        # Linie zeichnen
        if len(punkte) > 1:
            for i in range(len(punkte) - 1):
                self.chart_canvas.create_line(
                    punkte[i][0], punkte[i][1],
                    punkte[i+1][0], punkte[i+1][1],
                    fill=COLORS['accent'], width=2
                )

        # Punkte Zeichnen
        for i, (x, y) in enumerate(punkte):
            note = noten[i]
            farbe = GRADE_COLORS[note]
            self.chart_canvas.create_oval(x-6, y-6, x+6, y+6, fill=farbe, outline='white')

    def setup_statistik_tab(self, statistik_tab):

        # Statistik-Cards Frame
        statistik_cards_frame = tk.Frame(statistik_tab, bg=COLORS['bg'])
        statistik_cards_frame.pack()

        # Gesamtdurchschnitt
        gesamtdurchschnitt_frame =tk.Frame(statistik_cards_frame, bg=COLORS['bg'])
        gesamtdurchschnitt_frame.grid(row=0, column=0)

        gesamtdurchschnitt_titel_label = tk.Label(gesamtdurchschnitt_frame,
                                            text="📊 Gesamtdurchschnitt",
                                            bg=COLORS['bg'], fg=COLORS['fg'],
                                            font=(FONT_FAMILY, FONT_SIZES['normal']))
        gesamtdurchschnitt_titel_label.pack(padx=10, pady=5)

        self.gesamtdurchschnitt_wert_label = tk.Label(gesamtdurchschnitt_frame,
                                                 text="-",
                                                 bg=COLORS['bg'], fg=COLORS['fg'],
                                                 font=(FONT_FAMILY, FONT_SIZES['large'], 'bold'))
        self.gesamtdurchschnitt_wert_label.pack(padx=10, pady=5) 

        # Anzahl der Fächer
        anzahl_faecher_frame = tk.Frame(statistik_cards_frame, bg=COLORS['bg'])
        anzahl_faecher_frame.grid(row=0, column=2)

        anzahl_faecher_label = tk.Label(anzahl_faecher_frame,
                                        text="📝 Gesamt LEKs",
                                        bg=COLORS['bg'], fg=COLORS['fg'],
                                        font=(FONT_FAMILY, FONT_SIZES['normal']))
        anzahl_faecher_label.pack(padx=10, pady=5)

        self.anzahl_faecher_wert_label = tk.Label(anzahl_faecher_frame,
                                                  text="-",
                                                  bg=COLORS['bg'], fg=COLORS['fg'],
                                                  font=(FONT_FAMILY, FONT_SIZES['large'], 'bold'))
        self.anzahl_faecher_wert_label.pack(padx=10, pady=5)


        # Anzahl der LEKs
        anzahl_lek_frame = tk.Frame(statistik_cards_frame, bg=COLORS['bg'])
        anzahl_lek_frame.grid(row=0, column=1)

        anzahl_lek_label = tk.Label(anzahl_lek_frame,
                                    text="📚 Anzahl Fächer",
                                    bg=COLORS['bg'], fg=COLORS['fg'],
                                    font=(FONT_FAMILY, FONT_SIZES['normal']))
        anzahl_lek_label.pack(padx=10, pady=5)

        self.anzahl_lek_wert_label = tk.Label(anzahl_lek_frame,
                                              text="-",
                                              bg=COLORS['bg'], fg=COLORS['fg'],
                                              font=(FONT_FAMILY, FONT_SIZES['large'], 'bold'))
        self.anzahl_lek_wert_label.pack(padx=10, pady=5)

        # Beste note
        beste_frame = tk.Frame(statistik_cards_frame, bg=COLORS['bg'])
        beste_frame.grid(row=0, column=3)

        beste_label = tk.Label(beste_frame,
                               text="🏆 Beste Note",
                               bg=COLORS['bg'], fg=COLORS['fg'],
                               font=(FONT_FAMILY, FONT_SIZES['normal']))
        beste_label.pack(padx=10, pady=5)

        self.beste_wert_label = tk.Label(beste_frame,
                                         text="-",
                                         bg=COLORS['bg'], fg=COLORS['fg'],
                                         font=(FONT_FAMILY, FONT_SIZES['large'], 'bold'))
        self.beste_wert_label.pack(padx=10, pady=5)

        # Schlechteste
        schlechteste_frame = tk.Frame(statistik_cards_frame, bg=COLORS['bg'])
        schlechteste_frame.grid(row=0, column=4)

        schlechteste_label = tk.Label(schlechteste_frame,
                                      text="⚠️ Schlechteste Note",
                                      bg=COLORS['bg'], fg=COLORS['fg'],
                                      font=(FONT_FAMILY, FONT_SIZES['normal']))
        schlechteste_label.pack(padx=10, pady=5)

        self.schlechteste_wert_label = tk.Label(schlechteste_frame,
                                           text="-",
                                           bg=COLORS['bg'], fg=COLORS['fg'],
                                           font=(FONT_FAMILY, FONT_SIZES['large'], 'bold'))
        self.schlechteste_wert_label.pack(padx=10, pady=5)

        # Notenverteilung
        noten_verteilungg_label = tk.Label(statistik_tab,
                                           text="📊 Notenverteilung",
                                           bg=COLORS['bg'], fg=COLORS['fg'],
                                           font=(FONT_FAMILY, FONT_SIZES['title'], 'bold'))
        noten_verteilungg_label.pack(padx=20, pady=10)

        self.noten_verteilung_canvas = tk.Canvas(statistik_tab, bg='#1a1a2e',
                                            width=800, height=220,
                                            highlightthickness=0)
        self.noten_verteilung_canvas.pack(padx=20, pady=10)

        fach_vergleich_label = tk.Label(statistik_tab,
                                        text="📈 Fach-Vergleich",
                                        bg=COLORS['bg'], fg=COLORS['fg'],
                                        font=(FONT_FAMILY, FONT_SIZES['title'], 'bold'))
        fach_vergleich_label.pack(padx=20, pady=10)

        self.fach_vergleich_canvas = tk.Canvas(statistik_tab, bg='#1a1a2e',
                                          width=800, height=250,
                                          highlightthickness=0)
        self.fach_vergleich_canvas.pack(padx=20, pady=10)

        ziel_berechnen_button = tk.Button(statistik_tab, text="🎯 Ziel berechnen", 
                                          font=(FONT_FAMILY, FONT_SIZES['normal']), 
                                          bg=COLORS['button'], fg=COLORS['fg'], 
                                          width=20,
                                          command=self.open_ziel_dialog)
        ziel_berechnen_button.pack(padx=10, pady=5)

        self.update_statistik_cards()
        self.draw_fach_vergleich()

    def update_statistik_cards(self):
        # Anzahl Fächer
        anzahl_faecher = len(self.subjects)
        self.anzahl_faecher_wert_label.config(text=anzahl_faecher)

        # Gesamt LEKs
        gesamt_leks = sum([len(s.grades) for s in self.subjects])
        self.anzahl_lek_wert_label.config(text=gesamt_leks)

        # Gesamtdurchschnitt
        durchschnitte = []
        for subject in self.subjects:
            if subject.average:
                durchschnitte.append(subject.average)

        if len(durchschnitte) == 0:
            self.gesamtdurchschnitt_wert_label.config(text="-")
            ergebnis = None  # Kein Durchschnitt
        else:
            ergebnis = round(sum(durchschnitte) / len(durchschnitte), 2)
            self.gesamtdurchschnitt_wert_label.config(text=ergebnis)


        # Beste Note über ALLE Fächer
        alle_noten  = []
        for subject in self.subjects:
            for grade in subject.grades:
                alle_noten.append(grade.grade)

        if alle_noten:
            beste = min(alle_noten)
            schlechteste= max(alle_noten)
        else:
            beste = "-"
            schlechteste = "-"

        self.beste_wert_label.config(text=beste)
        self.schlechteste_wert_label.config(text=schlechteste)
        self.draw_noten_verteilung()

    def draw_noten_verteilung(self):
        # Canvas leeren
        self.noten_verteilung_canvas.delete("all")

        # Noten ind Dictionary zählen
        noten_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

        for subject in self.subjects:
            for grade in subject.grades:
                noten_count[grade.grade] += 1

        # Maximum finden
        max_count = max(noten_count.values()) if max(noten_count.values()) > 0 else 1

        # Balken zeichnen
        bar_height = 25
        spacing = 8
        left_margin = 80
        max_bar_width= 600

        for note in range(1, 7):
            count = noten_count[note]
            y = (note - 1) * (bar_height + spacing) + 20

            # Beschriftung links
            self.noten_verteilung_canvas.create_text(
                left_margin - 1, y + bar_height / 2,
                text=f"Note {note}:",
                anchor="e",
                fill=COLORS['fg'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )

            # Balken
            bar_width = (count / max_count) * max_bar_width if count > 0 else 0

            # Zeichne Balken nur wenn count > 0
            if count > 0:
                self.noten_verteilung_canvas.create_rectangle(
                    left_margin, y,
                    left_margin + bar_width, y + bar_height,
                    fill=GRADE_COLORS[note]
                )

            # Anzahl links vom Balken
            self.noten_verteilung_canvas.create_text(
                left_margin + bar_width + 10, y + bar_height / 2,
                text=f"{count}x",
                anchor="w",
                fill=COLORS['fg'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
                )
            
    def draw_fach_vergleich(self):
        # Canvas leeren
        self.fach_vergleich_canvas.delete('all')

        # Wenn keien Fäche, nichts zeichnen
        if len(self.subjects) == 0:
            return
        
        # Balken-Parameter
        bar_height = 25
        spacing = 8
        left_margin = 150
        max_bar_width = 500

        for i, subject in enumerate(self.subjects):
            # Nur Fächer mit Noten anzeigen
            if subject.average is None:
                continue

            y = i * (bar_height + spacing) + 20

            # Fachname links
            self.fach_vergleich_canvas.create_text(
                left_margin - 10, y + bar_height / 2,
                text=subject.name,
                anchor="e",
                fill=COLORS['fg'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )

            # Balkenlänge: Note 1 = volle Breite, Note 6 = kurz
            # Formel: (7 - durchschnitt) / 6 + mac_bar_width
            bar_width = ((7 - subject.average) / 6) * max_bar_width

            # Farbe basierend auf gerundetem Durchschnitt
            note_gerundet = round(subject.average)
            farbe = GRADE_COLORS[note_gerundet]

            # Balken zeichnen
            self.fach_vergleich_canvas.create_rectangle(
                    left_margin, y,
                    left_margin + bar_width, y + bar_height,
                    fill=farbe
                )
            
            # Durchschnitt rechts vom Balken
            self.fach_vergleich_canvas.create_text(
                left_margin + bar_width + 10, y + bar_height / 2,
                text=f"({subject.average})",
                anchor="e",
                fill=COLORS['fg'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
                )

    def open_ziel_dialog(self):
        popup = tk.Toplevel(self.root)
        popup.title("🎯 Ziel Berechnung")
        popup.geometry("600x600")
        popup.config(bg=COLORS['bg'])

        # Übersicht
        titel = tk.Label(popup, text="Was brauchst du?",
                         bg=COLORS['bg'], fg=COLORS['accent'],
                         font=(FONT_FAMILY, FONT_SIZES['title'], 'bold'))
        titel.pack(pady=20)

        # MODUS 1: PUNKTE FÜR NOTE
        benoetigte_punkte_frame = tk.Frame(popup, bg="#1a2332", padx=15, pady=15)
        benoetigte_punkte_frame.pack(fill="x", padx=20, pady=10)

        # Überschrift für Modus 1
        tk.Label(benoetigte_punkte_frame, text="📝 Punkte für Note berechnen",
                 bg='#1a2332', fg=COLORS['fg'],
                 font=(FONT_FAMILY, FONT_SIZES['normal'], 'bold')).pack(anchor="w")
        
        # Eingabezeile
        eingabe_frame1 = tk.Frame(benoetigte_punkte_frame, bg='#1a2332')
        eingabe_frame1.pack(fill="x", pady=10)

        #"Ich will Note" + Dropdown + "bei" + Entry + "Punkte"
        tk.Label(eingabe_frame1, text="Ich will Note",
             bg='#1a2332', fg=COLORS['fg']).pack(side="left")
    
        note_combo = ttk.Combobox(eingabe_frame1, values=[1, 2, 3, 4, 5, 6],
                                width=5, state='readonly')
        note_combo.pack(side="left", padx=5)
        
        tk.Label(eingabe_frame1, text="bei max.",
                bg='#1a2332', fg=COLORS['fg']).pack(side="left")
        
        max_entry = tk.Entry(eingabe_frame1, width=8, bg=COLORS['bg'], fg=COLORS['fg'])
        max_entry.pack(side="left", padx=5)
        
        tk.Label(eingabe_frame1, text="Punkten",
                bg='#1a2332', fg=COLORS['fg']).pack(side="left")
        
        # Berechnen-Button für Modus 1
        def berechne_punkte():
            note = note_combo.get()
            max_punkte = max_entry.get()
            
            if not note or not max_punkte:
                ergebnis1.config(text="Bitte alles ausfüllen!", fg="red")
                return
            
            try:
                note_int = int(note)
                max_p = float(max_punkte)
                
                # Berechnung aufrufen (statische Methode aus grade.py!)
                needed = Grade.calculate_required_points(note_int, max_p)
                
                ergebnis1.config(text=f"✅ Du brauchst mindestens {needed} Punkte!", 
                                fg=COLORS['accent'])
            except ValueError:
                ergebnis1.config(text="Bitte gültige Zahlen eingeben!", fg="red")

        
        berechnen_button = tk.Button(eingabe_frame1, text="Berechnen",
                                     font=(FONT_FAMILY, FONT_SIZES['normal']),
                                     bg=COLORS['button'], fg=COLORS['fg'],
                                     command=berechne_punkte)
        berechnen_button.pack(pady=10)

        # Ergebnis Label für Modus 1:
        ergebnis1 = tk.Label(eingabe_frame1, text="-",
                             bg=COLORS['bg'], fg=COLORS['fg'],
                             font=(FONT_FAMILY, FONT_SIZES['normal']))
        ergebnis1.pack(pady=10)

        # MODUS 2 FÜR DURCHSCHNITT
        frame2 = tk.Frame(popup, bg='#1a2332', padx=15, pady=15)
        frame2.pack(fill="x", padx=20, pady=10)

        # Überschrift für Modus 2
        tk.Label(frame2, text="📊 Note für Durchschnitt berechnen",
                bg='#1a2332', fg=COLORS['fg'],
                font=(FONT_FAMILY, FONT_SIZES['normal'], 'bold')).pack(anchor="w")

        # Eingabezeile
        eingabe_frame2 = tk.Frame(frame2, bg='#1a2332')
        eingabe_frame2.pack(fill="x", pady=10)

        # "Im Fach" + Dropdown + "will ich Durchschnitt" + Dropdown
        tk.Label(eingabe_frame2, text="Im Fach",
                bg='#1a2332', fg=COLORS['fg']).pack(side="left")

        # Fächer-Dropdown (nur Fächer mit LEKs!)
        faecher = [s.name for s in self.subjects if len(s.grades) > 0]
        fach_combo = ttk.Combobox(eingabe_frame2, values=faecher,
                                width=15, state='readonly')
        fach_combo.pack(side="left", padx=5)

        tk.Label(eingabe_frame2, text="will ich Ø",
                bg='#1a2332', fg=COLORS['fg']).pack(side="left")

        # Ziel-Durchschnitt Dropdown (1.0 bis 4.0 in 0.5er Schritten)
        durchschnitt_werte = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
        durchschnitt_combo = ttk.Combobox(eingabe_frame2, values=durchschnitt_werte,
                                        width=5, state='readonly')
        durchschnitt_combo.pack(side="left", padx=5)

        # Schließen Button 
        close_button = tk.Button(popup, text="Schließen",
                                 font=(FONT_FAMILY, FONT_SIZES['normal']),
                                 bg='#F44336', fg='white',
                                 command=popup.destroy)
        close_button.pack(pady=10)

        # Berechnen-Button für Modus 2
        def berechne_note():
            fach_name = fach_combo.get()
            ziel = durchschnitt_combo.get()
            
            if not fach_name or not ziel:
                ergebnis2_label.config(text="Bitte alles ausfüllen!", fg="red")
                return
            
            # Subject finden
            subject = None
            for s in self.subjects:
                if s.name == fach_name:
                    subject = s
                    break
            
            # Berechnung aufrufen (Methode aus subject.py!)
            ziel_float = float(ziel)
            needed = subject.calculate_needed_grade_for_average(ziel_float)
            
            if needed is None:
                ergebnis2_label.config(text="❌ Ziel leider nicht erreichbar!", fg="red")
            else:
                ergebnis2_label.config(text=f"✅ Du brauchst Note {needed} in der nächsten LEK!", 
                                    fg=COLORS['accent'])

        btn2 = tk.Button(frame2, text="Berechnen", command=berechne_note,
                        bg=COLORS['button'], fg='white')
        btn2.pack(pady=5)

        # Ergebnis-Label für Modus 2
        ergebnis2_label = tk.Label(frame2, text="",
                                bg='#1a2332', fg=COLORS['fg'],
                                font=(FONT_FAMILY, FONT_SIZES['normal']))
        ergebnis2_label.pack(pady=5)

    def setup_einstellungen_tab(self, einstellungen_tab):
        # Überschrift
        titel = tk.Label(einstellungen_tab, text="⚙️ Einstellungen",
                         bg=COLORS['bg'], fg=COLORS['accent'],
                         font=(FONT_FAMILY, FONT_SIZES['title'], 'bold'))
        titel.pack(pady=20)

        # Fächer verwalten
        faecher_frame = tk.Frame(einstellungen_tab, bg="#1a2332", padx=20, pady=15)
        faecher_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(faecher_frame, text="📚 Fächer verwalten",
                 bg='#1a2332', fg=COLORS['fg'],
                 font=(FONT_FAMILY, FONT_SIZES['normal'], 'bold')).pack(anchor="w")
        
        # Listenbox mit allen Fächern
        self.faecher_listbox = tk.Listbox(faecher_frame,
                                          bg=COLORS['bg'], fg=COLORS['fg'],
                                          font=(FONT_FAMILY, FONT_SIZES['normal']),
                                          height=6, width=40)
        self.faecher_listbox.pack(pady=10)

        # Listbox füllen
        self.update_faecher_listbox()

        # Button Frame
        button_frame = tk.Frame(faecher_frame, bg='#1a2332')
        button_frame.pack(pady=5)

        # Umbenennen Button
        rename_button = tk.Button(button_frame, text="✏️ Fach umbenennen",
                                  bg=COLORS['button'], fg='white',
                                  font=(FONT_FAMILY, FONT_SIZES['normal']),
                                  command=self.rename_fach)
        rename_button.pack(side="left", padx=(0, 10))

        # Löschen Button
        delete_button = tk.Button(button_frame, text="🗑️ Fach löschen",
                                  bg='#F44336', fg='white',
                                  font=(FONT_FAMILY, FONT_SIZES['normal']),
                                  command=self.delete_fach)
        delete_button.pack(side="left")

        # Schwellenwerte Frame
        schwellen_frame = tk.Frame(einstellungen_tab, bg='#1a2332', padx=20, pady=15)
        schwellen_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(schwellen_frame, text="📊 Noten-Schwellenwerte (in %)",
                 bg='#1a2332', fg=COLORS['fg'], 
                 font=(FONT_FAMILY, FONT_SIZES['normal'], 'bold')).pack(anchor="w")
        
        # Entry Felder für die einzelnen Noten
        self.threshold_entries = {}

        for note in range(1, 7):
            row_frame = tk.Frame(schwellen_frame, bg='#1a2332')
            row_frame.pack(fill="x", pady=2)

            tk.Label(row_frame, text=f"Note {note} ab:",
                     bg='#1a2332', fg=COLORS['fg'],
                     font=(FONT_FAMILY, FONT_SIZES['normal']),
                     width=12, anchor="w").pack(side="left")
            
            entry = tk.Entry(row_frame, bg=COLORS['bg'], fg=COLORS['fg'],
                             font=(FONT_FAMILY, FONT_SIZES['normal']), width=8)
            entry.insert(0, str(GRADE_THRESHOLDS[note]))
            entry.pack(side="left", padx=5)

            tk.Label(row_frame, text="%",
                     bg='#1a2332', fg=COLORS['fg']).pack(side="left")
            
            self.threshold_entries[note] = entry
        
        # Speichern Button
        save_threshold_btn = tk.Button(schwellen_frame, text="💾 Schwellenwerte speichern",
                                       bg=COLORS['button'], fg='white',
                                       font=(FONT_FAMILY, FONT_SIZES['normal']),
                                       command=self.save_thresholds)
        save_threshold_btn.pack(pady=10)

        # Import - Export
        export_frame = tk.Frame(einstellungen_tab, bg='#1a2332', padx=20, pady=15)
        export_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(export_frame, text="💾 Export / Import",
                 bg='#1a2332', fg=COLORS['fg'],
                 font=(FONT_FAMILY, FONT_SIZES['normal'], 'bold')).pack(anchor="w")

        # Button Frame 
        export_btn_frame = tk.Frame(export_frame, bg='#1a2332')
        export_btn_frame.pack(pady=10)

        # Export Button
        export_btn = tk.Button(export_btn_frame, text="📤 Als CSV exportieren",
                               bg=COLORS['button'], fg='white',
                               font=(FONT_FAMILY, FONT_SIZES['normal']),
                               command=self.export_csv)
        export_btn.pack(side="left", padx=(0, 10))
        
        # Import Button
        import_btn = tk.Button(export_btn_frame, text="📥 Aus CSV importieren",
                               bg=COLORS['button'], fg='white',
                               font=(FONT_FAMILY, FONT_SIZES['normal']),
                               command=self.import_csv)
        import_btn.pack(side="left")

    def update_faecher_listbox(self):
        self.faecher_listbox.delete(0, tk.END)
        for subject in self.subjects:
            self.faecher_listbox.insert(tk.END, f"{subject.name} ({len(subject.grades)})")

    def delete_fach(self):
        # Prüfen ob Fach ausgewählt
        selection = self.faecher_listbox.curselection()
        if not selection:
            messagebox.showerror("FEHLER", "Bitte ein Fach auswählen")
            return
        
        index = selection[0]
        fach_name = self.subjects[index].name

        # Warnung anzeigen!
        if not messagebox.askyesno("⚠️ Fach löschen?", 
                                f"'{fach_name}' wirklich löschen?\n\nAlle LEKs werden gelöscht!"):
            return
        
        # Löschen
        self.subjects.pop(index)

        # Speichern und alles aktualisieren
        self.auto_save()
        self.update_faecher_listbox()
        self.update_fach_dropdown()
        self.populate_uebersicht_table()
        self.update_statistik_cards()

    def rename_fach(self):
        # Prüfen ob ein Fach ausgewählt wurde
        selection = self.faecher_listbox.curselection()

        if not selection:
            messagebox.showerror("FEHLER", "Bitte ein Fach auswählen!")
            return
        
        index = selection[0]
        subject = self.subjects[index]
        alter_name = subject.name

        # Popup erstellen
        popup = tk.Toplevel(self.root)
        popup.title("Fach umbenennen")
        popup.geometry("350x150")
        popup.config(bg=COLORS['bg'])

        # Label
        tk.Label(popup, text="Neuer Name:",
                 bg=COLORS['bg'], fg=COLORS['fg'],
                 font=(FONT_FAMILY, FONT_SIZES['normal'])).pack(pady=(20, 5))
        
        # Entry mit aktuellem Namen
        name_entry = tk.Entry(popup, bg=COLORS['bg'], fg=COLORS['fg'],
                              font=(FONT_FAMILY, FONT_SIZES['normal']), width=30)
        name_entry.insert(0, alter_name)
        name_entry.pack(pady=5)

        # Speichern Funktion
        def speichern():
            neuer_name = name_entry.get().strip()

            if not neuer_name:
                messagebox.showerror("FEHLER", "Name darf nicht leer sein!")
                return
            
            # Namen ändern
            subject.name = neuer_name

            # Speichern und aktualisieren
            self.auto_save()
            self.update_faecher_listbox()
            self.update_fach_dropdown()
            self.populate_uebersicht_table()
            self.update_statistik_cards()
            popup.destroy()

        # Speichern Button
        tk.Button(popup, text="Speichern",
                  bg=COLORS['button'], fg='white',
                  font=(FONT_FAMILY, FONT_SIZES['normal']),
                  command=speichern).pack(pady=15)
        
    def save_thresholds(self):
        try:
            neue_werte = {}
            for note in range(1, 7):
                wert = int(self.threshold_entries[note].get())

                # Validierung: Wert muss zwischen 0 und 100 sein
                if wert < 0 or wert > 100:
                    messagebox.showerror("FEHLER", f"Note {note}: Wert muss zwischen 0 und 100 sein!")
                    return
                
                neue_werte[note] = wert

            # Validierung: Werte müssen absteigend sein (1 > 2 > 3 > ...)
            for i in range(1, 6):
                if neue_werte[i] <= neue_werte[i+1]:
                    messagebox.showerror("FEHLER", f"Note {i} muss höher sein als Note {i+1}!")
                    return
                
            # Global aktualisieren
            global GRADE_THRESHOLDS
            GRADE_THRESHOLDS.update(neue_werte)

            # In JSON speichern
            import json
            with open("settings.json", "w") as f:
                json.dump({"thresholds": neue_werte}, f, indent=4)

            messagebox.showinfo("Erfolg", "Schwellenwerte gespeichert!")

        except ValueError:
            messagebox.showerror("FEHLER", "Bitte nur ganze Zahlen eingeben!")

    def laod_saved_thresholds(self):

        if not os.path.exists("settings.json"):
            return
        
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)

            if "thresholds" in data:
                # Global aktualisieren:
                global GRADE_THRESHOLDS
                # Keys von String zu Int konvertieren
                for key, value in data["thresholds"].items():
                    GRADE_THRESHOLDS[int(key)] = value

        except (json.JSONDecodeError, KeyError, Exception):
            pass

    def export_csv(self):

        # Datei-Dialog öffnen
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Dateien", "*.csv")],
            title="CSV exportieren"
        )

        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=";")

                # Kopfzeile
                writer.writerow(["Fach", "Max Punkte", "Erreicht", "Prozent", "Note"])

                # Daten schreiben
                for subject in self.subjects:
                    for grade in subject.grades:
                        writer.writerow([
                            subject.name,
                            grade.max_points,
                            grade.achieved_points,
                            grade.percentage,
                            grade.grade
                        ])

            messagebox.showinfo("Erfolg", f"Daten exportieren nach:\n{filename}")

        except Exception as e:
            messagebox.showerror("FEHLER", f"Export fehlgeschlafen:\n{e}")

    def import_csv(self):

        # Datei-Dialog öffnen
        filename = filedialog.askopenfilename(
            filetypes=[("CSV Dateien", ".csv")],
            title="CSV importieren"
        )

        if not filename:
            return
        
        #Warnung anzeigen
        if not messagebox.askyesno("⚠️ Import", 
                               "Möchtest du die Daten importieren?\n\n"
                               "Bestehende Fächer werden ergänzt,\n"
                               "neue Fächer werden erstellt."):
            return
        
        try:
            with open(filename, "r", encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')

                # Kopfzeile überspringen
                next(reader)

                count = 0
                for row in reader:
                    if len(row) < 3:
                        continue

                    fach_name = row[0]
                    max_points = float(row[1])
                    achieved = float(row[2])

                    # Subject finden oder erstellen
                    subject = None
                    for s in self.subjects:
                        if s.name == fach_name:
                            subject = s
                            break
                    
                    if subject is None:
                        subject = Subject(fach_name)
                        self.subjects.append(subject)

                    # Grade erstellen und hinzufügen
                    grade = Grade(max_points, achieved)
                    subject.add_grade(grade)
                    count += 1
            
            # Speichern und aktualisieren
            self.auto_save()
            self.update_faecher_listbox()
            self.update_fach_dropdown()
            self.populate_uebersicht_table()
            self.update_statistik_cards()

            messagebox.showinfo("Erfolg", f"{count} LEKS importiert!")

        except Exception as e:
            messagebox.showerror("FEHLER", f"Import fehlgeschlafen:\n{e}")
