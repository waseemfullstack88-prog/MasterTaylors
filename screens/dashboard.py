# =============================================================================
# screens/dashboard.py — Dashboard screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from utils.constants import COLORS, FONTS, ORDER_STATUS_COLORS


def _money(v):
    return f"Rs. {v:,.0f}"


class DashboardScreen(ctk.CTkFrame):

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
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        ctk.CTkLabel(
            hdr, text="📊  Dashboard",
            font=FONTS["h2"], text_color=COLORS["gold"]
        ).pack(side="left", padx=28, pady=16)
        self._date_lbl = ctk.CTkLabel(
            hdr, text="", font=FONTS["body"], text_color=COLORS["text_secondary"]
        )
        self._date_lbl.pack(side="right", padx=28)

        # Scrollable body
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        body.grid_columnconfigure(0, weight=1)
        self._body = body

        # Quick‑action buttons
        self._build_actions(body)

        # Stat cards grid (row 0 inside body)
        self._stats_frame = ctk.CTkFrame(body, fg_color="transparent")
        self._stats_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))

        # Two-column bottom section
        bottom = ctk.CTkFrame(body, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        self._recent_frame   = self._build_panel(bottom, "👥  Recent Customers", 0)
        self._upcoming_frame = self._build_panel(bottom, "📅  Upcoming Deliveries", 1)

    def _build_actions(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        btns = [
            ("➕  New Customer", "add_customer", COLORS["gold"]),
            ("🔍  Search Customer", "customers",   COLORS["blue_light"]),
            ("📦  New Order",      "orders",       COLORS["green"]),
            ("💰  Add Payment",    "payments",     COLORS["teal_light"]),
        ]
        for i, (txt, screen, color) in enumerate(btns):
            b = ctk.CTkButton(
                frame, text=txt, font=FONTS["h5"],
                fg_color=color, hover_color=COLORS["border_light"],
                text_color="#ffffff", corner_radius=10, height=40,
                command=lambda s=screen: self.app.show_screen(s)
            )
            b.grid(row=0, column=i, padx=(0 if i==0 else 8, 0), sticky="w")

    def _build_panel(self, parent, title, col):
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                              corner_radius=12, border_width=1,
                              border_color=COLORS["border"])
        frame.grid(row=0, column=col, sticky="nsew",
                   padx=(0 if col==0 else 8, 0), pady=0)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=title, font=FONTS["h4"],
                     text_color=COLORS["gold"]).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        div = ctk.CTkFrame(frame, height=1, fg_color=COLORS["border"], corner_radius=0)
        div.grid(row=1, column=0, sticky="ew", padx=16)

        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        content.grid_columnconfigure(0, weight=1)
        frame._content = content
        return frame

    # ─── Stat cards ───────────────────────────────────────────────────────────

    def _stat_card(self, parent, row, col, icon, title, value, color):
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        card.grid(row=row, column=col, padx=(0 if col==0 else 8, 0),
                  pady=(0 if row==0 else 8, 0), sticky="nsew")

        # Left color bar
        bar = ctk.CTkFrame(card, width=5, fg_color=color, corner_radius=0)
        bar.pack(side="left", fill="y", padx=(0,12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, pady=14, padx=(0,14))

        ctk.CTkLabel(inner, text=f"{icon}  {title}",
                     font=FONTS["body_sm"], text_color=COLORS["text_secondary"]
                     ).pack(anchor="w")
        lbl = ctk.CTkLabel(inner, text=str(value),
                           font=FONTS["h2"], text_color=COLORS["text_primary"])
        lbl.pack(anchor="w")
        return lbl

    def _rebuild_stats(self, stats):
        # Clear old cards
        for w in self._stats_frame.winfo_children():
            w.destroy()

        for i in range(4):
            self._stats_frame.grid_columnconfigure(i, weight=1)

        cards = [
            ("👥", "Total Customers",  stats["total_customers"],    COLORS["gold"]),
            ("📦", "Today's Orders",   stats["today_orders"],       COLORS["blue_light"]),
            ("⏳", "Pending Orders",   stats["pending_orders"],     COLORS["orange_light"]),
            ("✅", "Ready / Delivered",
             f"{stats['ready_orders']} / {stats['delivered_orders']}", COLORS["green"]),
            ("💸", "Total Dues",       _money(stats["total_dues"]),  COLORS["red_light"]),
            ("📈", "Weekly Income",    _money(stats["weekly_income"]),COLORS["teal_light"]),
            ("💵", "Monthly Income",   _money(stats["monthly_income"]),COLORS["blue_light"]),
            ("💰", "Monthly Profit",   _money(stats["monthly_profit"]),COLORS["gold"]),
        ]
        for idx, (icon, title, value, color) in enumerate(cards):
            r, c = divmod(idx, 4)
            self._stat_card(self._stats_frame, r, c, icon, title, value, color)

    # ─── Recent customers ─────────────────────────────────────────────────────

    def _rebuild_recent(self, customers):
        content = self._recent_frame._content
        for w in content.winfo_children():
            w.destroy()

        if not customers:
            ctk.CTkLabel(content, text="No customers yet.",
                         text_color=COLORS["text_muted"], font=FONTS["body_sm"]
                         ).pack(pady=20)
            return

        for c in customers:
            row = ctk.CTkFrame(content, fg_color=COLORS["bg_light"],
                               corner_radius=8)
            row.pack(fill="x", padx=4, pady=3)

            ctk.CTkLabel(row, text=f"#{c['serial_number']}",
                         font=FONTS["h5"], text_color=COLORS["gold"],
                         width=60).pack(side="left", padx=(10,4), pady=8)
            ctk.CTkLabel(row, text=c["name"],
                         font=FONTS["body"], text_color=COLORS["text_primary"]
                         ).pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkLabel(row, text=c.get("phone",""),
                         font=FONTS["body_sm"], text_color=COLORS["text_secondary"]
                         ).pack(side="right", padx=10, pady=8)

            row.bind("<Button-1>", lambda e, cid=c["id"]:
                     self.app.show_screen("customer_profile", customer_id=cid))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, cid=c["id"]:
                           self.app.show_screen("customer_profile", customer_id=cid))

    # ─── Upcoming deliveries ──────────────────────────────────────────────────

    def _rebuild_upcoming(self, orders):
        content = self._upcoming_frame._content
        for w in content.winfo_children():
            w.destroy()

        if not orders:
            ctk.CTkLabel(content, text="No upcoming deliveries.",
                         text_color=COLORS["text_muted"], font=FONTS["body_sm"]
                         ).pack(pady=20)
            return

        for o in orders:
            row = ctk.CTkFrame(content, fg_color=COLORS["bg_light"], corner_radius=8)
            row.pack(fill="x", padx=4, pady=3)

            status_color = ORDER_STATUS_COLORS.get(o["status"], COLORS["gray"])
            ctk.CTkLabel(row, text="●", font=("Segoe UI", 14),
                         text_color=status_color, width=20
                         ).pack(side="left", padx=(10,4), pady=8)
            ctk.CTkLabel(row, text=o.get("customer_name",""),
                         font=FONTS["body"], text_color=COLORS["text_primary"]
                         ).pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkLabel(row, text=o.get("delivery_date",""),
                         font=FONTS["body_sm"], text_color=COLORS["gold"]
                         ).pack(side="right", padx=10, pady=8)

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, **kwargs):
        from datetime import datetime
        self._date_lbl.configure(
            text=datetime.now().strftime("%A, %d %B %Y")
        )
        stats = self.db.get_dashboard_stats()
        self._rebuild_stats(stats)
        self._rebuild_recent(stats["recent_customers"])
        self._rebuild_upcoming(stats["upcoming"])
