# =============================================================================
# components/sidebar.py — Navigation sidebar for Master Taylor's
# =============================================================================
import customtkinter as ctk
from utils.constants import COLORS, FONTS, NAV_ITEMS, SHOP_NAME, SHOP_SUBTITLE


class Sidebar(ctk.CTkFrame):
    """Left sidebar navigation panel."""

    WIDTH = 220

    def __init__(self, parent, navigate_callback):
        super().__init__(
            parent,
            width=self.WIDTH,
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
        )
        self.navigate = navigate_callback
        self.nav_buttons = {}
        self.active_screen = None

        self.pack_propagate(False)
        self._build()

    def _build(self):
        # ── Logo / Shop header ──────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"], corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)

        # Gold accent top bar
        accent_bar = ctk.CTkFrame(header, height=4, fg_color=COLORS["gold"], corner_radius=0)
        accent_bar.pack(fill="x")

        # Shop icon / scissors symbol
        icon_lbl = ctk.CTkLabel(
            header, text="✂", font=("Segoe UI", 36), text_color=COLORS["gold"]
        )
        icon_lbl.pack(pady=(18, 2))

        name_lbl = ctk.CTkLabel(
            header, text=SHOP_NAME,
            font=FONTS["shop_name"], text_color=COLORS["gold"]
        )
        name_lbl.pack()

        sub_lbl = ctk.CTkLabel(
            header, text=SHOP_SUBTITLE,
            font=FONTS["shop_sub"], text_color=COLORS["text_secondary"]
        )
        sub_lbl.pack(pady=(0, 6))

        # Divider
        div = ctk.CTkFrame(header, height=1, fg_color=COLORS["border"], corner_radius=0)
        div.pack(fill="x", padx=16, pady=(0, 16))

        # ── Navigation buttons ───────────────────────────────────────────────
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=8, pady=4)

        for screen_key, icon, label_en, label_ur in NAV_ITEMS:
            btn = self._make_nav_btn(nav_frame, screen_key, icon, label_en, label_ur)
            btn.pack(fill="x", pady=2)
            self.nav_buttons[screen_key] = btn

        # ── Bottom section ──────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=8, pady=12)

        ver_lbl = ctk.CTkLabel(
            bottom, text="v1.0.0 · Offline",
            font=FONTS["caption"], text_color=COLORS["text_muted"]
        )
        ver_lbl.pack()

    def _make_nav_btn(self, parent, key, icon, label_en, label_ur):
        """Create a navigation button."""
        frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=10)

        inner = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=10)
        inner.pack(fill="x", padx=2, pady=1)

        icon_lbl = ctk.CTkLabel(
            inner, text=icon, font=("Segoe UI", 18), width=36,
            text_color=COLORS["text_secondary"]
        )
        icon_lbl.pack(side="left", padx=(10, 4), pady=10)

        text_lbl = ctk.CTkLabel(
            inner, text=label_en,
            font=FONTS["h5"], text_color=COLORS["text_secondary"],
            anchor="w"
        )
        text_lbl.pack(side="left", fill="x", expand=True, pady=10)

        # Hover and click handlers
        def on_enter(e):
            if key != self.active_screen:
                inner.configure(fg_color=COLORS["sidebar_hover"])

        def on_leave(e):
            if key != self.active_screen:
                inner.configure(fg_color="transparent")

        def on_click(e, k=key):
            self.navigate(k)

        for widget in [frame, inner, icon_lbl, text_lbl]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        frame._inner = inner
        frame._icon  = icon_lbl
        frame._text  = text_lbl
        return frame

    def set_active(self, screen_key: str):
        # Deactivate old
        if self.active_screen and self.active_screen in self.nav_buttons:
            old = self.nav_buttons[self.active_screen]
            old._inner.configure(fg_color="transparent")
            old._icon.configure(text_color=COLORS["text_secondary"])
            old._text.configure(text_color=COLORS["text_secondary"])

        # Activate new
        self.active_screen = screen_key
        if screen_key in self.nav_buttons:
            btn = self.nav_buttons[screen_key]
            btn._inner.configure(fg_color=COLORS["sidebar_active"])
            btn._icon.configure(text_color=COLORS["gold"])
            btn._text.configure(text_color=COLORS["gold_light"])
