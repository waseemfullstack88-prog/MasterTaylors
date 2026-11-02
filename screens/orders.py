# =============================================================================
# screens/orders.py — Orders management screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import (
    COLORS, FONTS, ORDER_STATUSES_EN, ORDER_STATUS_COLORS,
    CLOTHING_TYPES
)
from datetime import date


class OrdersScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
        self._new_order_cid = None
        self._edit_order_id = None
        self._form_visible  = False
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
        ctk.CTkLabel(hdr, text="📦  Orders / آرڈرز",
                     font=FONTS["h2"], text_color=COLORS["gold"]
                     ).pack(side="left", padx=28, pady=16)
        ctk.CTkButton(
            hdr, text="➕  New Order", font=FONTS["h5"],
            fg_color=COLORS["gold"], hover_color=COLORS["gold_dark"],
            text_color="#000", corner_radius=8, height=36,
            command=lambda: self.show_form()
        ).pack(side="right", padx=20, pady=14)

        # Body (two-pane: list + form)
        body = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Splitter frames
        self._list_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_dark"],
                                        corner_radius=0)
        self._list_frame.grid(row=0, column=0, sticky="nsew")
        self._list_frame.grid_columnconfigure(0, weight=1)
        self._list_frame.grid_rowconfigure(1, weight=1)

        # Status filter bar
        filter_bar = ctk.CTkFrame(self._list_frame,
                                  fg_color=COLORS["bg_medium"], corner_radius=0)
        filter_bar.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(filter_bar, text="Filter:",
                     font=FONTS["body_sm"], text_color=COLORS["text_secondary"]
                     ).pack(side="left", padx=16, pady=10)

        self._status_filter = tk.StringVar(value="All")
        statuses = ["All"] + ORDER_STATUSES_EN
        for s in statuses:
            color = ORDER_STATUS_COLORS.get(s, COLORS["text_secondary"])
            ctk.CTkButton(
                filter_bar, text=s, font=FONTS["body_sm"],
                fg_color="transparent", hover_color=COLORS["sidebar_hover"],
                text_color=color, corner_radius=6, height=30,
                command=lambda v=s: self._filter(v)
            ).pack(side="left", padx=3, pady=8)

        # Orders table
        tbl_frame = ctk.CTkFrame(self._list_frame, fg_color=COLORS["bg_dark"],
                                 corner_radius=0)
        tbl_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)
        tbl_frame.grid_columnconfigure(0, weight=1)
        tbl_frame.grid_rowconfigure(0, weight=1)
        self._build_table(tbl_frame)

        # Form panel (hidden by default)
        self._form_frame = ctk.CTkScrollableFrame(
            body, fg_color=COLORS["bg_card"], corner_radius=0,
            border_width=1, border_color=COLORS["border"], width=420
        )
        self._build_order_form()

    def _build_table(self, parent):
        style = ttk.Style()
        style.configure("Orders.Treeview",
                        background=COLORS["tbl_bg"],
                        foreground=COLORS["text_primary"],
                        rowheight=36, fieldbackground=COLORS["tbl_bg"],
                        borderwidth=0, font=("Segoe UI", 11))
        style.configure("Orders.Treeview.Heading",
                        background=COLORS["tbl_header"], foreground=COLORS["gold"],
                        font=("Segoe UI", 11, "bold"), borderwidth=0, relief="flat")
        style.map("Orders.Treeview",
                  background=[("selected", COLORS["tbl_selected"])],
                  foreground=[("selected", "#fff")])

        cols = ("ID","Customer","Type","Qty","Total","Paid","Due","Status","Delivery")
        self._tree = ttk.Treeview(parent, style="Orders.Treeview",
                                  columns=cols, show="headings", selectmode="browse")
        widths = [50, 180, 120, 50, 90, 90, 90, 100, 100]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, minwidth=w, anchor="center")

        sy = ttk.Scrollbar(parent, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sy.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")

        for s in ORDER_STATUSES_EN:
            self._tree.tag_configure(s, foreground=ORDER_STATUS_COLORS.get(s, COLORS["text_primary"]))

        self._tree.bind("<Double-1>", self._on_row_double)

    def _build_order_form(self):
        form = self._form_frame
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Order Details",
                     font=FONTS["h3"], text_color=COLORS["gold"]
                     ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 4))

        self._cust_search_var = tk.StringVar()
        self._cust_search_var.trace_add("write", self._search_cust)
        ctk.CTkLabel(form, text="Customer *", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=1, column=0, sticky="w", padx=20, pady=(12, 2))

        self._cust_entry = ctk.CTkEntry(form, textvariable=self._cust_search_var,
                                        placeholder_text="Type name or serial...",
                                        font=FONTS["body"], height=38,
                                        fg_color=COLORS["bg_input"],
                                        border_color=COLORS["border"],
                                        text_color=COLORS["text_primary"])
        self._cust_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,4))

        self._cust_list_frame = ctk.CTkFrame(form, fg_color=COLORS["bg_light"],
                                             corner_radius=8)
        self._cust_list_frame.grid(row=3, column=0, sticky="ew", padx=20)
        self._cust_list_frame.grid_columnconfigure(0, weight=1)
        self._selected_cid = None
        self._selected_cname_lbl = ctk.CTkLabel(
            form, text="", font=FONTS["body_sm"], text_color=COLORS["green"]
        )
        self._selected_cname_lbl.grid(row=4, column=0, sticky="w", padx=20)

        fields_data = [
            ("Clothing Type  (قسم)", "clothing_type", None, 5),
            ("Order Date", "order_date", date.today().strftime("%Y-%m-%d"), 7),
            ("Delivery Date", "delivery_date", "", 9),
            ("Quantity", "quantity", "1", 11),
            ("Total Amount  (Rs)", "total_amount", "0", 13),
            ("Advance Paid  (Rs)", "advance_amount", "0", 15),
            ("Expense / Cost  (Rs)", "expense_amount", "0", 17),
        ]
        self._form_entries = {}
        for label, key, default, row in fields_data:
            ctk.CTkLabel(form, text=label, font=FONTS["h5"],
                         text_color=COLORS["text_secondary"]
                         ).grid(row=row, column=0, sticky="w", padx=20, pady=(10,2))
            if key == "clothing_type":
                var = tk.StringVar(value=CLOTHING_TYPES[0])
                mb = ctk.CTkOptionMenu(form, variable=var, values=CLOTHING_TYPES,
                                       font=FONTS["body"], height=38,
                                       fg_color=COLORS["bg_input"],
                                       button_color=COLORS["gold_dark"],
                                       button_hover_color=COLORS["gold"],
                                       text_color=COLORS["text_primary"])
                mb.grid(row=row+1, column=0, sticky="ew", padx=20, pady=(0,4))
                self._form_entries[key] = var
            else:
                e = ctk.CTkEntry(form, placeholder_text=label,
                                 font=FONTS["body"], height=38,
                                 fg_color=COLORS["bg_input"],
                                 border_color=COLORS["border"],
                                 text_color=COLORS["text_primary"])
                if default:
                    e.insert(0, default)
                e.grid(row=row+1, column=0, sticky="ew", padx=20, pady=(0,4))
                self._form_entries[key] = e

        # Status
        ctk.CTkLabel(form, text="Status", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=19, column=0, sticky="w", padx=20, pady=(10,2))
        self._status_var = tk.StringVar(value="Pending")
        ctk.CTkOptionMenu(form, variable=self._status_var,
                          values=ORDER_STATUSES_EN,
                          font=FONTS["body"], height=38,
                          fg_color=COLORS["bg_input"],
                          button_color=COLORS["gold_dark"],
                          button_hover_color=COLORS["gold"],
                          text_color=COLORS["text_primary"]
                          ).grid(row=20, column=0, sticky="ew", padx=20, pady=(0,4))

        # Design notes
        ctk.CTkLabel(form, text="Design Notes  (ڈیزائن نوٹ)", font=FONTS["h5"],
                     text_color=COLORS["text_secondary"]
                     ).grid(row=21, column=0, sticky="w", padx=20, pady=(10,2))
        self._order_notes = ctk.CTkTextbox(form, height=70, font=FONTS["body"],
                                           fg_color=COLORS["bg_input"],
                                           border_color=COLORS["border"],
                                           text_color=COLORS["text_primary"])
        self._order_notes.grid(row=22, column=0, sticky="ew", padx=20, pady=(0,4))

        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=23, column=0, sticky="ew", padx=20, pady=16)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="💾 Save", font=FONTS["h5"],
                      fg_color=COLORS["gold"], hover_color=COLORS["gold_dark"],
                      text_color="#000", corner_radius=8, height=42,
                      command=self._save_order
                      ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(btn_frame, text="✕ Cancel", font=FONTS["h5"],
                      fg_color=COLORS["bg_light"], hover_color=COLORS["border"],
                      text_color=COLORS["text_secondary"], corner_radius=8, height=42,
                      command=self.hide_form
                      ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    # ─── Logic ────────────────────────────────────────────────────────────────

    def _search_cust(self, *_):
        q = self._cust_search_var.get().strip()
        for w in self._cust_list_frame.winfo_children():
            w.destroy()
        if not q:
            return
        results = self.db.search_customers(q)[:5]
        for c in results:
            btn = ctk.CTkButton(
                self._cust_list_frame,
                text=f"#{c['serial_number']}  {c['name']}  {c.get('phone','')}",
                font=FONTS["body_sm"],
                fg_color="transparent", hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["text_primary"], corner_radius=0, anchor="w",
                command=lambda cid=c["id"], name=c["name"], sn=c["serial_number"]:
                    self._select_customer(cid, name, sn)
            )
            btn.pack(fill="x", padx=4, pady=1)

    def _select_customer(self, cid, name, serial):
        self._selected_cid = cid
        self._selected_cname_lbl.configure(text=f"✅  Selected: {name}  #{serial}")
        self._cust_search_var.set("")
        for w in self._cust_list_frame.winfo_children():
            w.destroy()

    def _get_form_data(self):
        data = {}
        for key, widget in self._form_entries.items():
            if isinstance(widget, tk.StringVar):
                data[key] = widget.get()
            else:
                data[key] = widget.get().strip()
        data["design_notes"] = self._order_notes.get("1.0", "end-1c").strip()
        data["status"]       = self._status_var.get()
        return data

    def _save_order(self):
        if not self._selected_cid:
            messagebox.showwarning("Missing", "Please select a customer.")
            return
        data = self._get_form_data()
        data["customer_id"] = self._selected_cid
        try:
            data["total_amount"]    = float(data.get("total_amount",0) or 0)
            data["advance_amount"]  = float(data.get("advance_amount",0) or 0)
            data["expense_amount"]  = float(data.get("expense_amount",0) or 0)
            data["quantity"]        = int(data.get("quantity",1) or 1)
        except ValueError:
            messagebox.showerror("Invalid", "Amount/Quantity must be numbers.")
            return

        if self._edit_order_id:
            self.db.update_order(self._edit_order_id, data)
            messagebox.showinfo("Saved", "Order updated successfully.")
        else:
            self.db.add_order(data)
            messagebox.showinfo("Saved", "Order saved successfully.")

        self.hide_form()
        self._load_orders("All")

    def _filter(self, status):
        self._load_orders(None if status == "All" else status)

    def _load_orders(self, status=None):
        self._tree.delete(*self._tree.get_children())
        orders = self.db.get_all_orders(status=status)
        for o in orders:
            total = o.get("total_amount",0) or 0
            paid  = o.get("paid_amount",0) or 0
            due   = o.get("order_due",0) or 0
            self._tree.insert("", "end",
                values=(
                    o["id"],
                    o.get("customer_name",""),
                    o.get("clothing_type",""),
                    o.get("quantity",1),
                    f"Rs.{total:,.0f}",
                    f"Rs.{paid:,.0f}",
                    f"Rs.{due:,.0f}",
                    o.get("status",""),
                    o.get("delivery_date","")
                ),
                tags=(o.get("status",""),),
                iid=str(o["id"])
            )

    def _on_row_double(self, event):
        sel = self._tree.selection()
        if sel:
            oid  = int(sel[0])
            order = self.db.get_order(oid)
            self.show_form(order=order)

    def show_form(self, order=None, customer_id=None):
        if not self._form_visible:
            self._list_frame.grid_configure(padx=(0,0))
            self._form_frame.grid(row=0, column=1, sticky="nsew",
                                  in_=self._list_frame.master)
            self._form_visible = True

        # Reset
        self._selected_cid = None
        self._selected_cname_lbl.configure(text="")
        self._cust_search_var.set("")
        self._order_notes.delete("1.0","end")
        for key, w in self._form_entries.items():
            if isinstance(w, ctk.CTkEntry):
                w.delete(0,"end")
        self._status_var.set("Pending")

        if customer_id:
            cust = self.db.get_customer(customer_id)
            if cust:
                self._select_customer(customer_id, cust["name"], cust["serial_number"])

        if order:
            self._edit_order_id = order["id"]
            self._select_customer(order["customer_id"],
                                  order.get("customer_name",""),
                                  order.get("serial_number",""))
            for key, w in self._form_entries.items():
                val = order.get(key,"") or ""
                if isinstance(w, ctk.CTkEntry):
                    w.delete(0,"end")
                    w.insert(0, str(val))
                elif isinstance(w, tk.StringVar):
                    w.set(str(val))
            self._status_var.set(order.get("status","Pending"))
            self._order_notes.delete("1.0","end")
            self._order_notes.insert("1.0", order.get("design_notes","") or "")
        else:
            self._edit_order_id = None
            from datetime import date
            for key, w in self._form_entries.items():
                if isinstance(w, ctk.CTkEntry):
                    if key == "order_date":
                        w.insert(0, date.today().strftime("%Y-%m-%d"))
                    elif key == "quantity":
                        w.insert(0, "1")
                    elif key in ("total_amount","advance_amount","expense_amount"):
                        w.insert(0, "0")

    def hide_form(self):
        if self._form_visible:
            self._form_frame.grid_remove()
            self._form_visible = False

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def on_show(self, new_order_for=None, **kwargs):
        self.hide_form()
        self._load_orders("All")
        if new_order_for:
            self._new_order_cid = new_order_for
            self.show_form(customer_id=new_order_for)
