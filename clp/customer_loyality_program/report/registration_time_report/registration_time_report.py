import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not filters.start_datetime or not filters.end_datetime:
        frappe.throw(_("Start and end date/time are required."))
    start = frappe.utils.get_datetime(filters.start_datetime)
    end = frappe.utils.get_datetime(filters.end_datetime)
    if end <= start:
        frappe.throw(_("End date/time must be after start date/time."))
    columns = [
        {"label": _("Customer ID"), "fieldname": "name", "fieldtype": "Link", "options": "Loyalty Customer", "width": 150},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 180},
        {"label": _("Mobile"), "fieldname": "mobile_number", "fieldtype": "Data", "width": 120},
        {"label": _("Vehicle"), "fieldname": "vehicle_number", "fieldtype": "Data", "width": 120},
        {"label": _("Registered At"), "fieldname": "creation", "fieldtype": "Datetime", "width": 170},
        {"label": _("Created By"), "fieldname": "created_by_user", "fieldtype": "Link", "options": "User", "width": 160}
    ]
    conditions = ["creation >= %(start)s", "creation < %(end)s"]
    params = {"start": start, "end": end}
    # Pump-wise registration needs a dedicated registration_pump field. Avoid silently
    # filtering by current pump settings because that would misstate historical registrations.
    if filters.get("registration_pump"):
        if not frappe.db.has_column("Loyalty Customer", "registration_pump"):
            frappe.throw(_("Add a registration pump field before using the pump filter."))
        conditions.append("registration_pump = %(registration_pump)s")
        params["registration_pump"] = filters.registration_pump
    data = frappe.db.sql(
        "SELECT name, customer_name, mobile_number, vehicle_number, creation, created_by_user "
        "FROM `tabLoyalty Customer` WHERE " + " AND ".join(conditions) + " ORDER BY creation ASC",
        params, as_dict=True)
    summary = [{"label": _("Total Registrations"), "value": len(data), "indicator": "Green", "datatype": "Int"}]
    return columns, data, None, None, summary
