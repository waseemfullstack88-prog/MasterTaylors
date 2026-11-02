# =============================================================================
# screens/reports.py — Reports screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from utils.constants import COLORS, FONTS
from datetime import date, timedelta
import os


def _money(v):
    return f"Rs. {v:,.0f}"


class ReportsScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
        self._current_report = "monthly"
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
        ctk.CTkLabel(hdr, text="📊  Reports / رپورٹ",
                     font=FONTS["h2"], text_color=COLORS["gold"]
                     ).pack(side="left", padx=28, pady=16)

        body = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # Toolbar
        toolbar = ctk.CTkFrame(body, fg_color=COLORS["bg_medium"], corner_radius=0)
        toolbar.grid(row=0, column=0, sticky="ew")

        report_types = [
            ("📅 Daily",   "daily"),
            ("📆 Weekly",  "weekly"),
            ("🗓 Monthly", "monthly"),
            ("💸 Dues",    "dues"),
            ("👥 All Customers", "customers"),
        ]
        self._report_btns = {}
        for label, key in report_types:
            b = ctk.CTkButton(
                toolbar, text=label, font=FONTS["body_sm"],
                fg_color="transparent", hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["text_secondary"], corner_radius=6,
                height=34,
                command=lambda k=key: self._show_report(k)
            )
            b.pack(side="left", padx=4, pady=10)
            self._report_btns[key] = b

        # Date range filter
        date_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        date_frame.pack(side="right", padx=16, pady=8)

        ctk.CTkLabel(date_frame, text="From:", font=FONTS["body_sm"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=4)
        self._from_entry = ctk.CTkEntry(date_frame, width=110, font=FONTS["body_sm"],
                                        height=32,
                                        fg_color=COLORS["bg_input"],
                                        border_color=COLORS["border"],
                                        text_color=COLORS["text_primary"])
        self._from_entry.pack(side="left", padx=4)

        ctk.CTkLabel(date_frame, text="To:", font=FONTS["body_sm"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=4)
        self._to_entry = ctk.CTkEntry(date_frame, width=110, font=FONTS["body_sm"],
                                      height=32,
                                      fg_color=COLORS["bg_input"],
                                      border_color=COLORS["border"],
                                      text_color=COLORS["text_primary"])
        self._to_entry.pack(side="left", padx=4)

        ctk.CTkButton(date_frame, text="Apply", font=FONTS["body_sm"],
                      fg_color=COLORS["gold_dark"], hover_color=COLORS["gold"],
                      text_color="#000", height=32, width=70, corner_radius=6,
                      command=self._apply_date_filter
                      ).pack(side="left", padx=4)

        # Summary cards row
        self._summary_frame = ctk.CTkFrame(body, fg_color="transparent")
        self._summary_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(12,0))

        # Report content
        self._content_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_dark"],
                                           corner_radius=0)
        self._content_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=8)
        self._content_frame.grid_columnconfigure(0, weight=1)
        self._content_frame.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(2, weight=1)

        self._build_report_table()

    def _build_report_table(self):
        style = ttk.Style()
        style.configure("Report.Treeview",
                        background=COLORS["tbl_bg"],
                        foreground=COLORS["text_primary"],
                        rowheight=34, fieldbackground=COLORS["tbl_bg"],
                        borderwidth=0, font=("Segoe UI", 11))
        style.configure("Report.Treeview.Heading",
                        background=COLORS["tbl_header"], foreground=COLORS["gold"],
                        font=("Segoe UI", 11, "bold"), borderwidth=0, relief="flat")
        style.map("Report.Treeview",
                  background=[("selected", COLORS["tbl_selected"])],
                  foreground=[("selected","#fff")])

        self._tree = ttk.Treeview(self._content_frame, style="Report.Treeview",
                                  show="headings", selectmode="browse")
        sy = ttk.Scrollbar(self._content_frame, orient="vertical",
                           command=self._tree.yview)
        self._tree.configure(yscrollcommand=sy.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        self._tree.tag_configure("even", background=COLORS["tbl_bg"])
        self._tree.tag_configure("odd",  background=COLORS["tbl_alt"])

    def _set_table_columns(self, cols, widths):
        self._tree["columns"] = cols
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, minwidth=50, anchor="center")

    def _summary_card(self, parent, col, icon, label, value, color):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12,
                            border_width=1, border_color=COLORS["border"])
        card.grid(row=0, column=col, padx=(0 if col==0 else 8, 0), sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        bar = ctk.CTkFrame(card, width=5, fg_color=color, corner_radius=0)
        bar.pack(side="left", fill="y")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        ctk.CTkLabel(inner, text=f"{icon}  {label}", font=FONTS["body_sm"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        ctk.CTkLabel(inner, text=str(value), font=FONTS["h3"],
                     text_color=COLORS["text_primary"]).pack(anchor="w")

    def _rebuild_summary(self, cards):
        for w in self._summary_frame.winfo_children():
            w.destroy()
        for i, (icon, label, value, color) in enumerate(cards):
            self._summary_card(self._summary_frame, i, icon, label, value, color)

    # ─── Report generators ────────────────────────────────────────────────────

    def _get_dates(self):
        f = self._from_entry.get().strip()
        t = self._to_entry.get().strip()
        return f or "", t or ""

    def _show_report(self, key):
        self._current_report = key
        for k, b in self._report_btns.items():
            if k == key:
                b.configure(fg_color=COLORS["sidebar_active"],
                            text_color=COLORS["gold"])
            else:
                b.configure(fg_color="transparent",
                            text_color=COLORS["text_secondary"])

        today = date.today().strftime("%Y-%m-%d")

        if key == "daily":
            self._from_entry.delete(0,"end"); self._from_entry.insert(0, today)
            self._to_entry.delete(0,"end");   self._to_entry.insert(0, today)
            self._run_orders_report(today, today)

        elif key == "weekly":
            w_start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
            self._from_entry.delete(0,"end"); self._from_entry.insert(0, w_start)
            self._to_entry.delete(0,"end");   self._to_entry.insert(0, today)
            self._run_orders_report(w_start, today)

        elif key == "monthly":
            m_start = date.today().replace(day=1).strftime("%Y-%m-%d")
            self._from_entry.delete(0,"end"); self._from_entry.insert(0, m_start)
            self._to_entry.delete(0,"end");   self._to_entry.insert(0, today)
            self._run_orders_report(m_start, today)

        elif key == "dues":
            self._run_dues_report()

        elif key == "customers":
            self._run_customers_report()

    def _apply_date_filter(self):
        f, t = self._get_dates()
        if not f or not t:
            return
        if self._current_report in ("daily","weekly","monthly"):
            self._run_orders_report(f, t)

    def _run_orders_report(self, start: str, end: str):
        income   = self.db.get_income_by_period(start, end)
        expenses = self.db.get_expenses_by_period(start, end)
        orders   = self.db.get_orders_report(start, end)
        total_orders = len(orders)
        total_billed = sum(o.get("total_amount",0) or 0 for o in orders)

        self._rebuild_summary([
            ("📦","Total Orders",   total_orders,      COLORS["blue_light"]),
            ("💵","Income Received",_money(income),    COLORS["green"]),
            ("💸","Total Expenses", _money(expenses),  COLORS["orange_light"]),
            ("💰","Est. Profit",    _money(income-expenses), COLORS["gold"]),
        ])

        cols   = ("ID","Customer","Type","Date","Delivery","Total","Paid","Due","Status")
        widths = [50,160,110,100,100,90,90,90,100]
        self._set_table_columns(cols, widths)
        self._tree.delete(*self._tree.get_children())

        for i, o in enumerate(orders):
            total = o.get("total_amount",0) or 0
            paid  = o.get("paid_amount",0) or 0
            due   = total - paid
            tag   = "even" if i%2==0 else "odd"
            self._tree.insert("","end",
                values=(o["id"], o.get("customer_name",""),
                        o.get("clothing_type",""), o.get("order_date",""),
                        o.get("delivery_date",""), f"Rs.{total:,.0f}",
                        f"Rs.{paid:,.0f}", f"Rs.{due:,.0f}",
                        o.get("status","")),
                tags=(tag,)
            )

    def _run_dues_report(self):
        dues = self.db.get_dues_report()
        total_due = sum(d.get("balance",0) or 0 for d in dues)

        self._rebuild_summary([
            ("👥","Customers with Dues", len(dues),       COLORS["orange_light"]),
            ("💸","Total Outstanding",   _money(total_due), COLORS["red_light"]),
        ])

        cols   = ("Serial","Customer","Phone","Total Billed","Total Paid","Balance")
        widths = [70,200,120,120,120,120]
        self._set_table_columns(cols, widths)
        self._tree.delete(*self._tree.get_children())

        for i, d in enumerate(dues):
            tag = "even" if i%2==0 else "odd"
            self._tree.insert("","end",
                values=(d["serial_number"], d["name"], d.get("phone",""),
                        f"Rs.{d.get('total_billed',0):,.0f}",
                        f"Rs.{d.get('total_paid',0):,.0f}",
                        f"Rs.{d.get('balance',0):,.0f}"),
                tags=(tag,)
            )

    def _run_customers_report(self):
        customers = self.db.get_all_customers()
        self._rebuild_summary([
            ("👥","Total Customers", len(customers), COLORS["gold"]),
        ])
        cols   = ("Serial","Name","Phone","Address","Due Balance","Added")
        widths = [70,200,120,180,110,100]
        self._set_table_columns(cols, widths)
        self._tree.delete(*self._tree.get_children())

        for i, c in enumerate(customers):
            bal = c.get("due_balance",0) or 0
            tag = "even" if i%2==0 else "odd"
            self._tree.insert("","end",
                values=(c["serial_number"], c["name"], c.get("phone",""),
                        c.get("address",""),
                        f"Rs.{bal:,.0f}" if bal>0 else "—",
                        (c.get("created_at","") or "")[:10]),
                tags=(tag,)
            )

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, **kwargs):
        self._show_report("monthly")
