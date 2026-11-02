# ✂️ MasterTaylors — Bespoke Tailoring & Order Management Desktop Suite

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active_Development-10B981?style=for-the-badge)

**MasterTaylors** is a desktop management system built in Python for bespoke tailoring businesses. It streamlines customer profiles, detailed body measurement records, order tracking, payment ledgers, PDF invoice/receipt generation, and database backups.

---

## ✨ Key Modules

- **📊 Dashboard (`screens/dashboard.py`):** Live overview of active orders, pending deliveries, revenue metrics, and recent customer activity.
- **👥 Customer & Profile Management (`screens/customers.py`, `screens/customer_profile.py`):** Searchable customer directory with complete order and measurement history.
- **📏 Custom Measurement Forms (`screens/measurement_form.py`):** Digital measurement sheets for suits, shalwar kameez, waistcoats, and custom garments.
- **🧵 Order Lifecycle Tracking (`screens/orders.py`):** Manage order statuses from *Booked* → *Cutting* → *Stitching* → *Ready* → *Delivered*.
- **💳 Payments & Ledger (`screens/payments.py`):** Track advance payments, remaining balances, and full payment histories.
- **📄 PDF Receipt & Measurement Slip Generator (`pdf/pdf_generator.py`):** Printable PDF invoices and tailor measurement tickets.
- **💾 Automated Database Backups (`screens/backup.py`, `database/db_manager.py`):** One-click SQLite backup and restore utilities.

---

## 🚀 Getting Started

```bash
git clone https://github.com/waseemfullstack88-prog/MasterTaylors.git
cd MasterTaylors
pip install -r requirements.txt
python main.py
```
