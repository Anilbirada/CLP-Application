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
            "width": 150
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
            "width": 130,
            "precision": 2
        },
        {
            "fieldname": "total_liters_purchased",
            "label": _("Total Purchased (L)"),
            "fieldtype": "Float",
            "width": 140,
            "precision": 2
        },
        {
            "fieldname": "total_gifts_received",
            "label": _("Gifts Received"),
            "fieldtype": "Int",
            "width": 110
        },
        {
            "fieldname": "last_gift_date",
            "label": _("Last Gift Date"),
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
            last_gift_date,
            registration_date,
            status
        FROM `tabLoyalty Customer`
        WHERE 1=1 {conditions}
        ORDER BY current_cycle_liters DESC, total_liters_purchased DESC
    """, filters, as_dict=1)
    
    return data


def get_conditions(filters):
    conditions = ""
    
    if filters.get("status"):
        conditions += " AND status = %(status)s"
    
    if filters.get("from_date"):
        conditions += " AND registration_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND registration_date <= %(to_date)s"
    
    if filters.get("min_points") is not None:
        conditions += " AND current_cycle_liters >= %(min_points)s"
    
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
            "labels": [d.get('customer_name', '')[:20] for d in top_customers],
            "datasets": [
                {
                    "name": "Current Points (L)",
                    "values": [d.get('current_cycle_liters', 0) for d in top_customers]
                }
            ]
        },
        "type": "bar",
        "colors": ["#667eea"],
        "height": 280
    }


def get_summary(data):
    if not data:
        return []
    
    total_customers = len(data)
    total_points = sum(d.get('current_cycle_liters', 0) for d in data)
    total_purchased = sum(d.get('total_liters_purchased', 0) for d in data)
    total_gifts = sum(d.get('total_gifts_received', 0) for d in data)
    
    # Calculate metrics
    avg_points = total_points / total_customers if total_customers > 0 else 0
    avg_purchased = total_purchased / total_customers if total_customers > 0 else 0
    
    # Count customers with positive points
    positive_balance = len([d for d in data if d.get('current_cycle_liters', 0) > 0])
    
    # Count customers with negative points
    negative_balance = len([d for d in data if d.get('current_cycle_liters', 0) < 0])
    
    # Active customers
    active_customers = len([d for d in data if d.get('status') == 'Active'])
    
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
            "value": positive_balance,
            "label": _("Positive Balance"),
            "datatype": "Int",
            "indicator": "Green"
        },
        {
            "value": negative_balance,
            "label": _("Negative Balance"),
            "datatype": "Int",
            "indicator": "Red" if negative_balance > 0 else "Gray"
        },
        {
            "value": round(total_points, 2),
            "label": _("Total Points Outstanding"),
            "datatype": "Float",
            "indicator": "Orange"
        },
        {
            "value": round(total_purchased, 2),
            "label": _("Total Fuel Sold (L)"),
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
            "value": round(avg_points, 2),
            "label": _("Avg Points/Customer"),
            "datatype": "Float",
            "indicator": "Cyan"
        },
        {
            "value": round(avg_purchased, 2),
            "label": _("Avg Purchase/Customer"),
            "datatype": "Float",
            "indicator": "Cyan"
        }
    ]
