import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    user_roles = set(frappe.get_roles())
    if not ({"System Manager", "Pump Owner", "CLM Incharge", "CLP Reports Viewer", "CLP Referral Manager"} & user_roles):
        frappe.throw(_("Not permitted to view referral rewards"), frappe.PermissionError)
    columns = [
        {"label": _("Reward ID"), "fieldname": "name", "fieldtype": "Link", "options": "Referral Reward Entry", "width": 150},
        {"label": _("Referrer ID"), "fieldname": "referrer", "fieldtype": "Link", "options": "Loyalty Customer", "width": 140},
        {"label": _("Referrer"), "fieldname": "referrer_name", "fieldtype": "Data", "width": 160},
        {"label": _("Referred Customer"), "fieldname": "referred_customer_name", "fieldtype": "Data", "width": 160},
        {"label": _("Fuel Transaction"), "fieldname": "fuel_purchase_entry", "fieldtype": "Link", "options": "Fuel Purchase Entry", "width": 150},
        {"label": _("Pump"), "fieldname": "petrol_pump", "fieldtype": "Link", "options": "Petrol Pump Location", "width": 140},
        {"label": _("Points"), "fieldname": "points_awarded", "fieldtype": "Int", "width": 80},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
        {"label": _("Reward Date"), "fieldname": "reward_date", "fieldtype": "Datetime", "width": 160}
    ]
    cond = ["1=1"]; params = {}
    if filters.get("from_datetime"):
        cond.append("r.reward_date >= %(start)s"); params["start"] = frappe.utils.get_datetime(filters.from_datetime)
    if filters.get("to_datetime"):
        cond.append("r.reward_date < %(end)s"); params["end"] = frappe.utils.get_datetime(filters.to_datetime)
    if filters.get("from_datetime") and filters.get("to_datetime"):
        if params["end"] <= params["start"]:
            frappe.throw(_("End date/time must be after start date/time."))
    if filters.get("petrol_pump"):
        cond.append("r.petrol_pump = %(pump)s"); params["pump"] = filters.petrol_pump
    if filters.get("status"):
        cond.append("r.status = %(status)s"); params["status"] = filters.status
    data = frappe.db.sql("""SELECT r.name, r.referrer, c.customer_name AS referrer_name,
        rc.customer_name AS referred_customer_name, r.fuel_purchase_entry, r.petrol_pump,
        r.points_awarded, r.status, r.reward_date
        FROM `tabReferral Reward Entry` r
        LEFT JOIN `tabLoyalty Customer` c ON c.name = r.referrer
        LEFT JOIN `tabLoyalty Customer` rc ON rc.name = r.referred_customer
        WHERE """ + " AND ".join(cond) + " ORDER BY r.reward_date DESC", params, as_dict=True)
    total = sum((row.points_awarded or 0) * (1 if row.status == "Awarded" else -1) for row in data)
    summary = [{"label": _("Net Points Awarded"), "value": total, "indicator": "Green", "datatype": "Int"}]
    return columns, data, None, None, summary
