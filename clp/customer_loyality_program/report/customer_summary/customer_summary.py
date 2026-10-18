# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters.get("customer"):
        frappe.throw(_("Please select a customer"))
    
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    summary = get_summary(data, filters)
    
    return columns, data, None, chart, summary

def get_columns():
    return [
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "transaction_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 140
        },
        {
            "fieldname": "reference_id",
            "label": _("Reference ID"),
            "fieldtype": "Dynamic Link",
            "options": "reference_doctype",
            "width": 130
        },
        {
            "fieldname": "petrol_pump",
            "label": _("Pump"),
            "fieldtype": "Link",
            "options": "Petrol Pump Location",
            "width": 150
        },
        {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "points_change",
            "label": _("Points Change"),
            "fieldtype": "Float",
            "width": 120,
            "precision": 2
        },
        {
            "fieldname": "running_balance",
            "label": _("Balance"),
            "fieldtype": "Float",
            "width": 100,
            "precision": 2
        },
        {
            "fieldname": "fuel_type",
            "label": _("Fuel Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "fieldname": "slip_no",
            "label": _("Slip No"),
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    customer = filters.get("customer")
    
    # Get all transactions
    transactions = []
    
    # Fetch fuel purchases
    fuel_conditions = get_fuel_conditions(filters)
    fuel_entries = frappe.db.sql(f"""
        SELECT
            name as reference_id,
            'Fuel Purchase Entry' as reference_doctype,
            purchase_date as date,
            'Fuel Purchase' as transaction_type,
            petrol_pump,
            fuel_type,
            liters,
            amount,
            slip_no,
            CONCAT(liters, 'L ', fuel_type, ' - ₹', amount) as description
        FROM `tabFuel Purchase Entry`
        WHERE customer = %(customer)s
            AND docstatus = 1
            {fuel_conditions}
        ORDER BY purchase_date ASC
    """, {"customer": customer, **filters}, as_dict=1)
    
    for entry in fuel_entries:
        transactions.append({
            "date": entry.date,
            "transaction_type": entry.transaction_type,
            "reference_id": entry.reference_id,
            "reference_doctype": entry.reference_doctype,
            "petrol_pump": entry.petrol_pump,
            "description": entry.description,
            "points_change": entry.liters,  # Positive points
            "fuel_type": entry.fuel_type,
            "amount": entry.amount,
            "slip_no": entry.slip_no
        })
    
    # Fetch gift redemptions
    gift_conditions = get_gift_conditions(filters)
    gift_entries = frappe.db.sql(f"""
        SELECT
            gr.name as reference_id,
            'Gift Redemption' as reference_doctype,
            gr.redemption_date as date,
            'Gift Redemption' as transaction_type,
            gr.petrol_pump,
            gr.total_points,
            gr.slip_no,
            GROUP_CONCAT(gri.item_name SEPARATOR ', ') as gift_items
        FROM `tabGift Redemption` gr
        LEFT JOIN `tabGift Redemption Item` gri ON gri.parent = gr.name
        WHERE gr.customer = %(customer)s
            AND gr.docstatus = 1
            {gift_conditions}
        GROUP BY gr.name
        ORDER BY gr.redemption_date ASC
    """, {"customer": customer, **filters}, as_dict=1)
    
    for entry in gift_entries:
        transactions.append({
            "date": entry.date,
            "transaction_type": entry.transaction_type,
            "reference_id": entry.reference_id,
            "reference_doctype": entry.reference_doctype,
            "petrol_pump": entry.petrol_pump,
            "description": f"Redeemed: {entry.gift_items or 'Items'}",
            "points_change": -1 * (entry.total_points or 0),  # Negative points
            "fuel_type": "",
            "amount": 0,
            "slip_no": entry.slip_no
        })
    
    # Sort by date
    transactions.sort(key=lambda x: x["date"])
    
    # Calculate running balance
    running_balance = 0
    for txn in transactions:
        running_balance += txn.get("points_change", 0)
        txn["running_balance"] = running_balance
    
    return transactions

def get_fuel_conditions(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND purchase_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND purchase_date <= %(to_date)s"
    
    if filters.get("petrol_pump"):
        conditions += " AND petrol_pump = %(petrol_pump)s"
    
    if filters.get("transaction_type") == "Gift Redemption":
        conditions += " AND 1=0"  # Exclude all fuel entries
    
    return conditions

def get_gift_conditions(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND gr.redemption_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND gr.redemption_date <= %(to_date)s"
    
    if filters.get("petrol_pump"):
        conditions += " AND gr.petrol_pump = %(petrol_pump)s"
    
    if filters.get("transaction_type") == "Fuel Purchase":
        conditions += " AND 1=0"  # Exclude all gift redemptions
    
    return conditions

def get_chart_data(data, filters):
    if not data:
        return None
    
    # Show points trend over time
    dates = []
    balances = []
    
    for row in data:
        date_str = frappe.format(row.get("date"), {"fieldtype": "Date"})
        dates.append(date_str)
        balances.append(row.get("running_balance", 0))
    
    # Limit to last 30 entries for readability
    if len(dates) > 30:
        dates = dates[-30:]
        balances = balances[-30:]
    
    return {
        "data": {
            "labels": dates,
            "datasets": [
                {
                    "name": "Points Balance",
                    "values": balances
                }
            ]
        },
        "type": "line",
        "colors": ["#667eea"],
        "height": 280
    }

def get_summary(data, filters):
    if not data:
        return []
    
    # Get customer details
    customer = frappe.get_doc("Loyalty Customer", filters.get("customer"))
    
    # Calculate metrics
    total_fuel_purchases = len([d for d in data if d.get("transaction_type") == "Fuel Purchase"])
    total_redemptions = len([d for d in data if d.get("transaction_type") == "Gift Redemption"])
    
    total_liters_purchased = sum(d.get("points_change", 0) for d in data if d.get("points_change", 0) > 0)
    total_points_redeemed = abs(sum(d.get("points_change", 0) for d in data if d.get("points_change", 0) < 0))
    
    total_amount_spent = sum(d.get("amount", 0) for d in data)
    
    current_balance = data[-1].get("running_balance", 0) if data else 0
    
    return [
        {
            "value": customer.customer_name,
            "label": _("Customer Name"),
            "datatype": "Data",
            "indicator": "Blue"
        },
        {
            "value": customer.mobile_number,
            "label": _("Mobile Number"),
            "datatype": "Data",
            "indicator": "Blue"
        },
        {
            "value": customer.vehicle_number,
            "label": _("Vehicle Number"),
            "datatype": "Data",
            "indicator": "Blue"
        },
        {
            "value": total_fuel_purchases,
            "label": _("Total Fuel Purchases"),
            "datatype": "Int",
            "indicator": "Green"
        },
        {
            "value": total_redemptions,
            "label": _("Total Redemptions"),
            "datatype": "Int",
            "indicator": "Red"
        },
        {
            "value": round(total_liters_purchased, 2),
            "label": _("Total Liters Purchased"),
            "datatype": "Float",
            "indicator": "Purple"
        },
        {
            "value": round(total_points_redeemed, 2),
            "label": _("Total Points Redeemed"),
            "datatype": "Float",
            "indicator": "Orange"
        },
        {
            "value": round(current_balance, 2),
            "label": _("Current Balance"),
            "datatype": "Float",
            "indicator": "Green" if current_balance >= 0 else "Red"
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
