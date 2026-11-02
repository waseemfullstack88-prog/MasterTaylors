# =============================================================================
# main.py — Master Taylor's & Dress Designer  |  Tailor Shop Management System
# =============================================================================
import sys
import os

# ── Ensure project root is on the path ───────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from database.db_manager import DatabaseManager
from components.sidebar   import Sidebar
from screens.dashboard       import DashboardScreen
from screens.customers       import CustomersScreen
from screens.add_customer    import AddCustomerScreen
from screens.customer_profile import CustomerProfileScreen
from screens.measurement_form import MeasurementFormScreen
from screens.orders          import OrdersScreen
from screens.payments        import PaymentsScreen
from screens.reports         import ReportsScreen
from screens.backup          import BackupScreen
from utils.constants import APP_TITLE, WINDOW_SIZE, COLORS, FONTS

# ── Global CustomTkinter theme ────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class MasterTaylorsApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # ── Window setup ─────────────────────────────────────────────────────
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_dark"])

        # App icon (optional)
        try:
            ico = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass

        # ── Database ─────────────────────────────────────────────────────────
        self.db = DatabaseManager()

        # ── State ────────────────────────────────────────────────────────────
        self._current_screen = None
        self.screens: dict[str, ctk.CTkFrame] = {}

        # ── Layout ───────────────────────────────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, self.show_screen)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Content area
        self._content = ctk.CTkFrame(
            self, fg_color=COLORS["bg_dark"], corner_radius=0
        )
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        # ── Screens ──────────────────────────────────────────────────────────
        self._init_screens()

        # ── Start on dashboard ────────────────────────────────────────────────
        self.show_screen("dashboard")

        # ── Maximise on open ─────────────────────────────────────────────────
        self.after(100, lambda: self.state("zoomed"))

        # Graceful close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── Screens ──────────────────────────────────────────────────────────────

    def _init_screens(self):
        mapping = {
            "dashboard":        DashboardScreen,
            "customers":        CustomersScreen,
            "add_customer":     AddCustomerScreen,
            "customer_profile": CustomerProfileScreen,
            "measurement_form": MeasurementFormScreen,
            "orders":           OrdersScreen,
            "payments":         PaymentsScreen,
            "reports":          ReportsScreen,
            "backup":           BackupScreen,
        }
        for name, cls in mapping.items():
            screen = cls(self._content, self)
            screen.grid(row=0, column=0, sticky="nsew")
            screen.grid_remove()           # hide initially
            self.screens[name] = screen

    def show_screen(self, name: str, **kwargs):
        """Switch to a named screen, passing optional kwargs to on_show()."""
        # Hide current
        if self._current_screen and self._current_screen in self.screens:
            self.screens[self._current_screen].grid_remove()

        # Show new
        if name in self.screens:
            screen = self.screens[name]
            screen.grid()
            self._current_screen = name
            self.sidebar.set_active(name)
            if hasattr(screen, "on_show"):
                screen.on_show(**kwargs)

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    def _on_close(self):
        try:
            self.db.close()
        except Exception:
            pass
        self.destroy()


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = MasterTaylorsApp()
    app.mainloop()
