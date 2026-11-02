# =============================================================================
# screens/customer_profile.py — Full customer profile screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLORS, FONTS, ORDER_STATUS_COLORS


def _money(v):
    return f"Rs. {v:,.0f}"


class CustomerProfileScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
        self._cid = None
        self._build()

    # ─── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header bar
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"],
                            corner_radius=0, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)

        ctk.CTkButton(
            hdr, text="← Back", font=FONTS["body"],
            fg_color="transparent", hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_secondary"],
            command=lambda: self.app.show_screen("customers")
        ).pack(side="left", padx=12, pady=16)

        self._hdr_lbl = ctk.CTkLabel(
            hdr, text="Customer Profile",
            font=FONTS["h2"], text_color=COLORS["gold"]
        )
        self._hdr_lbl.pack(side="left", padx=8, pady=16)

        # Action buttons
        btns = [
            ("✏️ Edit",          self._edit_customer),
            ("📏 Measurement",   self._open_measurement),
            ("📦 New Order",     self._new_order),
            ("💰 Add Payment",   self._add_payment),
            ("📄 Download PDF",  self._download_pdf),
        ]
        for txt, cmd in reversed(btns):
            ctk.CTkButton(
                hdr, text=txt, font=FONTS["body_sm"],
                fg_color=COLORS["bg_light"], hover_color=COLORS["border"],
                text_color=COLORS["text_primary"], corner_radius=8,
                height=34, command=cmd
            ).pack(side="right", padx=6, pady=16)

        # Body
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                      corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=3)
        self._body = body

        # Left panel: customer info + measurement summary
        self._info_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_card"],
                                        corner_radius=14, border_width=1,
                                        border_color=COLORS["border"])
        self._info_frame.grid(row=0, column=0, sticky="nsew",
                              padx=(20, 8), pady=20)

        # Right panel: tabs for orders / payments / history
        self._right = ctk.CTkFrame(body, fg_color="transparent")
        self._right.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self._right.grid_columnconfigure(0, weight=1)
        self._right.grid_rowconfigure(1, weight=1)

        self._build_tabs()

    def _build_tabs(self):
        tab_bar = ctk.CTkFrame(self._right, fg_color=COLORS["bg_card"],
                               corner_radius=12, border_width=1,
                               border_color=COLORS["border"])
        tab_bar.grid(row=0, column=0, sticky="ew")

        self._tab_btns = {}
        for label in ("Orders", "Payments", "History"):
            b = ctk.CTkButton(
                tab_bar, text=label, font=FONTS["h5"],
                fg_color="transparent", hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["text_secondary"], corner_radius=10,
                height=38,
                command=lambda l=label: self._show_tab(l)
            )
            b.pack(side="left", padx=4, pady=4)
            self._tab_btns[label] = b

        self._tab_content = ctk.CTkFrame(
            self._right, fg_color=COLORS["bg_card"],
            corner_radius=12, border_width=1, border_color=COLORS["border"]
        )
        self._tab_content.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self._tab_content.grid_columnconfigure(0, weight=1)
        self._tab_content.grid_rowconfigure(0, weight=1)

        self._active_tab = None

    def _show_tab(self, label):
        self._active_tab = label
        # Highlight active tab button
        for l, b in self._tab_btns.items():
            if l == label:
                b.configure(fg_color=COLORS["sidebar_active"],
                            text_color=COLORS["gold"])
            else:
                b.configure(fg_color="transparent",
                            text_color=COLORS["text_secondary"])

        for w in self._tab_content.winfo_children():
            w.destroy()

        if label == "Orders":
            self._build_orders_tab()
        elif label == "Payments":
            self._build_payments_tab()
        elif label == "History":
            self._build_history_tab()

    # ─── Left panel: customer info ─────────────────────────────────────────────

    def _rebuild_info(self, cust, meas):
        for w in self._info_frame.winfo_children():
            w.destroy()

        # Avatar / initials
        initials = (cust["name"] or " ")[0].upper()
        avatar = ctk.CTkFrame(self._info_frame, fg_color=COLORS["gold_dark"],
                              corner_radius=40, width=72, height=72)
        avatar.pack(pady=(24, 8))
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=initials, font=("Segoe UI", 28, "bold"),
                     text_color="#000").pack(expand=True)

        ctk.CTkLabel(self._info_frame, text=cust["name"],
                     font=FONTS["h3"], text_color=COLORS["text_primary"]
                     ).pack()
        ctk.CTkLabel(self._info_frame,
                     text=f"#{cust['serial_number']}",
                     font=FONTS["h5"], text_color=COLORS["gold"]
                     ).pack(pady=(0, 8))

        # Due balance badge
        due = self.db.get_customer_due(self._cid)
        due_color = COLORS["red_light"] if due > 0 else COLORS["green"]
        due_bg    = COLORS["red_bg"]    if due > 0 else COLORS["green_bg"]
        badge = ctk.CTkFrame(self._info_frame, fg_color=due_bg, corner_radius=8)
        badge.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(badge,
                     text="⚠️  Pending Dues" if due > 0 else "✅  No Dues",
                     font=FONTS["body_sm"], text_color=due_color
                     ).pack(side="left", padx=12, pady=6)
        ctk.CTkLabel(badge, text=_money(due),
                     font=FONTS["h4"], text_color=due_color
                     ).pack(side="right", padx=12, pady=6)

        div = ctk.CTkFrame(self._info_frame, height=1,
                           fg_color=COLORS["border"], corner_radius=0)
        div.pack(fill="x", padx=16, pady=4)

        # Details rows
        rows = [
            ("📱 Phone",   cust.get("phone","") or "—"),
            ("📍 Address", cust.get("address","") or "—"),
            ("👤 Ref",     cust.get("reference_name","") or "—"),
            ("📅 Added",   (cust.get("created_at","") or "")[:10]),
            ("📝 Notes",   cust.get("notes","") or "—"),
        ]
        for icon_txt, value in rows:
            row_f = ctk.CTkFrame(self._info_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(row_f, text=icon_txt, font=FONTS["body_sm"],
                         text_color=COLORS["text_secondary"], width=90, anchor="w"
                         ).pack(side="left")
            ctk.CTkLabel(row_f, text=value, font=FONTS["body"],
                         text_color=COLORS["text_primary"], anchor="w", wraplength=180
                         ).pack(side="left", fill="x", expand=True)

        # Measurement summary
        div2 = ctk.CTkFrame(self._info_frame, height=1,
                            fg_color=COLORS["border"], corner_radius=0)
        div2.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(self._info_frame, text="📏  Measurements",
                     font=FONTS["h5"], text_color=COLORS["gold"]
                     ).pack(anchor="w", padx=16, pady=(4, 4))

        if meas:
            meas_rows = [
                ("لمبائی", meas.get("length","") or "—"),
                ("بازو",   meas.get("sleeve","") or "—"),
                ("کندھا",  meas.get("shoulder","") or "—"),
                ("چھاتی",  meas.get("chest","") or "—"),
                ("شلوار",  meas.get("trouser_length","") or "—"),
                ("پائنچہ", meas.get("trouser_bottom","") or "—"),
            ]
            for ur, val in meas_rows:
                mrow = ctk.CTkFrame(self._info_frame, fg_color="transparent")
                mrow.pack(fill="x", padx=16, pady=1)
                ctk.CTkLabel(mrow, text=ur, font=FONTS["urdu_sm"],
                             text_color=COLORS["text_secondary"], width=80, anchor="e"
                             ).pack(side="right", padx=(4, 12))
                ctk.CTkLabel(mrow, text=val, font=FONTS["body"],
                             text_color=COLORS["text_primary"]
                             ).pack(side="left")
            ctk.CTkButton(
                self._info_frame, text="📏  Edit / View Full Measurement",
                font=FONTS["body_sm"],
                fg_color=COLORS["gold_dark"], hover_color=COLORS["gold"],
                text_color="#000", height=34, corner_radius=8,
                command=self._open_measurement
            ).pack(fill="x", padx=16, pady=(8, 4))
        else:
            ctk.CTkLabel(self._info_frame, text="No measurement on record.",
                         font=FONTS["body_sm"], text_color=COLORS["text_muted"]
                         ).pack(pady=4)
            ctk.CTkButton(
                self._info_frame, text="➕  Add Measurement",
                font=FONTS["body_sm"],
                fg_color=COLORS["gold"], hover_color=COLORS["gold_dark"],
                text_color="#000", height=34, corner_radius=8,
                command=self._open_measurement
            ).pack(fill="x", padx=16, pady=(4, 20))

    # ─── Orders tab ───────────────────────────────────────────────────────────

    def _build_orders_tab(self):
        frame = ctk.CTkScrollableFrame(self._tab_content,
                                       fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        frame.grid_columnconfigure(0, weight=1)

        orders = self.db.get_customer_orders(self._cid)
        if not orders:
            ctk.CTkLabel(frame, text="No orders yet.",
                         font=FONTS["body"], text_color=COLORS["text_muted"]
                         ).pack(pady=30)
            return

        for o in orders:
            self._order_card(frame, o)

    def _order_card(self, parent, o):
        status_color = ORDER_STATUS_COLORS.get(o["status"], COLORS["gray"])
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_light"],
                            corner_radius=10, border_width=1,
                            border_color=COLORS["border"])
        card.pack(fill="x", pady=4)
        card.grid_columnconfigure(1, weight=1)

        # Status bar
        bar = ctk.CTkFrame(card, width=6, fg_color=status_color, corner_radius=0)
        bar.pack(side="left", fill="y")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x")
        ctk.CTkLabel(row1, text=o.get("clothing_type","Order"),
                     font=FONTS["h5"], text_color=COLORS["text_primary"]
                     ).pack(side="left")
        ctk.CTkLabel(row1, text=o["status"],
                     font=FONTS["body_sm"], text_color=status_color
                     ).pack(side="left", padx=8)
        ctk.CTkLabel(row1, text=f"Order #{o['id']}",
                     font=FONTS["caption"], text_color=COLORS["text_muted"]
                     ).pack(side="right")

        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=(4,0))
        ctk.CTkLabel(row2,
                     text=f"📅 {o.get('order_date','')}  →  🚚 {o.get('delivery_date','')}",
                     font=FONTS["body_sm"], text_color=COLORS["text_secondary"]
                     ).pack(side="left")

        row3 = ctk.CTkFrame(inner, fg_color="transparent")
        row3.pack(fill="x", pady=(4,0))
        total = o.get("total_amount",0) or 0
        paid  = o.get("paid_amount",0) or 0
        due   = o.get("order_due",0) or 0
        ctk.CTkLabel(row3,
                     text=f"Total: {_money(total)}  |  Paid: {_money(paid)}  |  Due: {_money(due)}",
                     font=FONTS["body_sm"],
                     text_color=COLORS["red_light"] if due > 0 else COLORS["green"]
                     ).pack(side="left")

        # Status change buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)

        status_flow = ["Pending", "Cutting", "Stitching", "Ready", "Delivered"]
        cur_idx = status_flow.index(o["status"]) if o["status"] in status_flow else -1
        if 0 <= cur_idx < len(status_flow) - 1:
            next_s = status_flow[cur_idx + 1]
            ctk.CTkButton(
                btn_frame, text=f"→ {next_s}", font=FONTS["caption"],
                fg_color=status_color, hover_color=COLORS["border"],
                text_color="#000" if next_s=="Ready" else "#fff",
                height=30, width=90, corner_radius=6,
                command=lambda oid=o["id"], s=next_s: self._advance_status(oid, s)
            ).pack(pady=4)

    # ─── Payments tab ─────────────────────────────────────────────────────────

    def _build_payments_tab(self):
        frame = ctk.CTkScrollableFrame(self._tab_content,
                                       fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        frame.grid_columnconfigure(0, weight=1)

        payments = self.db.get_customer_payments(self._cid)
        if not payments:
            ctk.CTkLabel(frame, text="No payments recorded.",
                         font=FONTS["body"], text_color=COLORS["text_muted"]
                         ).pack(pady=30)
            return

        total = sum(p["amount"] for p in payments)
        ctk.CTkLabel(frame,
                     text=f"Total Paid: {_money(total)}",
                     font=FONTS["h4"], text_color=COLORS["green"]
                     ).pack(anchor="w", padx=8, pady=(4, 8))

        for p in payments:
            row = ctk.CTkFrame(frame, fg_color=COLORS["bg_light"], corner_radius=8)
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(row, text="💚", font=("Segoe UI",14)
                         ).pack(side="left", padx=(10,4), pady=8)
            ctk.CTkLabel(row, text=p.get("payment_date",""),
                         font=FONTS["body_sm"], text_color=COLORS["text_secondary"]
                         ).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=p.get("notes","") or "",
                         font=FONTS["body_sm"], text_color=COLORS["text_muted"]
                         ).pack(side="left", padx=4, fill="x", expand=True)
            ctk.CTkLabel(row, text=_money(p["amount"]),
                         font=FONTS["h5"], text_color=COLORS["green"]
                         ).pack(side="right", padx=14, pady=8)

    # ─── History tab ──────────────────────────────────────────────────────────

    def _build_history_tab(self):
        frame = ctk.CTkScrollableFrame(self._tab_content,
                                       fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        frame.grid_columnconfigure(0, weight=1)

        history = self.db.get_measurement_history(self._cid)
        if not history:
            ctk.CTkLabel(frame, text="No measurement history.",
                         font=FONTS["body"], text_color=COLORS["text_muted"]
                         ).pack(pady=30)
            return

        for h in history:
            card = ctk.CTkFrame(frame, fg_color=COLORS["bg_light"],
                                corner_radius=10, border_width=1,
                                border_color=COLORS["border"])
            card.pack(fill="x", pady=4)

            hdr = ctk.CTkFrame(card, fg_color=COLORS["bg_medium"], corner_radius=0)
            hdr.pack(fill="x")
            ctk.CTkLabel(hdr,
                         text=f"📅  Changed: {h.get('changed_at','')[:16]}",
                         font=FONTS["body_sm"], text_color=COLORS["gold"]
                         ).pack(side="left", padx=12, pady=6)
            ctk.CTkLabel(hdr, text=h.get("change_note",""),
                         font=FONTS["body_sm"], text_color=COLORS["text_muted"]
                         ).pack(side="right", padx=12)

            snap = h.get("snapshot", {})
            snap_frame = ctk.CTkFrame(card, fg_color="transparent")
            snap_frame.pack(fill="x", padx=12, pady=6)

            fields = [
                ("لمبائی","length"),("بازو","sleeve"),("کندھا","shoulder"),
                ("چھاتی","chest"),("شلوار","trouser_length"),
            ]
            for col_i, (ur, key) in enumerate(fields):
                f = ctk.CTkFrame(snap_frame, fg_color="transparent")
                f.grid(row=0, column=col_i, padx=8)
                ctk.CTkLabel(f, text=ur, font=FONTS["urdu_sm"],
                             text_color=COLORS["text_secondary"]).pack()
                ctk.CTkLabel(f, text=snap.get(key,"—") or "—",
                             font=FONTS["body"], text_color=COLORS["text_primary"]
                             ).pack()

    # ─── Actions ──────────────────────────────────────────────────────────────

    def _edit_customer(self):
        self.app.show_screen("add_customer", edit_customer_id=self._cid)

    def _open_measurement(self):
        self.app.show_screen("measurement_form", customer_id=self._cid)

    def _new_order(self):
        self.app.show_screen("orders", new_order_for=self._cid)

    def _add_payment(self):
        self.app.show_screen("payments", customer_id=self._cid)

    def _download_pdf(self):
        from pdf.pdf_generator import generate_measurement_pdf
        cust = self.db.get_customer(self._cid)
        meas = self.db.get_measurement(self._cid)
        if not meas:
            messagebox.showwarning("No Measurement",
                                   "Please add a measurement before downloading PDF.")
            return
        import os
        from pathlib import Path
        downloads = Path.home() / "Downloads"
        out = downloads / f"measurement_{cust['serial_number']}_{cust['name'].replace(' ','_')}.pdf"
        generate_measurement_pdf(cust, meas, str(out))
        messagebox.showinfo("PDF Saved", f"PDF saved to:\n{out}")
        os.startfile(str(out))

    def _advance_status(self, order_id, new_status):
        self.db.update_order_status(order_id, new_status)
        self._show_tab("Orders")

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, customer_id=None, open_measurement=False, **kwargs):
        if customer_id:
            self._cid = customer_id
        if not self._cid:
            return

        cust = self.db.get_customer(self._cid)
        meas = self.db.get_measurement(self._cid)

        self._hdr_lbl.configure(
            text=f"👤  {cust['name']}  —  #{cust['serial_number']}"
        )
        self._rebuild_info(cust, meas)
        self._show_tab("Orders")

        if open_measurement:
            self.after(100, self._open_measurement)
