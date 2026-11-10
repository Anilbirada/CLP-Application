import frappe

def execute():
    """Ensure Module Def for 'Stock' is registered and points to an active app."""
    try:
        installed = frappe.get_installed_apps() if hasattr(frappe, "get_installed_apps") else []
        app = "erpnext" if "erpnext" in installed else "clp"

        if frappe.db.exists("Module Def", "Stock"):
            frappe.db.set_value("Module Def", "Stock", {
                "app_name": app,
                "disabled": 0
            }, update_modified=False)
        else:
            doc = frappe.get_doc({
                "doctype": "Module Def",
                "module_name": "Stock",
                "app_name": app,
                "disabled": 0
            })
            doc.flags.ignore_permissions = True
            doc.insert()

        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"fix_stock_module_definition patch error: {e}", "CLP Migration")
