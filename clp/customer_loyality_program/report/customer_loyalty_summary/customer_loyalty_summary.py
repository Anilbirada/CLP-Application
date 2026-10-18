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
            "fieldname": "customer_id",
            "label": _("Customer ID"),
            "fieldtype": "Link",
            "options": "Loyalty Customer",
            "width": 120
        },
        {
            "fieldname": "customer_name",
            "label": _("Customer Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "vehicle_number",
            "label": _("Vehicle"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "mobile_number",
            "label": _("Mobile"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "current_cycle_liters",
            "label": _("Current Points (L)"),
            "fieldtype": "Float",
            "width": 140,
            "precision": 2
        },
        {
            "fieldname": "total_liters_purchased",
            "label": _("Total Purchased (L)"),
            "fieldtype": "Float",
            "width": 150,
            "precision": 2
        },
        {
            "fieldname": "total_gifts_received",
            "label": _("Gifts Received"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "last_purchase_date",
            "label": _("Last Purchase"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "last_gift_date",
            "label": _("Last Gift"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "registration_date",
            "label": _("Registered On"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT 
            name as customer_id,
            customer_name,
            vehicle_number,
            mobile_number,
            current_cycle_liters,
            total_liters_purchased,
            total_gifts_received,
            last_purchase_date,
            last_gift_date,
            registration_date,
            status
        FROM `tabLoyalty Customer`
        WHERE 1=1 {conditions}
        ORDER BY current_cycle_liters DESC, total_liters_purchased DESC
    """, as_dict=1)
    
    return data


def get_conditions(filters):
    conditions = ""
    
    if filters.get("status"):
        conditions += " AND status = %(status)s"
    
    return conditions


def get_chart_data(data):
    if not data:
        return None
    
    # Top 10 customers by points
    top_customers = sorted(data, key=lambda x: x.get('current_cycle_liters', 0), reverse=True)[:10]
    
    if not top_customers:
        return None
    
    return {
        "data": {
            "labels": [d.get('customer_name', 'Unknown')[:20] for d in top_customers],
            "datasets": [
                {
                    "name": "Loyalty Points",
                    "values": [d.get('current_cycle_liters', 0) for d in top_customers]
                }
            ]
        },
        "type": "bar",
        "colors": ["#667eea"],
        "barOptions": {
            "stacked": False
        }
    }


def get_summary(data):
    if not data:
        return []
    
    total_customers = len(data)
    active_customers = len([d for d in data if d.get('status') == 'Active'])
    total_points = sum(d.get('current_cycle_liters', 0) for d in data)
    total_purchases = sum(d.get('total_liters_purchased', 0) for d in data)
    total_gifts = sum(d.get('total_gifts_received', 0) for d in data)
    
    # Customers with negative balance
    negative_balance = len([d for d in data if d.get('current_cycle_liters', 0) < 0])
    
    # Average points per customer
    avg_points = total_points / total_customers if total_customers > 0 else 0
    
    return [
        {
            "value": total_customers,
            "label": _("Total Customers"),
            "datatype": "Int",
            "indicator": "Blue"
        },
        {
            "value": active_customers,
            "label": _("Active Customers"),
            "datatype": "Int",
            "indicator": "Green"
        },
        {
            "value": total_points,
            "label": _("Total Points Outstanding"),
            "datatype": "Float",
            "indicator": "Orange"
        },
        {
            "value": total_purchases,
            "label": _("Total Liters Sold"),
            "datatype": "Float",
            "indicator": "Purple"
        },
        {
            "value": total_gifts,
            "label": _("Total Gifts Given"),
            "datatype": "Int",
            "indicator": "Red"
        },
        {
            "value": negative_balance,
            "label": _("Negative Balance Customers"),
            "datatype": "Int",
            "indicator": "Red" if negative_balance > 0 else "Gray"
        },
        {
            "value": round(avg_points, 2),
            "label": _("Avg Points/Customer"),
            "datatype": "Float",
            "indicator": "Cyan"
        }
    ]
