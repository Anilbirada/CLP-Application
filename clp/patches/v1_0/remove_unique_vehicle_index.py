import frappe

def execute():
    """Remove a standalone unique index on vehicle_number so duplicates are permitted."""
    table = "tabLoyalty Customer"
    try:
        indexes = frappe.db.sql("SHOW INDEX FROM `tabLoyalty Customer`", as_dict=True)
    except Exception:
        return
    grouped = {}
    for row in indexes:
        grouped.setdefault(row.get("Key_name"), []).append(row)
    for name, rows in grouped.items():
        if not name or name == "PRIMARY":
            continue
        unique = all(int(r.get("Non_unique", 1)) == 0 for r in rows)
        columns = [r.get("Column_name") for r in sorted(rows, key=lambda x: int(x.get("Seq_in_index", 1)))]
        if unique and columns == ["vehicle_number"]:
            safe_name = name.replace("`", "``")
            frappe.db.sql(f"ALTER TABLE `{table}` DROP INDEX `{safe_name}`")
