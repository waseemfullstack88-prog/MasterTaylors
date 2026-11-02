# =============================================================================
# screens/customers.py — Customer search screen
# =============================================================================
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from utils.constants import COLORS, FONTS


class CustomersScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.app = app
        self.db  = app.db
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="👥  Customers / گاہک",
                     font=FONTS["h2"], text_color=COLORS["gold"]
                     ).pack(side="left", padx=28, pady=16)
        ctk.CTkButton(
            hdr, text="➕  Add Customer", font=FONTS["h5"],
            fg_color=COLORS["gold"], hover_color=COLORS["gold_dark"],
            text_color="#000000", corner_radius=8, height=36,
            command=lambda: self.app.show_screen("add_customer")
        ).pack(side="right", padx=20, pady=14)

        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"],
                                    corner_radius=0)
        search_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI",18),
                     text_color=COLORS["text_secondary"]
                     ).pack(side="left", padx=(24, 6), pady=14)

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._do_search())
        entry = ctk.CTkEntry(
            search_frame, textvariable=self._search_var,
            placeholder_text="Search by serial number, name, or phone...",
            font=FONTS["body"], height=40, width=500,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        entry.pack(side="left", padx=4, pady=14)
        entry.focus()

        self._results_lbl = ctk.CTkLabel(
            search_frame, text="", font=FONTS["body_sm"],
            text_color=COLORS["text_secondary"]
        )
        self._results_lbl.pack(side="left", padx=16)

        # Table frame
        tbl_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        tbl_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=16)
        tbl_frame.grid_columnconfigure(0, weight=1)
        tbl_frame.grid_rowconfigure(0, weight=1)
        self._build_table(tbl_frame)

    def _build_table(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                        background=COLORS["tbl_bg"],
                        foreground=COLORS["text_primary"],
                        rowheight=36,
                        fieldbackground=COLORS["tbl_bg"],
                        borderwidth=0,
                        font=("Segoe UI", 11))
        style.configure("Custom.Treeview.Heading",
                        background=COLORS["tbl_header"],
                        foreground=COLORS["gold"],
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0, relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", COLORS["tbl_selected"])],
                  foreground=[("selected", "#ffffff")])

        cols = ("#", "Serial", "Name", "Phone", "Balance", "Last Order")
        self._tree = ttk.Treeview(
            parent, style="Custom.Treeview", columns=cols,
            show="headings", selectmode="browse"
        )
        col_widths = [40, 90, 250, 140, 130, 130]
        for col, w in zip(cols, col_widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, minwidth=w,
                              anchor="center" if col in ("#","Serial","Balance") else "w")

        scroll_y = ttk.Scrollbar(parent, orient="vertical",
                                 command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll_y.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")

        # Alternating row colours
        self._tree.tag_configure("even", background=COLORS["tbl_bg"])
        self._tree.tag_configure("odd",  background=COLORS["tbl_alt"])
        self._tree.tag_configure("due",  foreground=COLORS["orange_light"])

        self._tree.bind("<Double-1>", self._on_row_double)
        self._tree.bind("<Return>",   self._on_row_double)

    def _do_search(self):
        q = self._search_var.get().strip()
        if q:
            rows = self.db.search_customers(q)
        else:
            rows = self.db.get_all_customers()

        self._tree.delete(*self._tree.get_children())
        self._results_lbl.configure(text=f"{len(rows)} records found")

        for i, r in enumerate(rows):
            bal = r.get("due_balance", 0) or 0
            bal_txt = f"Rs. {bal:,.0f}" if bal > 0 else "—"
            tag = "due" if bal > 0 else ("even" if i%2==0 else "odd")
            self._tree.insert(
                "", "end",
                values=(i+1, r["serial_number"], r["name"],
                        r.get("phone",""), bal_txt,
                        r.get("last_order_date","") or "—"),
                tags=(tag,),
                iid=str(r["id"])
            )

    def _on_row_double(self, event):
        sel = self._tree.selection()
        if sel:
            cid = int(sel[0])
            self.app.show_screen("customer_profile", customer_id=cid)

    def on_show(self, **kwargs):
        self._do_search()
