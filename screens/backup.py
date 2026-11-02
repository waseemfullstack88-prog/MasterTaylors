# =============================================================================
# screens/backup.py — Backup & Restore screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os, csv, shutil
from pathlib import Path
from utils.constants import COLORS, FONTS
from datetime import datetime


class BackupScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
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
        ctk.CTkLabel(hdr, text="💾  Backup & Restore / بیک اپ",
                     font=FONTS["h2"], text_color=COLORS["gold"]
                     ).pack(side="left", padx=28, pady=16)

        # Body
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                      corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        # ── Database info card ──────────────────────────────────────────────
        info_card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=14,
                                 border_width=1, border_color=COLORS["border"])
        info_card.grid(row=0, column=0, columnspan=2, sticky="ew",
                       padx=40, pady=(30, 16))
        ctk.CTkLabel(info_card, text="🗄️  Database Status",
                     font=FONTS["h3"], text_color=COLORS["text_primary"]
                     ).pack(anchor="w", padx=24, pady=(20, 8))

        self._db_path_lbl = ctk.CTkLabel(
            info_card, text="", font=FONTS["body"],
            text_color=COLORS["text_secondary"], wraplength=700, anchor="w"
        )
        self._db_path_lbl.pack(anchor="w", padx=24, pady=2)
        self._db_size_lbl = ctk.CTkLabel(
            info_card, text="", font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self._db_size_lbl.pack(anchor="w", padx=24, pady=(0, 20))

        # ── Backup card ─────────────────────────────────────────────────────
        self._make_action_card(
            body, row=1, col=0,
            icon="📤", title="Create Backup",
            description="Save a backup copy of the database to your chosen folder.\nBackup file is named with the current date and time.",
            btn_text="📤  Backup Now",
            btn_color=COLORS["blue_light"],
            btn_hover=COLORS["blue"],
            command=self._do_backup
        )

        # ── Restore card ────────────────────────────────────────────────────
        self._make_action_card(
            body, row=1, col=1,
            icon="📥", title="Restore Backup",
            description="⚠️  Replace current data with a previous backup.\nAll current data will be replaced!",
            btn_text="📥  Restore Backup",
            btn_color=COLORS["orange_light"],
            btn_hover=COLORS["orange"],
            command=self._do_restore
        )

        # ── Export CSV cards ────────────────────────────────────────────────
        self._make_action_card(
            body, row=2, col=0,
            icon="📋", title="Export Customer List (CSV)",
            description="Export all customer details to a CSV file\nthat can be opened in Excel or Google Sheets.",
            btn_text="📋  Export Customers",
            btn_color=COLORS["teal_light"],
            btn_hover=COLORS["teal"],
            command=self._export_customers
        )

        self._make_action_card(
            body, row=2, col=1,
            icon="💸", title="Export Dues Report (CSV)",
            description="Export all pending dues and balances\nto a CSV file for accounting purposes.",
            btn_text="💸  Export Dues",
            btn_color=COLORS["purple_light"],
            btn_hover=COLORS["purple"],
            command=self._export_dues
        )

        # ── Log area ────────────────────────────────────────────────────────
        ctk.CTkLabel(body, text="Backup Log", font=FONTS["h4"],
                     text_color=COLORS["text_primary"]
                     ).grid(row=3, column=0, columnspan=2, sticky="w",
                            padx=40, pady=(20, 4))
        self._log = ctk.CTkTextbox(body, height=160, font=FONTS["body_sm"],
                                   fg_color=COLORS["bg_card"],
                                   border_color=COLORS["border"],
                                   text_color=COLORS["text_secondary"],
                                   state="disabled")
        self._log.grid(row=4, column=0, columnspan=2, sticky="ew",
                       padx=40, pady=(0, 40))

    def _make_action_card(self, parent, row, col, icon, title, description,
                          btn_text, btn_color, btn_hover, command):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=14,
                            border_width=1, border_color=COLORS["border"])
        card.grid(row=row, column=col, sticky="nsew",
                  padx=(40 if col==0 else 16, 16 if col==0 else 40),
                  pady=8)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=f"{icon}  {title}",
                     font=FONTS["h4"], text_color=COLORS["text_primary"]
                     ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(card, text=description,
                     font=FONTS["body_sm"], text_color=COLORS["text_secondary"],
                     justify="left", wraplength=320
                     ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))
        ctk.CTkButton(card, text=btn_text, font=FONTS["h5"],
                      fg_color=btn_color, hover_color=btn_hover,
                      text_color="#fff", corner_radius=8, height=42,
                      command=command
                      ).grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _log_msg(self, msg: str):
        self._log.configure(state="normal")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.insert("end", f"[{ts}]  {msg}\n")
        self._log.configure(state="disabled")
        self._log.see("end")

    def _do_backup(self):
        dest = filedialog.askdirectory(title="Select Backup Folder")
        if not dest:
            return
        try:
            path = self.db.backup(dest)
            self._log_msg(f"✅  Backup saved: {path}")
            messagebox.showinfo("Backup Complete", f"Backup saved to:\n{path}")
        except Exception as e:
            self._log_msg(f"❌  Backup failed: {e}")
            messagebox.showerror("Error", str(e))

    def _do_restore(self):
        src = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database files","*.db"), ("All files","*.*")]
        )
        if not src:
            return
        if not messagebox.askyesno(
            "Confirm Restore",
            "⚠️  This will replace ALL current data with the backup.\n\nAre you sure?"
        ):
            return
        try:
            self.db.restore(src)
            self._log_msg(f"✅  Restored from: {src}")
            messagebox.showinfo("Restore Complete",
                                "Database restored successfully!\nPlease restart the app.")
        except Exception as e:
            self._log_msg(f"❌  Restore failed: {e}")
            messagebox.showerror("Error", str(e))

    def _export_customers(self):
        path = filedialog.asksaveasfilename(
            title="Save Customer List",
            defaultextension=".csv",
            initialfile=f"customers_{date_str()}.csv",
            filetypes=[("CSV files","*.csv")]
        )
        if not path:
            return
        try:
            customers = self.db.get_all_customers()
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Serial","Name","Phone","Address",
                                 "Reference","Notes","Due Balance","Added"])
                for c in customers:
                    writer.writerow([
                        c["serial_number"], c["name"], c.get("phone",""),
                        c.get("address",""), c.get("reference_name",""),
                        c.get("notes",""), c.get("due_balance",0) or 0,
                        (c.get("created_at","") or "")[:10]
                    ])
            self._log_msg(f"✅  Customers exported: {path}")
            messagebox.showinfo("Exported", f"Customer list saved to:\n{path}")
            os.startfile(path)
        except Exception as e:
            self._log_msg(f"❌  Export failed: {e}")
            messagebox.showerror("Error", str(e))

    def _export_dues(self):
        path = filedialog.asksaveasfilename(
            title="Save Dues Report",
            defaultextension=".csv",
            initialfile=f"dues_report_{date_str()}.csv",
            filetypes=[("CSV files","*.csv")]
        )
        if not path:
            return
        try:
            dues = self.db.get_dues_report()
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Serial","Name","Phone",
                                 "Total Billed","Total Paid","Balance"])
                for d in dues:
                    writer.writerow([
                        d["serial_number"], d["name"], d.get("phone",""),
                        d.get("total_billed",0), d.get("total_paid",0),
                        d.get("balance",0)
                    ])
            self._log_msg(f"✅  Dues exported: {path}")
            messagebox.showinfo("Exported", f"Dues report saved to:\n{path}")
            os.startfile(path)
        except Exception as e:
            self._log_msg(f"❌  Export failed: {e}")
            messagebox.showerror("Error", str(e))

    def _update_db_info(self):
        db_path = str(self.db.DB_FILE)
        self._db_path_lbl.configure(text=f"📁  Location: {db_path}")
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            cust = self.db.get_total_customers()
            self._db_size_lbl.configure(
                text=f"📊  Size: {size/1024:.1f} KB  |  Customers: {cust}"
            )

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, **kwargs):
        self._update_db_info()


def date_str():
    from datetime import date
    return date.today().strftime("%Y-%m-%d")
