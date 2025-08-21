from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from typing import Dict

try:
    from .models import Bestellung
    from .queue_service import BestellungsQueue
    from .repository import BestellungsRepository
except ImportError:  # Allow running as a top-level script
    from models import Bestellung
    from queue_service import BestellungsQueue
    from repository import BestellungsRepository


class BestellungsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Bestellungsmanagement")
        self.root.geometry("640x520")
        self.root.config(bg="#f0f0f0")

        repo = BestellungsRepository(Path("bestellungen.json"))
        self.queue = BestellungsQueue(repo)

        self.getraenke_bestellung: Dict[str, int] = {}

        self.getraenke = ["Wasser", "Cola", "Bier", "Wein"]

        main_frame = tk.Frame(root, padx=16, pady=16, bg="#f0f0f0")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Tisch
        tk.Label(main_frame, text="Tischnummer:", font=("Arial", 14), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.tisch_nummer_var = tk.StringVar(value="1")
        tisch_werte = [str(i) for i in range(1, 11)]
        self.tisch_dropdown = ttk.OptionMenu(
            main_frame, self.tisch_nummer_var, tisch_werte[0], *tisch_werte
        )
        self.tisch_dropdown.config(width=15)
        self.tisch_dropdown.grid(row=0, column=1, pady=8)

        # Getränk
        tk.Label(main_frame, text="Getränk:", font=("Arial", 14), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.getraenk_var = tk.StringVar(value=self.getraenke[0])
        self.getraenk_dropdown = ttk.OptionMenu(
            main_frame, self.getraenk_var, self.getraenke[0], *self.getraenke
        )
        self.getraenk_dropdown.config(width=15)
        self.getraenk_dropdown.grid(row=1, column=1, pady=8)

        # Anzahl
        tk.Label(main_frame, text="Anzahl:", font=("Arial", 14), bg="#f0f0f0").grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.anzahl_var = tk.IntVar(value=1)
        self.spinbox_anzahl = tk.Spinbox(
            main_frame, from_=1, to=10, textvariable=self.anzahl_var, font=("Arial", 14)
        )
        self.spinbox_anzahl.grid(row=2, column=1, pady=8)

        # Buttons oben
        self.btn_getraenk_hinzufuegen = tk.Button(
            main_frame,
            text="Getränk hinzufügen",
            command=self.getraenk_hinzufuegen,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            padx=10,
            pady=5,
        )
        self.btn_getraenk_hinzufuegen.grid(row=3, column=0, pady=8, padx=8)

        self.btn_hinzufuegen = tk.Button(
            main_frame,
            text="Bestellung abschicken",
            command=self.bestellung_hinzufuegen,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            padx=10,
            pady=5,
            state=tk.DISABLED,
        )
        self.btn_hinzufuegen.grid(row=3, column=1, pady=8, padx=8)

        # Treeview für Getränke
        tk.Label(main_frame, text="Aktuelle Getränke:", font=("Arial", 14), bg="#f0f0f0").grid(
            row=4, column=0, sticky="w", pady=8
        )
        columns = ("getraenk", "anzahl")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=6)
        self.tree.heading("getraenk", text="Getränk")
        self.tree.heading("anzahl", text="Anzahl")
        self.tree.column("getraenk", width=200, anchor="w")
        self.tree.column("anzahl", width=80, anchor="center")
        self.tree.grid(row=5, column=0, columnspan=2, sticky="nsew")

        # Entfernen-Button
        self.btn_remove = tk.Button(
            main_frame,
            text="Ausgewähltes entfernen",
            command=self.entferne_auswahl,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 12),
            padx=10,
            pady=5,
            state=tk.DISABLED,
        )
        self.btn_remove.grid(row=6, column=0, pady=8, padx=8)

        # Queue Bedienung
        self.btn_abarbeiten = tk.Button(
            main_frame,
            text="Bestellung abarbeiten",
            command=self.bestellung_abarbeiten,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12),
            padx=10,
            pady=5,
        )
        self.btn_abarbeiten.grid(row=6, column=1, pady=8, padx=8)

        self.btn_anzeigen = tk.Button(
            main_frame,
            text="Aktuelle Bestellungen anzeigen",
            command=self.bestellungen_anzeigen,
            bg="#f44336",
            fg="white",
            font=("Arial", 12),
            padx=10,
            pady=5,
        )
        self.btn_anzeigen.grid(row=7, column=0, columnspan=2, pady=8, padx=8)

        # Events
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_buttons_state())

        # Grid expand config
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        self._update_buttons_state()

    def _refresh_tree(self) -> None:
        for i in self.tree.get_children():
            self.tree.delete(i)
        for getraenk, anzahl in self.getraenke_bestellung.items():
            self.tree.insert("", tk.END, values=(getraenk, anzahl))
        self._update_buttons_state()

    def _update_buttons_state(self) -> None:
        has_items = bool(self.getraenke_bestellung)
        self.btn_hinzufuegen.config(state=(tk.NORMAL if has_items else tk.DISABLED))
        selected = self.tree.selection()
        self.btn_remove.config(state=(tk.NORMAL if selected else tk.DISABLED))

    def getraenk_hinzufuegen(self) -> None:
        getraenk = self.getraenk_var.get()
        anzahl = int(self.anzahl_var.get())
        if anzahl <= 0:
            messagebox.showwarning("Hinweis", "Die Anzahl muss größer als 0 sein.")
            return
        self.getraenke_bestellung[getraenk] = self.getraenke_bestellung.get(getraenk, 0) + anzahl
        self._refresh_tree()

    def entferne_auswahl(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        for item_id in selected:
            values = self.tree.item(item_id, "values")
            if values:
                drink = values[0]
                self.getraenke_bestellung.pop(drink, None)
        self._refresh_tree()

    def bestellung_hinzufuegen(self) -> None:
        if not self.getraenke_bestellung:
            messagebox.showwarning("Hinweis", "Füge zuerst Getränke hinzu.")
            return
        try:
            tisch_nummer = int(self.tisch_nummer_var.get())
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Tischnummer.")
            return
        bestellung = Bestellung(tisch_nummer, dict(self.getraenke_bestellung))
        self.queue.bestellung_hinzufuegen(bestellung)
        messagebox.showinfo("Erfolg", "Bestellung hinzugefügt.")
        self.getraenke_bestellung.clear()
        self._refresh_tree()

    def bestellung_abarbeiten(self) -> None:
        bearbeitete_bestellung = self.queue.bestellung_abarbeiten()
        if bearbeitete_bestellung:
            messagebox.showinfo("Erfolg", f"Bestellung bearbeitet: {bearbeitete_bestellung}")
        else:
            messagebox.showinfo("Info", "Keine Bestellungen in der Warteschlange.")

    def bestellungen_anzeigen(self) -> None:
        bestellungen = self.queue.aktuelle_bestellungen()
        if bestellungen:
            text = "\n".join(str(b) for b in bestellungen)
            messagebox.showinfo("Aktuelle Bestellungen", text)
        else:
            messagebox.showinfo("Aktuelle Bestellungen", "Keine Bestellungen in der Warteschlange.")


def main() -> None:
    root = tk.Tk()
    BestellungsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


