# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "redemption_id",
            "label": _("Redemption ID"),
            "fieldtype": "Link",
            "options": "Gift Redemption",
            "width": 140
        },
        {
            "fieldname": "redemption_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Loyalty Customer",
            "width": 120
        },
        {
            "fieldname": "customer_name",
            "label": _("Customer Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "petrol_pump",
            "label": _("Pump"),
            "fieldtype": "Link",
            "options": "Petrol Pump Location",
            "width": 150
        },
        {
            "fieldname": "gift_item",
            "label": _("Gift Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "points_required",
            "label": _("Points Used"),
            "fieldtype": "Float",
            "width": 100,
            "precision": 2
        },
        {
            "fieldname": "total_points",
            "label": _("Total Points"),
            "fieldtype": "Float",
            "width": 110,
            "precision": 2
        },
        {
            "fieldname": "gift_given_by",
            "label": _("Given By"),
            "fieldtype": "Link",
            "options": "User",
            "width": 120
        },
        {
            "fieldname": "stock_entry",
            "label": _("Stock Entry"),
            "fieldtype": "Link",
            "options": "Stock Entry",
            "width": 140
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    # Query joins Gift Redemption with Gift Redemption Item child table
    data = frappe.db.sql(f"""
        SELECT
            gr.name as redemption_id,
            gr.redemption_date,
            gr.customer,
            lc.customer_name,
            gr.petrol_pump,
            gri.gift_item,
            gri.item_name,
            gri.points_required,
            gr.total_points,
            gr.gift_given_by,
            gr.stock_entry
        FROM `tabGift Redemption` gr
        LEFT JOIN `tabLoyalty Customer` lc ON gr.customer = lc.name
        LEFT JOIN `tabGift Redemption Item` gri ON gri.parent = gr.name
        WHERE gr.docstatus = 1 {conditions}
        ORDER BY gr.redemption_date DESC, gr.name, gri.idx
    """, filters, as_dict=1)
    
    return data


def get_conditions(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND gr.redemption_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND gr.redemption_date <= %(to_date)s"
    
    if filters.get("petrol_pump"):
        conditions += " AND gr.petrol_pump = %(petrol_pump)s"
    
    if filters.get("customer"):
        conditions += " AND gr.customer = %(customer)s"
    
    if filters.get("gift_item"):
        conditions += " AND gri.gift_item = %(gift_item)s"
    
    return conditions


def get_chart_data(data):
    if not data:
        return None
    
    # Group by gift item
    gift_counts = {}
    for row in data:
        gift_item = row.get('item_name') or row.get('gift_item')
        if gift_item:
            gift_counts[gift_item] = gift_counts.get(gift_item, 0) + 1
    
    if not gift_counts:
        return None
    
    return {
        "data": {
            "labels": list(gift_counts.keys()),
            "datasets": [
                {
                    "name": "Redemptions",
                    "values": list(gift_counts.values())
                }
            ]
        },
        "type": "pie",
        "colors": ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#43e97b", "#00c9ff", "#92fe9d"]
    }


def get_summary(data):
    if not data:
        return []
    
    # Count unique redemption IDs (parent records)
    unique_redemptions = len(set(d['redemption_id'] for d in data if d.get('redemption_id')))
    
    # Sum total points from unique redemptions only
    seen_redemptions = set()
    total_points = 0
    for d in data:
        redemption_id = d.get('redemption_id')
        if redemption_id and redemption_id not in seen_redemptions:
            seen_redemptions.add(redemption_id)
            total_points += d.get('total_points', 0)
    
    # Count unique customers
    unique_customers = len(set(d['customer'] for d in data if d.get('customer')))
    
    # Count total gift items given
    total_items = len([d for d in data if d.get('gift_item')])
    
    return [
        {
            "value": unique_redemptions,
            "label": _("Total Redemptions"),
            "datatype": "Int",
            "indicator": "Blue"
        },
        {
            "value": total_items,
            "label": _("Total Items Given"),
            "datatype": "Int",
            "indicator": "Green"
        },
        {
            "value": total_points,
            "label": _("Total Points Redeemed"),
            "datatype": "Float",
            "indicator": "Orange"
        },
        {
            "value": unique_customers,
            "label": _("Unique Customers"),
            "datatype": "Int",
            "indicator": "Purple"
        }
    ]

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customers(doctype, txt, searchfield, start, page_len, filters):
    """
    Custom query to show customer name and mobile number in link field
    """
    return frappe.db.sql("""
        SELECT 
            name,
            CONCAT(customer_name, ' - ', mobile_number) as display_name
        FROM `tabLoyalty Customer`
        WHERE 
            status = 'Active'
            AND (
                customer_name LIKE %(txt)s 
                OR mobile_number LIKE %(txt)s
                OR name LIKE %(txt)s
            )
        ORDER BY customer_name
        LIMIT %(start)s, %(page_len)s
    """, {
        'txt': '%' + txt + '%',
        'start': start,
        'page_len': page_len
    })
