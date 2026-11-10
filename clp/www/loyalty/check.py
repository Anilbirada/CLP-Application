import frappe

def get_context(context):
    """Seamlessly redirect /loyalty/check to /loyality/check with all query parameters intact."""
    qs = ""
    try:
        if hasattr(frappe.request, "query_string") and frappe.request.query_string:
            qs = frappe.request.query_string.decode() if isinstance(frappe.request.query_string, bytes) else str(frappe.request.query_string)
    except Exception:
        pass
    
    target = f"/loyality/check?{qs}" if qs else "/loyality/check"
    frappe.local.flags.redirect_location = target
    raise frappe.Redirect
