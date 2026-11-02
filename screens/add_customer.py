# =============================================================================
# screens/add_customer.py — Add / Edit customer screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from utils.constants import COLORS, FONTS


class AddCustomerScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
        self._edit_id = None   # None = add mode, int = edit mode
        self._build()

    # ─── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self._hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"],
                                  corner_radius=0, height=64)
        self._hdr.grid(row=0, column=0, sticky="ew")
        self._hdr.grid_propagate(False)
        self._hdr_lbl = ctk.CTkLabel(
            self._hdr, text="➕  Add New Customer",
            font=FONTS["h2"], text_color=COLORS["gold"]
        )
        self._hdr_lbl.pack(side="left", padx=28, pady=16)
        ctk.CTkButton(
            self._hdr, text="← Back", font=FONTS["body"],
            fg_color="transparent", hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_secondary"], corner_radius=8,
            command=lambda: self.app.show_screen("customers")
        ).pack(side="right", padx=20, pady=16)

        # Content
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=14,
                            border_width=1, border_color=COLORS["border"])
        card.grid(row=0, column=0, padx=60, pady=30, sticky="nsew")
        card.grid_columnconfigure((0, 1), weight=1)

        self._fields = {}
        self._build_form(card)

    def _lbl(self, parent, text, row, col):
        ctk.CTkLabel(parent, text=text, font=FONTS["h5"],
                     text_color=COLORS["text_secondary"],
                     anchor="w"
                     ).grid(row=row, column=col, sticky="w",
                            padx=(24, 8), pady=(16, 2))

    def _entry(self, parent, key, placeholder, row, col, colspan=1):
        e = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            font=FONTS["body"], height=40,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"]
        )
        e.grid(row=row, column=col, columnspan=colspan,
               sticky="ew", padx=(8, 24), pady=(0, 4))
        self._fields[key] = e
        return e

    def _build_form(self, card):
        # Section title
        ctk.CTkLabel(card, text="Customer Information",
                     font=FONTS["h3"], text_color=COLORS["text_primary"]
                     ).grid(row=0, column=0, columnspan=2, sticky="w",
                            padx=24, pady=(24, 8))
        ctk.CTkFrame(card, height=1, fg_color=COLORS["border"],
                     corner_radius=0
                     ).grid(row=1, column=0, columnspan=2, sticky="ew",
                            padx=24, pady=(0, 8))

        # Serial number
        self._lbl(card, "Serial Number *  (نمبر)", 2, 0)
        serial_frame = ctk.CTkFrame(card, fg_color="transparent")
        serial_frame.grid(row=3, column=0, sticky="ew", padx=(8,24), pady=(0,4))
        serial_frame.grid_columnconfigure(0, weight=1)
        serial_e = ctk.CTkEntry(
            serial_frame, font=FONTS["body"], height=40,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            placeholder_text="Auto-generated or enter existing"
        )
        serial_e.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(
            serial_frame, text="Auto", width=60, height=40,
            fg_color=COLORS["gold_dark"], hover_color=COLORS["gold"],
            text_color="#000", font=FONTS["body_sm"],
            command=self._auto_serial
        ).grid(row=0, column=1, padx=(6, 0))
        self._fields["serial_number"] = serial_e

        # Name
        self._lbl(card, "Customer Name *  (نام)", 2, 1)
        self._entry(card, "name", "Full name", 3, 1)

        # Phone
        self._lbl(card, "Phone Number  (موبائل)", 4, 0)
        self._entry(card, "phone", "e.g. 0300-1234567", 5, 0)

        # Address
        self._lbl(card, "Address / Area  (پتہ)", 4, 1)
        self._entry(card, "address", "Village, area, city", 5, 1)

        # Reference
        self._lbl(card, "Reference / Father Name  (حوالہ)", 6, 0)
        self._entry(card, "reference_name", "Optional", 7, 0)

        # Notes
        self._lbl(card, "General Notes  (نوٹ)", 6, 1)
        self._entry(card, "notes", "Any general notes", 7, 1)

        # Also add measurement checkbox
        self._add_measurement_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            card,
            text="Also open Measurement Form after saving",
            variable=self._add_measurement_var,
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["gold"],
            hover_color=COLORS["gold_dark"],
            checkmark_color="#000"
        ).grid(row=8, column=0, columnspan=2, sticky="w", padx=24, pady=(20, 4))

        # Save button
        self._save_btn = ctk.CTkButton(
            card, text="💾  Save Customer", font=FONTS["h4"],
            fg_color=COLORS["gold"], hover_color=COLORS["gold_dark"],
            text_color="#000000", corner_radius=10, height=46,
            command=self._save
        )
        self._save_btn.grid(row=9, column=0, columnspan=2,
                            padx=24, pady=(8, 30), sticky="ew")

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _auto_serial(self):
        nxt = self.db.get_next_serial()
        e = self._fields["serial_number"]
        e.delete(0, "end")
        e.insert(0, nxt)

    def _get_data(self):
        return {k: e.get().strip() for k, e in self._fields.items()}

    def _save(self):
        data = self._get_data()
        if not data.get("serial_number"):
            messagebox.showwarning("Missing", "Serial number is required.")
            return
        if not data.get("name"):
            messagebox.showwarning("Missing", "Customer name is required.")
            return

        if self._edit_id:
            # Edit mode
            if self.db.serial_exists(data["serial_number"], exclude_id=self._edit_id):
                messagebox.showerror("Duplicate", "Serial number already used by another customer.")
                return
            self.db.update_customer(self._edit_id, data)
            cid = self._edit_id
            messagebox.showinfo("Saved", f"Customer #{data['serial_number']} updated successfully.")
        else:
            # Add mode
            if self.db.serial_exists(data["serial_number"]):
                messagebox.showerror("Duplicate", "Serial number already exists. Use a different number.")
                return
            cid = self.db.add_customer(data)
            messagebox.showinfo("Saved", f"Customer #{data['serial_number']} added successfully.")

        if self._add_measurement_var.get():
            self.app.show_screen("customer_profile", customer_id=cid, open_measurement=True)
        else:
            self.app.show_screen("customer_profile", customer_id=cid)

    def _clear(self):
        for e in self._fields.values():
            e.delete(0, "end")

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, edit_customer_id=None, **kwargs):
        if edit_customer_id:
            self._edit_id = edit_customer_id
            self._hdr_lbl.configure(text="✏️  Edit Customer")
            self._save_btn.configure(text="💾  Update Customer")
            cust = self.db.get_customer(edit_customer_id)
            if cust:
                for key, e in self._fields.items():
                    e.delete(0, "end")
                    e.insert(0, cust.get(key, "") or "")
        else:
            self._edit_id = None
            self._hdr_lbl.configure(text="➕  Add New Customer")
            self._save_btn.configure(text="💾  Save Customer")
            self._clear()
            self._auto_serial()
