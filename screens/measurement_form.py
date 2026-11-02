# =============================================================================
# screens/measurement_form.py — Urdu measurement form screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils.constants import (
    COLORS, FONTS, MEASUREMENT_FIELDS, MEASUREMENT_CHECKBOXES
)


class MeasurementFormScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
        self._cid = None
        self._entries = {}
        self._check_vars = {}
        self._build()

    # ─── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"],
                            corner_radius=0, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)

        ctk.CTkButton(
            hdr, text="← Back", font=FONTS["body"],
            fg_color="transparent", hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_secondary"],
            command=self._go_back
        ).pack(side="left", padx=12, pady=16)

        ctk.CTkLabel(
            hdr, text="📏  Measurement Form  —  ناپ کا فارم",
            font=FONTS["h2"], text_color=COLORS["gold"]
        ).pack(side="left", padx=8, pady=16)

        ctk.CTkButton(
            hdr, text="💾  Save Measurement",
            font=FONTS["h5"],
            fg_color=COLORS["gold"], hover_color=COLORS["gold_dark"],
            text_color="#000", corner_radius=8,
            command=self._save
        ).pack(side="right", padx=16, pady=16)

        ctk.CTkButton(
            hdr, text="🕐  View History",
            font=FONTS["body_sm"],
            fg_color="transparent", hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_secondary"], corner_radius=8,
            command=self._view_history
        ).pack(side="right", padx=4, pady=16)

        # Body
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                      corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        # Customer info banner
        self._banner = ctk.CTkFrame(body, fg_color=COLORS["gold_bg"],
                                    corner_radius=10, border_width=1,
                                    border_color=COLORS["gold_dark"])
        self._banner.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        self._banner_lbl = ctk.CTkLabel(
            self._banner, text="",
            font=FONTS["h4"], text_color=COLORS["gold"]
        )
        self._banner_lbl.pack(side="left", padx=20, pady=12)

        # Main register card
        card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"],
                            corner_radius=14, border_width=1,
                            border_color=COLORS["border"])
        card.grid(row=1, column=0, sticky="nsew", padx=24, pady=12)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        # Register header line
        reg_hdr = ctk.CTkFrame(card, fg_color=COLORS["gold"],
                               corner_radius=0, height=3)
        reg_hdr.grid(row=0, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(
            card, text="ناپ رجسٹر",
            font=FONTS["urdu_xl"], text_color=COLORS["gold"]
        ).grid(row=1, column=0, columnspan=2, pady=(12, 4))

        # Left column: Kameez measurements
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="قمیض / کرتہ",
                     font=FONTS["urdu_lg"], text_color=COLORS["text_secondary"]
                     ).grid(row=0, column=0, columnspan=2, pady=(0, 8))

        kameez_fields = [
            ("length","لمبائی","e.g. 44"),
            ("sleeve","بازو","e.g. 25"),
            ("shoulder","کندھا / تیرا","e.g. 18"),
            ("chest","چھاتی","e.g. 42"),
            ("belly","پیٹ","e.g. 40"),
            ("ghera","گھیرہ","e.g. 44"),
            ("collar_size","کالر سائز","e.g. 15"),
            ("cuff_size","کف سائز","e.g. 6"),
            ("daman","دامن","e.g. 14"),
        ]
        for i, (key, ur_label, ph) in enumerate(kameez_fields):
            self._meas_row(left, i+1, key, ur_label, ph)

        # Vertical divider
        div = ctk.CTkFrame(card, width=1, fg_color=COLORS["border"], corner_radius=0)
        div.grid(row=2, column=0, sticky="nse", padx=(0, 0))

        # Right column: Shalwar + options
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.grid(row=2, column=1, sticky="nsew", padx=12, pady=8)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="شلوار",
                     font=FONTS["urdu_lg"], text_color=COLORS["text_secondary"]
                     ).grid(row=0, column=0, columnspan=2, pady=(0, 8))

        shalwar_fields = [
            ("trouser_length","شلوار لمبائی","e.g. 40"),
            ("trouser_bottom","پائنچہ","e.g. 22"),
            ("waist","کمر","e.g. 38"),
        ]
        for i, (key, ur_label, ph) in enumerate(shalwar_fields):
            self._meas_row(right, i+1, key, ur_label, ph)

        # Checkboxes section
        ctk.CTkLabel(right, text="اختیارات",
                     font=FONTS["urdu_md"], text_color=COLORS["text_secondary"]
                     ).grid(row=5, column=0, columnspan=2, pady=(16, 4), sticky="e")

        self._build_checkboxes(right, start_row=6)

        # Design notes — full width below both columns
        notes_frame = ctk.CTkFrame(card, fg_color=COLORS["bg_light"],
                                   corner_radius=10)
        notes_frame.grid(row=3, column=0, columnspan=2, sticky="ew",
                         padx=16, pady=(8, 0))
        notes_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(notes_frame, text="ڈیزائن / اسٹائل نوٹ",
                     font=FONTS["urdu_md"], text_color=COLORS["gold"],
                     anchor="e"
                     ).grid(row=0, column=0, sticky="e", padx=16, pady=(12, 2))

        self._design_notes = ctk.CTkTextbox(
            notes_frame, height=80, font=FONTS["body"],
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self._design_notes.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        ctk.CTkLabel(notes_frame, text="اضافی تفصیل",
                     font=FONTS["urdu_md"], text_color=COLORS["gold"],
                     anchor="e"
                     ).grid(row=2, column=0, sticky="e", padx=16, pady=(4, 2))

        self._additional_notes = ctk.CTkTextbox(
            notes_frame, height=60, font=FONTS["body"],
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self._additional_notes.grid(row=3, column=0, sticky="ew",
                                    padx=16, pady=(0, 16))

        # Bottom save
        ctk.CTkButton(
            body, text="💾  Save Measurement  /  ناپ محفوظ کریں",
            font=FONTS["h4"],
            fg_color=COLORS["gold"], hover_color=COLORS["gold_dark"],
            text_color="#000000", corner_radius=12, height=50,
            command=self._save
        ).grid(row=2, column=0, padx=24, pady=20, sticky="ew")

    def _meas_row(self, parent, row, key, ur_label, placeholder):
        """Create one measurement row: Urdu label (right) + entry (left)."""
        inner = ctk.CTkFrame(parent, fg_color=COLORS["bg_light"], corner_radius=8)
        inner.grid(row=row, column=0, sticky="ew", pady=3, padx=2)
        inner.grid_columnconfigure(0, weight=1)

        # Urdu label on right side
        ctk.CTkLabel(
            inner, text=ur_label,
            font=FONTS["urdu_md"], text_color=COLORS["text_secondary"],
            anchor="e", width=130
        ).grid(row=0, column=1, padx=(4, 12), pady=6, sticky="e")

        entry = ctk.CTkEntry(
            inner, placeholder_text=placeholder,
            font=FONTS["body"], height=34, width=100,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            justify="center"
        )
        entry.grid(row=0, column=0, padx=(12, 4), pady=6)
        self._entries[key] = entry

    def _build_checkboxes(self, parent, start_row):
        """Build checkbox options in a 2-column grid."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_light"], corner_radius=8)
        frame.grid(row=start_row, column=0, columnspan=2, sticky="ew",
                   padx=2, pady=4)

        for i, (key, ur_label, en_label) in enumerate(MEASUREMENT_CHECKBOXES):
            var = tk.IntVar()
            cb = ctk.CTkCheckBox(
                frame,
                text=ur_label,
                variable=var,
                font=FONTS["urdu_sm"],
                text_color=COLORS["text_primary"],
                fg_color=COLORS["gold"],
                hover_color=COLORS["gold_dark"],
                checkmark_color="#000"
            )
            r, c = divmod(i, 2)
            cb.grid(row=r, column=c, sticky="e", padx=10, pady=4)
            self._check_vars[key] = var

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _collect_data(self):
        data = {}
        for key, entry in self._entries.items():
            data[key] = entry.get().strip()
        for key, var in self._check_vars.items():
            data[key] = var.get()
        data["design_notes"]     = self._design_notes.get("1.0", "end-1c").strip()
        data["additional_notes"] = self._additional_notes.get("1.0", "end-1c").strip()
        return data

    def _populate(self, meas):
        if not meas:
            return
        for key, entry in self._entries.items():
            entry.delete(0, "end")
            entry.insert(0, meas.get(key, "") or "")
        for key, var in self._check_vars.items():
            var.set(int(meas.get(key, 0) or 0))
        self._design_notes.delete("1.0", "end")
        self._design_notes.insert("1.0", meas.get("design_notes","") or "")
        self._additional_notes.delete("1.0", "end")
        self._additional_notes.insert("1.0", meas.get("additional_notes","") or "")

    def _clear(self):
        for entry in self._entries.values():
            entry.delete(0, "end")
        for var in self._check_vars.values():
            var.set(0)
        self._design_notes.delete("1.0", "end")
        self._additional_notes.delete("1.0", "end")

    def _save(self):
        if not self._cid:
            return
        data = self._collect_data()
        self.db.save_measurement(self._cid, data)
        messagebox.showinfo("Saved", "✅  Measurement saved successfully!")
        self._go_back()

    def _go_back(self):
        if self._cid:
            self.app.show_screen("customer_profile", customer_id=self._cid)
        else:
            self.app.show_screen("customers")

    def _view_history(self):
        if self._cid:
            self.app.show_screen("customer_profile", customer_id=self._cid)
            self.app.screens["customer_profile"]._show_tab("History")

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, customer_id=None, **kwargs):
        if customer_id:
            self._cid = customer_id
        if not self._cid:
            return

        cust = self.db.get_customer(self._cid)
        self._banner_lbl.configure(
            text=f"👤  {cust['name']}  —  شماریہ نمبر: #{cust['serial_number']}  —  📱 {cust.get('phone','')}"
        )

        meas = self.db.get_measurement(self._cid)
        self._clear()
        self._populate(meas)
