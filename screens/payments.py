# =============================================================================
# screens/payments.py — Payments & Dues screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLORS, FONTS, PAYMENT_METHODS
from datetime import date


class PaymentsScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
        self._preset_cid = None
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
        ctk.CTkLabel(hdr, text="💰  Payments & Dues / ادائیگی",
                     font=FONTS["h2"], text_color=COLORS["gold"]
                     ).pack(side="left", padx=28, pady=16)

        body = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left: payment history table
        left = ctk.CTkFrame(body, fg_color=COLORS["bg_dark"], corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(16,8), pady=16)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left, text="Payment History", font=FONTS["h3"],
                     text_color=COLORS["text_primary"]
                     ).grid(row=0, column=0, sticky="w", padx=4, pady=(0,8))

        self._build_table(left)

        # Right: Add Payment form + Dues summary
        right = ctk.CTkScrollableFrame(body, fg_color=COLORS["bg_card"],
                                       corner_radius=14, border_width=1,
                                       border_color=COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew", padx=(0,16), pady=16)
        right.grid_columnconfigure(0, weight=1)
        self._build_form(right)

    def _build_table(self, parent):
        style = ttk.Style()
        style.configure("Pay.Treeview",
                        background=COLORS["tbl_bg"],
                        foreground=COLORS["text_primary"],
                        rowheight=34, fieldbackground=COLORS["tbl_bg"],
                        borderwidth=0, font=("Segoe UI", 11))
        style.configure("Pay.Treeview.Heading",
                        background=COLORS["tbl_header"], foreground=COLORS["gold"],
                        font=("Segoe UI", 11, "bold"), borderwidth=0, relief="flat")
        style.map("Pay.Treeview",
                  background=[("selected", COLORS["tbl_selected"])],
                  foreground=[("selected","#fff")])

        cols = ("Date","Customer","Serial","Order Type","Amount","Method","Notes")
        self._tree = ttk.Treeview(parent, style="Pay.Treeview",
                                  columns=cols, show="headings", selectmode="browse")
        widths = [100, 160, 70, 120, 90, 80, 160]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, minwidth=w, anchor="center")

        sy = ttk.Scrollbar(parent, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sy.set)
        self._tree.grid(row=1, column=0, sticky="nsew")
        sy.grid(row=1, column=1, sticky="ns")

        self._tree.tag_configure("even", background=COLORS["tbl_bg"])
        self._tree.tag_configure("odd",  background=COLORS["tbl_alt"])

    def _build_form(self, parent):
        ctk.CTkLabel(parent, text="Add Payment",
                     font=FONTS["h3"], text_color=COLORS["gold"]
                     ).grid(row=0, column=0, sticky="w", padx=20, pady=(20,4))

        # Customer search
        ctk.CTkLabel(parent, text="Customer *", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=1, column=0, sticky="w", padx=20, pady=(12,2))

        self._cust_var = tk.StringVar()
        self._cust_var.trace_add("write", self._search_cust)
        self._cust_entry = ctk.CTkEntry(
            parent, textvariable=self._cust_var,
            placeholder_text="Search customer...",
            font=FONTS["body"], height=38,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self._cust_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,2))

        self._cust_results = ctk.CTkFrame(parent, fg_color=COLORS["bg_light"],
                                          corner_radius=8)
        self._cust_results.grid(row=3, column=0, sticky="ew", padx=20)

        self._selected_cid = None
        self._selected_lbl = ctk.CTkLabel(parent, text="",
                                          font=FONTS["body_sm"],
                                          text_color=COLORS["green"])
        self._selected_lbl.grid(row=4, column=0, sticky="w", padx=20)

        # Due balance display
        self._due_frame = ctk.CTkFrame(parent, fg_color=COLORS["red_bg"],
                                       corner_radius=8, border_width=1,
                                       border_color=COLORS["red"])
        self._due_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=8)
        self._due_lbl = ctk.CTkLabel(self._due_frame, text="",
                                     font=FONTS["h4"], text_color=COLORS["red_light"])
        self._due_lbl.pack(padx=16, pady=10)

        # Payment date
        ctk.CTkLabel(parent, text="Payment Date", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=6, column=0, sticky="w", padx=20, pady=(8,2))
        self._date_entry = ctk.CTkEntry(parent, font=FONTS["body"], height=38,
                                        fg_color=COLORS["bg_input"],
                                        border_color=COLORS["border"],
                                        text_color=COLORS["text_primary"])
        self._date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self._date_entry.grid(row=7, column=0, sticky="ew", padx=20, pady=(0,4))

        # Amount
        ctk.CTkLabel(parent, text="Amount  (رقم)", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=8, column=0, sticky="w", padx=20, pady=(8,2))
        self._amount_entry = ctk.CTkEntry(parent, placeholder_text="Enter amount in Rs.",
                                          font=FONTS["h4"], height=46,
                                          fg_color=COLORS["bg_input"],
                                          border_color=COLORS["gold_dark"],
                                          text_color=COLORS["gold"])
        self._amount_entry.grid(row=9, column=0, sticky="ew", padx=20, pady=(0,4))

        # Method
        ctk.CTkLabel(parent, text="Payment Method", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=10, column=0, sticky="w", padx=20, pady=(8,2))
        self._method_var = tk.StringVar(value=PAYMENT_METHODS[0])
        ctk.CTkOptionMenu(parent, variable=self._method_var,
                          values=PAYMENT_METHODS, font=FONTS["body"], height=38,
                          fg_color=COLORS["bg_input"],
                          button_color=COLORS["gold_dark"],
                          button_hover_color=COLORS["gold"],
                          text_color=COLORS["text_primary"]
                          ).grid(row=11, column=0, sticky="ew", padx=20, pady=(0,4))

        # Notes
        ctk.CTkLabel(parent, text="Notes  (نوٹ)", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=12, column=0, sticky="w", padx=20, pady=(8,2))
        self._notes_entry = ctk.CTkEntry(parent, placeholder_text="Optional notes",
                                         font=FONTS["body"], height=38,
                                         fg_color=COLORS["bg_input"],
                                         border_color=COLORS["border"],
                                         text_color=COLORS["text_primary"])
        self._notes_entry.grid(row=13, column=0, sticky="ew", padx=20, pady=(0,4))

        # Save button
        ctk.CTkButton(parent, text="💾  Record Payment",
                      font=FONTS["h4"],
                      fg_color=COLORS["green"], hover_color="#1a6e3a",
                      text_color="#fff", corner_radius=10, height=46,
                      command=self._save_payment
                      ).grid(row=14, column=0, sticky="ew", padx=20, pady=(16, 8))

        # Pending dues section
        ctk.CTkFrame(parent, height=1, fg_color=COLORS["border"], corner_radius=0
                     ).grid(row=15, column=0, sticky="ew", padx=20, pady=8)
        ctk.CTkLabel(parent, text="⚠️  Pending Dues Summary",
                     font=FONTS["h4"], text_color=COLORS["orange_light"]
                     ).grid(row=16, column=0, sticky="w", padx=20, pady=(4, 8))

        self._dues_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                                   height=250)
        self._dues_frame.grid(row=17, column=0, sticky="ew", padx=8, pady=(0,20))
        self._dues_frame.grid_columnconfigure(0, weight=1)

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _search_cust(self, *_):
        q = self._cust_var.get().strip()
        for w in self._cust_results.winfo_children():
            w.destroy()
        if not q:
            return
        for c in self.db.search_customers(q)[:5]:
            ctk.CTkButton(
                self._cust_results,
                text=f"#{c['serial_number']}  {c['name']}",
                font=FONTS["body_sm"], fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["text_primary"], anchor="w",
                command=lambda cid=c["id"], n=c["name"], s=c["serial_number"]:
                    self._select_cust(cid, n, s)
            ).pack(fill="x", padx=4, pady=1)

    def _select_cust(self, cid, name, serial):
        self._selected_cid = cid
        self._selected_lbl.configure(text=f"✅  {name}  #{serial}")
        self._cust_var.set("")
        for w in self._cust_results.winfo_children():
            w.destroy()
        due = self.db.get_customer_due(cid)
        if due > 0:
            self._due_frame.configure(fg_color=COLORS["red_bg"],
                                      border_color=COLORS["red"])
            self._due_lbl.configure(
                text=f"⚠️  Due Balance: Rs. {due:,.0f}",
                text_color=COLORS["red_light"]
            )
        else:
            self._due_frame.configure(fg_color=COLORS["green_bg"],
                                      border_color=COLORS["green"])
            self._due_lbl.configure(
                text="✅  No pending dues",
                text_color=COLORS["green"]
            )

    def _save_payment(self):
        if not self._selected_cid:
            messagebox.showwarning("Missing", "Please select a customer.")
            return
        try:
            amount = float(self._amount_entry.get().strip() or 0)
        except ValueError:
            messagebox.showerror("Invalid", "Amount must be a number.")
            return
        if amount <= 0:
            messagebox.showwarning("Invalid", "Amount must be greater than zero.")
            return

        self.db.add_payment({
            "customer_id":     self._selected_cid,
            "payment_date":    self._date_entry.get().strip(),
            "amount":          amount,
            "payment_method":  self._method_var.get(),
            "notes":           self._notes_entry.get().strip(),
        })
        messagebox.showinfo("Saved", f"Payment of Rs. {amount:,.0f} recorded.")
        self._amount_entry.delete(0, "end")
        self._notes_entry.delete(0, "end")
        self._select_cust(self._selected_cid,
                          self._selected_lbl.cget("text").split("  ")[1],
                          "")
        self._load_payments()
        self._load_dues()

    def _load_payments(self):
        self._tree.delete(*self._tree.get_children())
        payments = self.db.get_all_payments()
        for i, p in enumerate(payments):
            tag = "even" if i%2==0 else "odd"
            self._tree.insert("", "end",
                values=(
                    p.get("payment_date",""),
                    p.get("customer_name",""),
                    p.get("serial_number",""),
                    p.get("clothing_type","—") or "—",
                    f"Rs. {p['amount']:,.0f}",
                    p.get("payment_method",""),
                    p.get("notes",""),
                ),
                tags=(tag,)
            )

    def _load_dues(self):
        for w in self._dues_frame.winfo_children():
            w.destroy()
        dues = self.db.get_dues_report()
        if not dues:
            ctk.CTkLabel(self._dues_frame, text="✅  No pending dues!",
                         font=FONTS["body"], text_color=COLORS["green"]
                         ).pack(pady=10)
            return
        for d in dues[:20]:
            row = ctk.CTkFrame(self._dues_frame, fg_color=COLORS["bg_light"],
                               corner_radius=8)
            row.pack(fill="x", pady=2, padx=4)
            ctk.CTkLabel(row, text=f"#{d['serial_number']}  {d['name']}",
                         font=FONTS["body_sm"], text_color=COLORS["text_primary"]
                         ).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=f"Rs. {d['balance']:,.0f}",
                         font=FONTS["h5"], text_color=COLORS["red_light"]
                         ).pack(side="right", padx=10, pady=6)
            row.bind("<Button-1>", lambda e, cid=d.get("id",0):
                     self.app.show_screen("customer_profile", customer_id=cid)
                     if cid else None)

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, customer_id=None, **kwargs):
        self._load_payments()
        self._load_dues()
        if customer_id:
            cust = self.db.get_customer(customer_id)
            if cust:
                self._select_cust(customer_id, cust["name"], cust["serial_number"])
