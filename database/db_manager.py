# =============================================================================
# database/db_manager.py — SQLite database manager for Master Taylor's
# =============================================================================
import sqlite3
import os
import json
import shutil
from datetime import datetime, date
from pathlib import Path


class DatabaseManager:
    """Handles all SQLite database operations."""

    DB_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "MasterTaylors"
    DB_FILE = DB_DIR / "master_taylors.db"

    def __init__(self):
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(
            str(self.DB_FILE),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.create_tables()

    # ─── Schema ───────────────────────────────────────────────────────────────

    def create_tables(self):
        cur = self.conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            serial_number   TEXT UNIQUE NOT NULL,
            name            TEXT NOT NULL,
            phone           TEXT,
            address         TEXT,
            reference_name  TEXT,
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now','localtime')),
            updated_at      TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS measurements (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id      INTEGER UNIQUE REFERENCES customers(id),
            length           TEXT,
            sleeve           TEXT,
            shoulder         TEXT,
            chest            TEXT,
            belly            TEXT,
            ghera            TEXT,
            trouser_length   TEXT,
            trouser_bottom   TEXT,
            waist            TEXT,
            collar_size      TEXT,
            cuff_size        TEXT,
            daman            TEXT,
            cb_collar        INTEGER DEFAULT 0,
            cb_cuff          INTEGER DEFAULT 0,
            cb_front_pocket  INTEGER DEFAULT 0,
            cb_side_pocket   INTEGER DEFAULT 0,
            cb_trouser_pocket INTEGER DEFAULT 0,
            cb_daman_round   INTEGER DEFAULT 0,
            cb_daman_straight INTEGER DEFAULT 0,
            cb_embroidery    INTEGER DEFAULT 0,
            cb_special       INTEGER DEFAULT 0,
            design_notes     TEXT,
            additional_notes TEXT,
            created_at       TEXT DEFAULT (datetime('now','localtime')),
            updated_at       TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS measurement_history (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id         INTEGER REFERENCES customers(id),
            measurement_snapshot TEXT,
            changed_at          TEXT DEFAULT (datetime('now','localtime')),
            change_note         TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id    INTEGER REFERENCES customers(id),
            order_date     TEXT DEFAULT (date('now','localtime')),
            delivery_date  TEXT,
            clothing_type  TEXT,
            quantity       INTEGER DEFAULT 1,
            total_amount   REAL DEFAULT 0,
            expense_amount REAL DEFAULT 0,
            status         TEXT DEFAULT 'Pending',
            design_notes   TEXT,
            created_at     TEXT DEFAULT (datetime('now','localtime')),
            updated_at     TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS payments (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id    INTEGER REFERENCES customers(id),
            order_id       INTEGER REFERENCES orders(id),
            payment_date   TEXT DEFAULT (date('now','localtime')),
            amount         REAL DEFAULT 0,
            payment_method TEXT DEFAULT 'نقد',
            notes          TEXT,
            created_at     TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT DEFAULT (date('now','localtime')),
            category     TEXT,
            amount       REAL DEFAULT 0,
            notes        TEXT,
            created_at   TEXT DEFAULT (datetime('now','localtime'))
        );
        """)
        self.conn.commit()

    # ─── Helper ───────────────────────────────────────────────────────────────

    def _row_to_dict(self, row):
        return dict(row) if row else None

    def _rows_to_list(self, rows):
        return [dict(r) for r in rows]

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def today(self):
        return date.today().strftime("%Y-%m-%d")

    # ─── Customers ────────────────────────────────────────────────────────────

    def get_next_serial(self):
        """Return next auto serial number (max numeric + 1)."""
        cur = self.conn.execute(
            "SELECT serial_number FROM customers ORDER BY CAST(serial_number AS INTEGER) DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            try:
                return str(int(row[0]) + 1)
            except ValueError:
                pass
        return "1"

    def serial_exists(self, serial, exclude_id=None):
        if exclude_id:
            cur = self.conn.execute(
                "SELECT id FROM customers WHERE serial_number=? AND id!=?",
                (serial, exclude_id)
            )
        else:
            cur = self.conn.execute(
                "SELECT id FROM customers WHERE serial_number=?", (serial,)
            )
        return cur.fetchone() is not None

    def add_customer(self, data: dict) -> int:
        cur = self.conn.execute(
            """INSERT INTO customers
               (serial_number, name, phone, address, reference_name, notes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (data["serial_number"], data["name"], data.get("phone",""),
             data.get("address",""), data.get("reference_name",""),
             data.get("notes",""), self.now(), self.now())
        )
        self.conn.commit()
        return cur.lastrowid

    def update_customer(self, cid: int, data: dict):
        self.conn.execute(
            """UPDATE customers SET
               serial_number=?, name=?, phone=?, address=?,
               reference_name=?, notes=?, updated_at=?
               WHERE id=?""",
            (data["serial_number"], data["name"], data.get("phone",""),
             data.get("address",""), data.get("reference_name",""),
             data.get("notes",""), self.now(), cid)
        )
        self.conn.commit()

    def get_customer(self, cid: int):
        cur = self.conn.execute("SELECT * FROM customers WHERE id=?", (cid,))
        return self._row_to_dict(cur.fetchone())

    def get_customer_by_serial(self, serial: str):
        cur = self.conn.execute(
            "SELECT * FROM customers WHERE serial_number=?", (serial,)
        )
        return self._row_to_dict(cur.fetchone())

    def search_customers(self, query: str):
        q = f"%{query}%"
        cur = self.conn.execute(
            """SELECT c.*,
               IFNULL((SELECT SUM(o.total_amount) FROM orders o WHERE o.customer_id=c.id),0)
                 - IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0)
                 AS due_balance,
               (SELECT o2.order_date FROM orders o2 WHERE o2.customer_id=c.id
                ORDER BY o2.created_at DESC LIMIT 1) AS last_order_date
               FROM customers c
               WHERE c.serial_number LIKE ?
                  OR c.name LIKE ?
                  OR c.phone LIKE ?
               ORDER BY CAST(c.serial_number AS INTEGER)""",
            (q, q, q)
        )
        return self._rows_to_list(cur.fetchall())

    def get_all_customers(self):
        cur = self.conn.execute(
            """SELECT c.*,
               IFNULL((SELECT SUM(o.total_amount) FROM orders o WHERE o.customer_id=c.id),0)
                 - IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0)
                 AS due_balance
               FROM customers c ORDER BY CAST(c.serial_number AS INTEGER)"""
        )
        return self._rows_to_list(cur.fetchall())

    def get_customer_due(self, cid: int) -> float:
        cur = self.conn.execute(
            """SELECT
               IFNULL((SELECT SUM(total_amount) FROM orders WHERE customer_id=?),0)
               - IFNULL((SELECT SUM(amount) FROM payments WHERE customer_id=?),0)""",
            (cid, cid)
        )
        row = cur.fetchone()
        return row[0] if row else 0.0

    def get_total_customers(self):
        cur = self.conn.execute("SELECT COUNT(*) FROM customers")
        return cur.fetchone()[0]

    # ─── Measurements ─────────────────────────────────────────────────────────

    def get_measurement(self, customer_id: int):
        cur = self.conn.execute(
            "SELECT * FROM measurements WHERE customer_id=?", (customer_id,)
        )
        return self._row_to_dict(cur.fetchone())

    def save_measurement(self, customer_id: int, data: dict, change_note: str = ""):
        existing = self.get_measurement(customer_id)
        if existing:
            # Save history first
            snapshot = json.dumps(existing)
            self.conn.execute(
                """INSERT INTO measurement_history
                   (customer_id, measurement_snapshot, changed_at, change_note)
                   VALUES (?, ?, ?, ?)""",
                (customer_id, snapshot, self.now(), change_note or "ناپ تبدیل")
            )
            # Update current
            self.conn.execute(
                """UPDATE measurements SET
                   length=?, sleeve=?, shoulder=?, chest=?, belly=?, ghera=?,
                   trouser_length=?, trouser_bottom=?, waist=?, collar_size=?,
                   cuff_size=?, daman=?,
                   cb_collar=?, cb_cuff=?, cb_front_pocket=?, cb_side_pocket=?,
                   cb_trouser_pocket=?, cb_daman_round=?, cb_daman_straight=?,
                   cb_embroidery=?, cb_special=?,
                   design_notes=?, additional_notes=?, updated_at=?
                   WHERE customer_id=?""",
                (data.get("length",""), data.get("sleeve",""), data.get("shoulder",""),
                 data.get("chest",""), data.get("belly",""), data.get("ghera",""),
                 data.get("trouser_length",""), data.get("trouser_bottom",""),
                 data.get("waist",""), data.get("collar_size",""), data.get("cuff_size",""),
                 data.get("daman",""),
                 int(data.get("cb_collar",0)), int(data.get("cb_cuff",0)),
                 int(data.get("cb_front_pocket",0)), int(data.get("cb_side_pocket",0)),
                 int(data.get("cb_trouser_pocket",0)), int(data.get("cb_daman_round",0)),
                 int(data.get("cb_daman_straight",0)), int(data.get("cb_embroidery",0)),
                 int(data.get("cb_special",0)),
                 data.get("design_notes",""), data.get("additional_notes",""),
                 self.now(), customer_id)
            )
        else:
            self.conn.execute(
                """INSERT INTO measurements
                   (customer_id, length, sleeve, shoulder, chest, belly, ghera,
                    trouser_length, trouser_bottom, waist, collar_size, cuff_size, daman,
                    cb_collar, cb_cuff, cb_front_pocket, cb_side_pocket,
                    cb_trouser_pocket, cb_daman_round, cb_daman_straight,
                    cb_embroidery, cb_special, design_notes, additional_notes,
                    created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (customer_id,
                 data.get("length",""), data.get("sleeve",""), data.get("shoulder",""),
                 data.get("chest",""), data.get("belly",""), data.get("ghera",""),
                 data.get("trouser_length",""), data.get("trouser_bottom",""),
                 data.get("waist",""), data.get("collar_size",""), data.get("cuff_size",""),
                 data.get("daman",""),
                 int(data.get("cb_collar",0)), int(data.get("cb_cuff",0)),
                 int(data.get("cb_front_pocket",0)), int(data.get("cb_side_pocket",0)),
                 int(data.get("cb_trouser_pocket",0)), int(data.get("cb_daman_round",0)),
                 int(data.get("cb_daman_straight",0)), int(data.get("cb_embroidery",0)),
                 int(data.get("cb_special",0)),
                 data.get("design_notes",""), data.get("additional_notes",""),
                 self.now(), self.now())
            )
        self.conn.commit()

    def get_measurement_history(self, customer_id: int):
        cur = self.conn.execute(
            """SELECT * FROM measurement_history
               WHERE customer_id=? ORDER BY changed_at DESC""",
            (customer_id,)
        )
        rows = self._rows_to_list(cur.fetchall())
        for r in rows:
            try:
                r["snapshot"] = json.loads(r["measurement_snapshot"])
            except Exception:
                r["snapshot"] = {}
        return rows

    # ─── Orders ───────────────────────────────────────────────────────────────

    def add_order(self, data: dict) -> int:
        cur = self.conn.execute(
            """INSERT INTO orders
               (customer_id, order_date, delivery_date, clothing_type, quantity,
                total_amount, expense_amount, status, design_notes, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (data["customer_id"], data.get("order_date", self.today()),
             data.get("delivery_date",""), data.get("clothing_type","شلوار قمیض"),
             int(data.get("quantity",1)), float(data.get("total_amount",0)),
             float(data.get("expense_amount",0)), data.get("status","Pending"),
             data.get("design_notes",""), self.now(), self.now())
        )
        # If advance payment provided, record it
        advance = float(data.get("advance_amount", 0))
        if advance > 0:
            self.conn.execute(
                """INSERT INTO payments
                   (customer_id, order_id, payment_date, amount, payment_method, notes, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (data["customer_id"], cur.lastrowid, self.today(),
                 advance, "نقد", "پیشگی ادائیگی", self.now())
            )
        self.conn.commit()
        return cur.lastrowid

    def update_order(self, oid: int, data: dict):
        self.conn.execute(
            """UPDATE orders SET
               order_date=?, delivery_date=?, clothing_type=?, quantity=?,
               total_amount=?, expense_amount=?, status=?, design_notes=?, updated_at=?
               WHERE id=?""",
            (data.get("order_date", self.today()), data.get("delivery_date",""),
             data.get("clothing_type",""), int(data.get("quantity",1)),
             float(data.get("total_amount",0)), float(data.get("expense_amount",0)),
             data.get("status","Pending"), data.get("design_notes",""),
             self.now(), oid)
        )
        self.conn.commit()

    def update_order_status(self, oid: int, status: str):
        self.conn.execute(
            "UPDATE orders SET status=?, updated_at=? WHERE id=?",
            (status, self.now(), oid)
        )
        self.conn.commit()

    def get_order(self, oid: int):
        cur = self.conn.execute(
            """SELECT o.*, c.name AS customer_name, c.serial_number,
               IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id),0) AS paid_amount
               FROM orders o LEFT JOIN customers c ON c.id=o.customer_id
               WHERE o.id=?""", (oid,)
        )
        return self._row_to_dict(cur.fetchone())

    def get_customer_orders(self, customer_id: int):
        cur = self.conn.execute(
            """SELECT o.*,
               IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id),0) AS paid_amount,
               o.total_amount - IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id),0)
                 AS order_due
               FROM orders o WHERE o.customer_id=?
               ORDER BY o.order_date DESC""",
            (customer_id,)
        )
        return self._rows_to_list(cur.fetchall())

    def get_all_orders(self, status=None, start_date=None, end_date=None):
        q = """SELECT o.*, c.name AS customer_name, c.serial_number, c.phone,
               IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id),0) AS paid_amount,
               o.total_amount - IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id),0)
                 AS order_due
               FROM orders o LEFT JOIN customers c ON c.id=o.customer_id
               WHERE 1=1"""
        params = []
        if status:
            q += " AND o.status=?"
            params.append(status)
        if start_date:
            q += " AND o.order_date>=?"
            params.append(start_date)
        if end_date:
            q += " AND o.order_date<=?"
            params.append(end_date)
        q += " ORDER BY o.order_date DESC"
        cur = self.conn.execute(q, params)
        return self._rows_to_list(cur.fetchall())

    def get_today_orders(self):
        cur = self.conn.execute(
            "SELECT COUNT(*) FROM orders WHERE order_date=?", (self.today(),)
        )
        return cur.fetchone()[0]

    def get_orders_by_status(self, status: str):
        cur = self.conn.execute(
            "SELECT COUNT(*) FROM orders WHERE status=?", (status,)
        )
        return cur.fetchone()[0]

    def get_upcoming_deliveries(self, days=7):
        from datetime import timedelta
        end = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
        cur = self.conn.execute(
            """SELECT o.*, c.name AS customer_name, c.phone
               FROM orders o LEFT JOIN customers c ON c.id=o.customer_id
               WHERE o.delivery_date BETWEEN ? AND ?
               AND o.status NOT IN ('Delivered','Cancelled')
               ORDER BY o.delivery_date""",
            (self.today(), end)
        )
        return self._rows_to_list(cur.fetchall())

    # ─── Payments ─────────────────────────────────────────────────────────────

    def add_payment(self, data: dict) -> int:
        cur = self.conn.execute(
            """INSERT INTO payments
               (customer_id, order_id, payment_date, amount, payment_method, notes, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (data["customer_id"], data.get("order_id"),
             data.get("payment_date", self.today()),
             float(data.get("amount",0)), data.get("payment_method","نقد"),
             data.get("notes",""), self.now())
        )
        self.conn.commit()
        return cur.lastrowid

    def get_customer_payments(self, customer_id: int):
        cur = self.conn.execute(
            """SELECT p.*, o.clothing_type
               FROM payments p LEFT JOIN orders o ON o.id=p.order_id
               WHERE p.customer_id=? ORDER BY p.payment_date DESC""",
            (customer_id,)
        )
        return self._rows_to_list(cur.fetchall())

    def get_order_payments(self, order_id: int):
        cur = self.conn.execute(
            "SELECT * FROM payments WHERE order_id=? ORDER BY payment_date DESC",
            (order_id,)
        )
        return self._rows_to_list(cur.fetchall())

    def get_all_payments(self, start_date=None, end_date=None):
        q = """SELECT p.*, c.name AS customer_name, c.serial_number,
               o.clothing_type
               FROM payments p
               LEFT JOIN customers c ON c.id=p.customer_id
               LEFT JOIN orders o ON o.id=p.order_id
               WHERE 1=1"""
        params = []
        if start_date:
            q += " AND p.payment_date>=?"
            params.append(start_date)
        if end_date:
            q += " AND p.payment_date<=?"
            params.append(end_date)
        q += " ORDER BY p.payment_date DESC"
        cur = self.conn.execute(q, params)
        return self._rows_to_list(cur.fetchall())

    def get_total_dues(self):
        cur = self.conn.execute(
            """SELECT
               IFNULL((SELECT SUM(total_amount) FROM orders WHERE status!='Cancelled'),0)
               - IFNULL((SELECT SUM(amount) FROM payments),0)"""
        )
        row = cur.fetchone()
        return max(row[0], 0) if row else 0.0

    # ─── Reports ──────────────────────────────────────────────────────────────

    def get_income_by_period(self, start_date: str, end_date: str):
        cur = self.conn.execute(
            "SELECT IFNULL(SUM(amount),0) FROM payments WHERE payment_date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        return cur.fetchone()[0] or 0.0

    def get_expenses_by_period(self, start_date: str, end_date: str):
        """Sum of order expenses (cost) for orders delivered in period."""
        cur = self.conn.execute(
            """SELECT IFNULL(SUM(expense_amount),0) FROM orders
               WHERE order_date BETWEEN ? AND ? AND expense_amount > 0""",
            (start_date, end_date)
        )
        return cur.fetchone()[0] or 0.0

    def get_orders_report(self, start_date: str, end_date: str):
        cur = self.conn.execute(
            """SELECT o.*, c.name AS customer_name, c.serial_number,
               IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.order_id=o.id),0) AS paid_amount
               FROM orders o LEFT JOIN customers c ON c.id=o.customer_id
               WHERE o.order_date BETWEEN ? AND ?
               ORDER BY o.order_date DESC""",
            (start_date, end_date)
        )
        return self._rows_to_list(cur.fetchall())

    def get_dues_report(self):
        cur = self.conn.execute(
            """SELECT c.serial_number, c.name, c.phone,
               IFNULL(SUM(o.total_amount),0) AS total_billed,
               IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0) AS total_paid,
               IFNULL(SUM(o.total_amount),0)
               - IFNULL((SELECT SUM(p.amount) FROM payments p WHERE p.customer_id=c.id),0) AS balance
               FROM customers c LEFT JOIN orders o ON o.customer_id=c.id
               GROUP BY c.id
               HAVING balance > 0
               ORDER BY balance DESC"""
        )
        return self._rows_to_list(cur.fetchall())

    def get_dashboard_stats(self):
        from datetime import timedelta
        today = self.today()
        w_start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        m_start = date.today().replace(day=1).strftime("%Y-%m-%d")

        total_customers   = self.get_total_customers()
        today_orders      = self.get_today_orders()
        pending_orders    = self.get_orders_by_status("Pending")
        cutting_orders    = self.get_orders_by_status("Cutting")
        stitching_orders  = self.get_orders_by_status("Stitching")
        ready_orders      = self.get_orders_by_status("Ready")
        delivered_orders  = self.get_orders_by_status("Delivered")
        total_dues        = self.get_total_dues()
        weekly_income     = self.get_income_by_period(w_start, today)
        monthly_income    = self.get_income_by_period(m_start, today)
        monthly_expenses  = self.get_expenses_by_period(m_start, today)
        monthly_profit    = monthly_income - monthly_expenses

        recent_customers = self._rows_to_list(
            self.conn.execute(
                "SELECT * FROM customers ORDER BY created_at DESC LIMIT 5"
            ).fetchall()
        )
        upcoming = self.get_upcoming_deliveries(7)

        return {
            "total_customers":  total_customers,
            "today_orders":     today_orders,
            "pending_orders":   pending_orders,
            "cutting_orders":   cutting_orders,
            "stitching_orders": stitching_orders,
            "ready_orders":     ready_orders,
            "delivered_orders": delivered_orders,
            "total_dues":       total_dues,
            "weekly_income":    weekly_income,
            "monthly_income":   monthly_income,
            "monthly_profit":   monthly_profit,
            "recent_customers": recent_customers,
            "upcoming":         upcoming,
        }

    # ─── Expenses ─────────────────────────────────────────────────────────────

    def add_expense(self, data: dict):
        self.conn.execute(
            "INSERT INTO expenses (expense_date, category, amount, notes, created_at) VALUES (?,?,?,?,?)",
            (data.get("expense_date", self.today()), data.get("category","عام"),
             float(data.get("amount",0)), data.get("notes",""), self.now())
        )
        self.conn.commit()

    # ─── Backup & Restore ─────────────────────────────────────────────────────

    def backup(self, dest_dir: str) -> str:
        ts   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest = Path(dest_dir) / f"master_taylors_backup_{ts}.db"
        shutil.copy2(str(self.DB_FILE), str(dest))
        return str(dest)

    def restore(self, src_path: str):
        """Restore from a backup file. Closes and reopens connection."""
        self.conn.close()
        shutil.copy2(src_path, str(self.DB_FILE))
        self.conn = sqlite3.connect(
            str(self.DB_FILE),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")

    def close(self):
        if self.conn:
            self.conn.close()
