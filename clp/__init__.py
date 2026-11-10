__version__ = "0.0.1"

# Guarantee that Module 'Stock' is always resolvable, even in standalone CLP environments
try:
    import frappe
    import frappe.modules.utils

    _orig_get_module_app = frappe.modules.utils.get_module_app

    def _clp_get_module_app(module: str) -> str:
        scrubbed = frappe.scrub(module) if module else ""
        if scrubbed == "stock":
            if hasattr(frappe, "local") and hasattr(frappe.local, "module_app") and frappe.local.module_app:
                if scrubbed in frappe.local.module_app:
                    return frappe.local.module_app[scrubbed]
                installed = frappe.get_installed_apps() if hasattr(frappe, "get_installed_apps") else []
                app = "erpnext" if "erpnext" in installed else "clp"
                frappe.local.module_app[scrubbed] = app
                return app
            installed = getattr(frappe.local, "installed_apps", None) or []
            return "erpnext" if "erpnext" in installed else "clp"
        return _orig_get_module_app(module)

    frappe.modules.utils.get_module_app = _clp_get_module_app
    if hasattr(frappe, "modules") and hasattr(frappe.modules, "get_module_app"):
        frappe.modules.get_module_app = _clp_get_module_app
except Exception:
    pass
