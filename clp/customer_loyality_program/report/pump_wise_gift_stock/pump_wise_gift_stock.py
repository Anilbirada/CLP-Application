# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    return [
        {
            "fieldname": "petrol_pump",
            "label": _("Pump Name"),
            "fieldtype": "Link",
            "options": "Petrol Pump Location",
            "width": 180
        },
        {
            "fieldname": "pump_code",
            "label": _("Pump Code"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 180
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
            "label": _("Points Required (L)"),
            "fieldtype": "Float",
            "width": 130,
            "precision": 2
        },
        {
            "fieldname": "actual_qty",
            "label": _("Available Stock"),
            "fieldtype": "Float",
            "width": 120,
            "precision": 2
        },
        {
            "fieldname": "stock_uom",
            "label": _("UOM"),
            "fieldtype": "Link",
            "options": "UOM",
            "width": 80
        },
        {
            "fieldname": "stock_value",
            "label": _("Stock Value"),
            "fieldtype": "Currency",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT
            ppl.name as petrol_pump,
            ppl.pump_code,
            ppl.warehouse,
            pgi.gift_item,
            i.item_name,
            pgi.points_required,
            COALESCE(b.actual_qty, 0) as actual_qty,
            i.stock_uom,
            COALESCE(b.stock_value, 0) as stock_value
        FROM `tabPetrol Pump Location` ppl
        INNER JOIN `tabPump Gift Item` pgi ON pgi.parent = ppl.name
        INNER JOIN `tabItem` i ON i.name = pgi.gift_item
        LEFT JOIN `tabBin` b ON b.item_code = pgi.gift_item AND b.warehouse = ppl.warehouse
        WHERE ppl.is_active = 1 {conditions}
        ORDER BY ppl.name, pgi.points_required
    """, filters, as_dict=1)
    
    return data


def get_conditions(filters):
    conditions = ""
    
    if filters.get("petrol_pump"):
        conditions += " AND ppl.name = %(petrol_pump)s"
    
    if filters.get("gift_item"):
        conditions += " AND pgi.gift_item = %(gift_item)s"
    
    if filters.get("show_zero_stock"):
        pass  # Show all
    else:
        conditions += " AND COALESCE(b.actual_qty, 0) > 0"
    
    return conditions


def get_chart_data(data):
    if not data:
        return None
    
    # Group by pump and sum stock quantities
    pump_stock = {}
    for row in data:
        pump = row['petrol_pump']
        if pump not in pump_stock:
            pump_stock[pump] = 0
        pump_stock[pump] += row['actual_qty']
    
    return {
        "data": {
            "labels": list(pump_stock.keys()),
            "datasets": [
                {
                    "name": "Total Gift Items Stock",
                    "values": list(pump_stock.values())
                }
            ]
        },
        "type": "bar",
        "colors": ["#43e97b"],
        "barOptions": {
            "stacked": 0
        }
    }
