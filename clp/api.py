# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
import qrcode
from io import BytesIO
import base64
from frappe import _
from urllib.parse import quote
from frappe.rate_limiter import rate_limit


CLP_STAFF_ROLES = {
    "System Manager", "Pump Owner", "Pump Manager", "CLM Incharge",
    "CLP Stock Add", "CLP Stock Subtract", "CLP Stock Transfer",
    "CLP Reports Viewer", "CLP Referral Manager",
}

def _has_role(role, user=None):
    """Check if current user (or specified user) has the given role."""
    return role in frappe.get_roles(user)

def _require_clp_staff(roles=None):
    """Reject Guest and authenticated users without an explicitly permitted CLP role."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please sign in to use this feature."), frappe.PermissionError)
    allowed = set(roles or CLP_STAFF_ROLES)
    user_roles = set(frappe.get_roles())
    if not (user_roles & allowed):
        frappe.throw(_("You do not have permission to access this CLP feature."), frappe.PermissionError)

@frappe.whitelist()
def get_customers_for_search(doctype, txt, searchfield, start, page_len, filters):
    """Enhanced search showing ID, name, vehicle, mobile with space-free vehicle matching"""
    import re
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    clean_txt = re.sub(r'[\s\-]+', '', txt or '').upper()
    return frappe.db.sql("""
        SELECT 
            name,
            CONCAT(name, ' - ', customer_name, ' - ', vehicle_number) as label
        FROM `tabLoyalty Customer`
        WHERE 
            status = 'Active'
            AND (
                name LIKE %(txt)s
                OR customer_name LIKE %(txt)s
                OR vehicle_number LIKE %(txt)s
                OR REPLACE(REPLACE(UPPER(vehicle_number), ' ', ''), '-', '') LIKE %(clean_txt)s
                OR mobile_number LIKE %(txt)s
                OR REPLACE(mobile_number, ' ', '') LIKE %(clean_txt)s
            )
        ORDER BY name DESC
        LIMIT %(page_len)s OFFSET %(start)s
    """, {
        'txt': f'%{txt}%',
        'clean_txt': f'%{clean_txt}%',
        'start': start,
        'page_len': page_len
    })


@frappe.whitelist()
def check_customer_exists(customer_id):
    """Check if customer exists - SERVER SIDE"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    if frappe.db.exists("Loyalty Customer", customer_id):
        customer = frappe.get_doc("Loyalty Customer", customer_id)
        return {
            "exists": True,
            "customer_id": customer.name,
            "customer_name": customer.customer_name,
            "vehicle_number": customer.vehicle_number,
            "mobile_number": customer.mobile_number,
            "current_cycle_liters": customer.current_cycle_liters,
            "total_gifts_received": customer.total_gifts_received
        }
    else:
        return {
            "exists": False,
            "customer_id": customer_id
        }

@frappe.whitelist()
def scan_and_process_qr(qr_data):
    """Process scanned QR code"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    if not qr_data or len(qr_data) > 2048:
        frappe.throw(_("Invalid QR data"))
    # Extract customer ID from URL
    if '?id=' in qr_data:
        customer_id = qr_data.split('?id=')[1]
    else:
        customer_id = qr_data.split('/')[-1]
    
    # Use check_customer_exists function
    return check_customer_exists(customer_id)

@frappe.whitelist()
def generate_qr_image(customer_id):
    """Generate QR code for customer"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    if not frappe.db.exists("Loyalty Customer", customer_id):
        frappe.throw(_("Customer not found"))
    site_url = frappe.utils.get_url()
    token = frappe.db.get_value("Loyalty Customer", customer_id, "qr_access_token")
    if not token:
        import secrets
        token = secrets.token_urlsafe(32)
        frappe.db.set_value("Loyalty Customer", customer_id, "qr_access_token", token)
    qr_data = f"{site_url}/loyality/check?token={quote(token)}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {"image": f"data:image/png;base64,{img_str}"}

@frappe.whitelist()
def bulk_generate_qr_codes(start_num=0, count=100, output_dir=None):
    """Generate a ZIP of QR images for customers ordered by registration.

    ``start_num`` is a zero-based offset, not a customer ID; this supports the
    app's MANUAL-/QR-prefixed naming series rather than assuming numeric IDs.
    ``output_dir`` is retained for backward-compatible calls but is ignored.
    """
    import zipfile
    _require_clp_staff({"System Manager", "Pump Owner"})
    try:
        offset, count = int(start_num), int(count)
    except (TypeError, ValueError):
        frappe.throw(_("Start offset and count must be integers"))
    if offset < 0 or count < 1 or count > 500:
        frappe.throw(_("Offset cannot be negative and count must be between 1 and 500"))

    customers = frappe.get_all(
        "Loyalty Customer", fields=["name", "qr_access_token"],
        order_by="creation asc", limit_start=offset, limit_page_length=count
    )
    site_url = frappe.utils.get_url()
    archive = BytesIO()
    generated = 0
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for customer in customers:
            token = customer.qr_access_token
            if not token:
                import secrets
                token = secrets.token_urlsafe(32)
                frappe.db.set_value("Loyalty Customer", customer.name, "qr_access_token", token)
            qr_data = f"{site_url}/loyality/check?token={quote(token)}"
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qr_data)
            qr.make(fit=True)
            image_buffer = BytesIO()
            qr.make_image(fill_color="black", back_color="white").save(image_buffer, format="PNG")
            safe_name = "".join(ch for ch in customer.name if ch.isalnum() or ch in "-_ .")[:120] or "customer"
            bundle.writestr(f"qr_{safe_name}.png", image_buffer.getvalue())
            generated += 1

    file_doc = frappe.get_doc({
        "doctype": "File", "file_name": "clp_customer_qr_codes.zip",
        "is_private": 1, "content": archive.getvalue()
    })
    file_doc.insert(ignore_permissions=True)
    return {"success": True, "count": generated, "file_url": file_doc.file_url}

@frappe.whitelist()
def get_pump_gift_stock(petrol_pump):
    """Get total actual gift stock at pump from Bin table"""
    _require_clp_staff()
    pump = frappe.get_doc("Petrol Pump Location", petrol_pump)
    
    if not pump.warehouse:
        return {
            "pump_name": pump.pump_name,
            "qty": 0
        }
    
    if not pump.gift_items or len(pump.gift_items) == 0:
        return {
            "pump_name": pump.pump_name,
            "qty": 0
        }
    
    # Get actual stock from Bin table for all gift items
    total_stock = 0
    
    for gift_item in pump.gift_items:
        stock = frappe.db.get_value("Bin", {
            "item_code": gift_item.gift_item,
            "warehouse": pump.warehouse
        }, "actual_qty") or 0
        
        total_stock += float(stock)
    
    return {
        "pump_name": pump.pump_name,
        "qty": total_stock
    }

@frappe.whitelist()
def get_item_stock_at_warehouse(item_code, warehouse):
    """Get actual stock quantity of an item at a warehouse"""
    _require_clp_staff()
    stock = frappe.db.get_value("Bin", 
        {
            "item_code": item_code, 
            "warehouse": warehouse
        }, 
        "actual_qty"
    )
    
    return float(stock) if stock else 0.0

@frappe.whitelist()
def get_top_customers_chart(limit=10):
    """Get top customers by loyalty points for chart"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge", "CLP Reports Viewer"})
    limit = min(max(int(limit or 10), 1), 100)
    data = frappe.db.sql("""
        SELECT 
            customer_name as name,
            current_cycle_liters as value
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
        ORDER BY current_cycle_liters DESC
        LIMIT %s
    """, (int(limit),), as_dict=1)
    
    labels = [d.name for d in data]
    values = [d.value for d in data]
    
    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Loyalty Points (L)",
                "values": values
            }
        ],
        "type": "bar"
    }

@frappe.whitelist()
def get_monthly_fuel_sales(months=6):
    """Get monthly fuel sales for chart"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge", "CLP Reports Viewer"})
    months = min(max(int(months or 6), 1), 36)
    from frappe.utils import add_months, today, formatdate
    
    start_date = add_months(today(), -int(months))
    
    data = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(purchase_date, '%%Y-%%m') as month,
            SUM(liters) as total_liters,
            COUNT(*) as total_purchases
        FROM `tabFuel Purchase Entry`
        WHERE docstatus = 1
        AND purchase_date >= %s
        GROUP BY DATE_FORMAT(purchase_date, '%%Y-%%m')
        ORDER BY month
    """, (start_date,), as_dict=1)
    
    labels = [d.month for d in data]
    liters = [d.total_liters for d in data]
    purchases = [d.total_purchases for d in data]
    
    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Liters Sold",
                "values": liters
            },
            {
                "name": "Number of Purchases",
                "values": purchases
            }
        ],
        "type": "line"
    }

@frappe.whitelist()
def get_customer_with_highest_points():
    """Get customer with highest loyalty points"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge", "CLP Reports Viewer"})
    customer = frappe.db.sql("""
        SELECT 
            name as customer_id,
            customer_name,
            current_cycle_liters,
            vehicle_number,
            mobile_number
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
        ORDER BY current_cycle_liters DESC
        LIMIT 1
    """, as_dict=1)
    
    if customer:
        return customer[0]
    return {}
@frappe.whitelist()
def search_customer_for_scanner(search_text):
    """Enhanced search for QR scanner - ID, name, vehicle, mobile with space-free matching"""
    import re
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    if not search_text:
        frappe.throw(_("Please enter search text"))
    
    # Clean and prepare search text
    search_text = search_text.strip()
    clean_search = re.sub(r'[\s\-]+', '', search_text).upper()
    search_pattern = f"%{search_text}%"
    clean_pattern = f"%{clean_search}%"
    
    customers = frappe.db.sql("""
        SELECT 
            name,
            customer_name,
            vehicle_number,
            mobile_number,
            current_cycle_liters,
            total_gifts_received
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
        AND (
            LOWER(name) LIKE LOWER(%(search)s)
            OR LOWER(customer_name) LIKE LOWER(%(search)s)
            OR LOWER(vehicle_number) LIKE LOWER(%(search)s)
            OR REPLACE(REPLACE(UPPER(vehicle_number), ' ', ''), '-', '') LIKE %(clean_pattern)s
            OR mobile_number LIKE %(search)s
            OR REPLACE(mobile_number, ' ', '') LIKE %(clean_pattern)s
        )
        ORDER BY 
            CASE 
                WHEN LOWER(name) = LOWER(%(exact)s) THEN 1
                WHEN REPLACE(REPLACE(UPPER(vehicle_number), ' ', ''), '-', '') = %(clean_exact)s THEN 2
                WHEN LOWER(name) LIKE LOWER(%(search)s) THEN 3
                WHEN LOWER(customer_name) LIKE LOWER(%(search)s) THEN 4
                WHEN REPLACE(REPLACE(UPPER(vehicle_number), ' ', ''), '-', '') LIKE %(clean_pattern)s THEN 5
                ELSE 6
            END,
            modified DESC
        LIMIT 20
    """, {"search": search_pattern, "exact": search_text, "clean_pattern": clean_pattern, "clean_exact": clean_search}, as_dict=1)
    
    return customers



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_pump_gift_items(doctype, txt, searchfield, start, page_len, filters):
    """Get gift items for selected pump - used in Link query"""
    _require_clp_staff()
    petrol_pump = filters.get('petrol_pump')
    if not petrol_pump:
        return []
    
    return frappe.db.sql("""
        SELECT DISTINCT i.name, i.item_name
        FROM `tabItem` i
        INNER JOIN `tabPump Gift Item` pgi ON pgi.gift_item = i.name
        WHERE pgi.parent = %(pump)s
        AND (i.item_name LIKE %(txt)s OR i.name LIKE %(txt)s)
        ORDER BY i.item_name
        LIMIT %(start)s, %(page_len)s
    """, {
        'pump': petrol_pump,
        'txt': f'%{txt}%',
        'start': start,
        'page_len': page_len
    })


@frappe.whitelist()
def get_gift_item_points(petrol_pump, gift_item):
    """Get points required and available stock for gift item"""
    _require_clp_staff()
    if not petrol_pump or not gift_item:
        return {"points_required": 0, "available_stock": 0}
    
    # Get points from Pump Gift Item
    points = frappe.db.get_value("Pump Gift Item", {
        "parent": petrol_pump,
        "gift_item": gift_item
    }, "points_required") or 0
    
    # Get warehouse from pump
    warehouse = frappe.db.get_value("Petrol Pump Location", petrol_pump, "warehouse")
    
    # Get stock from Bin
    stock = 0
    if warehouse:
        stock = frappe.db.get_value("Bin", {
            "item_code": gift_item,
            "warehouse": warehouse
        }, "actual_qty") or 0
    
    return {
        "points_required": points,
        "available_stock": stock
    }



@frappe.whitelist()
def export_report_to_pdf(report_name, filters=None):
    """Export report to PDF"""
    _require_clp_staff({"System Manager", "Pump Owner", "CLM Incharge", "CLP Reports Viewer"})
    from frappe.utils.pdf import get_pdf
    from frappe.desk.query_report import run
    
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    # Get report data
    report = frappe.get_doc("Report", report_name)
    result = run(report_name, filters=filters)
    
    columns = result.get("columns", [])
    data = result.get("result", [])
    
    # Generate HTML
    html = frappe.render_template(
        "frappe/www/printview.html",
        {
            "title": report_name,
            "columns": columns,
            "data": data,
            "report_name": report_name,
            "filters": filters
        }
    )
    
    # Generate PDF
    pdf = get_pdf(html, {"orientation": "Landscape"})
    
    # Create file
    file_name = f"{report_name.replace(' ', '_')}.pdf"
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "is_private": 1,
        "content": pdf
    })
    file_doc.save()
    
    return file_doc.file_url

@frappe.whitelist()
def get_gift_stock_data(pump=None, item=None, status=None):
    """Get gift stock data for management page"""
    _require_clp_staff()
    if status and status not in {"in_stock", "low_stock", "out_of_stock"}:
        frappe.throw(_("Invalid stock status filter"))
    conditions = []
    params = {}
    if pump:
        conditions.append("ppl.name = %(pump)s")
        params["pump"] = pump
    if item:
        conditions.append("pgi.gift_item = %(item)s")
        params["item"] = item
    filter_sql = " AND " + " AND ".join(conditions) if conditions else ""
    
    data = frappe.db.sql(f"""
        SELECT
            ppl.name as pump,
            ppl.pump_name,
            ppl.warehouse,
            pgi.gift_item as item_code,
            i.item_name,
            pgi.points_required,
            COALESCE(b.actual_qty, 0) as actual_qty
        FROM `tabPetrol Pump Location` ppl
        INNER JOIN `tabPump Gift Item` pgi ON pgi.parent = ppl.name
        INNER JOIN `tabItem` i ON i.name = pgi.gift_item
        LEFT JOIN `tabBin` b ON b.item_code = pgi.gift_item AND b.warehouse = ppl.warehouse
        WHERE ppl.is_active = 1 {filter_sql}
        ORDER BY ppl.pump_name, i.item_name
    """, params, as_dict=1)
    
    # Filter by status if specified
    if status:
        if status == 'in_stock':
            data = [d for d in data if d.actual_qty > 10]
        elif status == 'low_stock':
            data = [d for d in data if 0 < d.actual_qty <= 10]
        elif status == 'out_of_stock':
            data = [d for d in data if d.actual_qty <= 0]
    
    return data


@frappe.whitelist()
def adjust_gift_stock(item_code, warehouse, qty, action, reason):
    """Adjust gift stock - add or remove, with server-side role enforcement."""
    action = (action or "").lower().strip()
    if action not in ("add", "remove"):
        frappe.throw(_("Action must be add or remove"))
    required_role = "CLP Stock Add" if action == "add" else "CLP Stock Subtract"
    if not (_has_role("System Manager") or _has_role("Pump Owner") or _has_role(required_role)):
        frappe.throw(_("You do not have permission to {0} gift stock").format(action), frappe.PermissionError)
    try:
        qty = float(qty)
    except (TypeError, ValueError):
        frappe.throw(_("Quantity must be a valid number"))
    if qty <= 0:
        frappe.throw(_("Quantity must be greater than zero"))
    reason = str(reason or "").strip()
    if not reason:
        frappe.throw(_("A reason is required for stock adjustment"))
    
    if not frappe.db.exists("Warehouse", warehouse):
        frappe.throw(_("Warehouse does not exist"))
    if not frappe.db.exists("Item", item_code):
        frappe.throw(_("Gift item does not exist"))
    if not frappe.db.exists("Pump Gift Item", {"gift_item": item_code, "parenttype": "Petrol Pump Location"}):
        frappe.throw(_("Only configured CLP gift items can be adjusted"))

    # Create Stock Entry
    stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Receipt" if action == "add" else "Material Issue",
        "company": frappe.defaults.get_defaults().company,
        "remarks": f"Gift Stock Adjustment: {reason}",
        "items": [{
            "item_code": item_code,
            "qty": qty,
            "t_warehouse": warehouse if action == "add" else None,
            "s_warehouse": warehouse if action == "remove" else None,
            "cost_center": frappe.db.get_value("Company", frappe.defaults.get_defaults().company, "cost_center")
        }]
    })
    
    stock_entry.insert()
    stock_entry.submit()
    
    return {
        "success": True,
        "stock_entry": stock_entry.name
    }


@frappe.whitelist()
def get_loyalty_dashboard_stats():
    """Get dashboard statistics"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge", "CLP Reports Viewer"})
    from frappe.utils import today, add_days

    today_date = today()
    tomorrow = add_days(today_date, 1)

    total_customers = frappe.db.count("Loyalty Customer")
    active_customers = frappe.db.count("Loyalty Customer", {"status": "Active"})

    total_points = frappe.db.sql("""
        SELECT COALESCE(SUM(current_cycle_liters), 0) as total
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
    """)[0][0] or 0

    total_gifts = frappe.db.sql("""
        SELECT COALESCE(SUM(total_gifts_received), 0) as total
        FROM `tabLoyalty Customer`
    """)[0][0] or 0

    today_purchases = frappe.db.count("Fuel Purchase Entry", [
        ["purchase_date", ">=", today_date],
        ["purchase_date", "<", tomorrow],
        ["docstatus", "=", 1],
    ])

    today_redemptions = frappe.db.count("Gift Redemption", [
        ["redemption_date", ">=", today_date],
        ["redemption_date", "<", tomorrow],
        ["docstatus", "=", 1],
    ])
    
    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_points": round(total_points, 2),
        "total_gifts": total_gifts,
        "today_purchases": today_purchases,
        "today_redemptions": today_redemptions
    }

@frappe.whitelist()
def create_quick_sale(customer_name, mobile_number, vehicle_number, petrol_pump, fuel_type=None, liters=0, amount=0, referred_by_customer=None):
    """Create quick sale for walk-in customer"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    if not customer_name or not mobile_number or not vehicle_number or not petrol_pump:
        frappe.throw(_("Customer name, mobile, vehicle and pump are required"))
    try:
        liters = float(liters or 0)
        amount = float(amount or 0)
    except (TypeError, ValueError):
        frappe.throw(_("Liters and amount must be valid numbers"))
    if liters <= 0 or amount < 0:
        frappe.throw(_("Liters must be positive and amount cannot be negative"))
    
    # Check if customer already exists
    existing = frappe.db.exists("Loyalty Customer", {
        "vehicle_number": vehicle_number.upper(),
        "mobile_number": mobile_number
    })
    
    if existing:
        customer_id = existing
        customer_doc = frappe.get_doc("Loyalty Customer", customer_id)
    else:
        # Create new customer
        customer_doc = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": customer_name,
            "mobile_number": mobile_number,
            "vehicle_number": vehicle_number.upper(),
            "registration_pump": petrol_pump,
            "referred_by_customer": referred_by_customer,
            "status": "Active"
        })
        customer_doc.insert()
        customer_id = customer_doc.name
    
    # Create fuel purchase entry
    purchase = frappe.get_doc({
        "doctype": "Fuel Purchase Entry",
        "customer": customer_id,
        "petrol_pump": petrol_pump,
        "fuel_type": fuel_type,
        "liters": liters,
        "amount": amount,
        "purchase_date": frappe.utils.now()
    })
    purchase.insert()
    purchase.submit()
    
    # Reload customer to get updated points
    customer_doc.reload()
    
    return {
        "success": True,
        "customer_id": customer_id,
        "customer_name": customer_doc.customer_name,
        "vehicle_number": customer_doc.vehicle_number,
        "fuel_type": fuel_type,
        "liters": liters,
        "amount": amount,
        "points_earned": liters,
        "total_points": customer_doc.current_cycle_liters
    }
    
@frappe.whitelist()
def register_customer_with_qr(qr_code, customer_name, mobile_number, vehicle_number, referred_by_customer=None, registration_pump=None):
    """Register a new customer with a scanned QR code"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    if not qr_code or not customer_name or not mobile_number or not vehicle_number:
        frappe.throw(_("QR code, customer name, mobile and vehicle are required"))
    doc = frappe.new_doc('Loyalty Customer')
    doc.__qr_code = qr_code  # Set the special attribute for autoname
    doc.customer_name = customer_name
    doc.mobile_number = mobile_number
    doc.vehicle_number = vehicle_number
    doc.referred_by_customer = referred_by_customer
    doc.registration_pump = registration_pump
    doc.status = 'Active'
    doc.naming_series = 'QR-.####.'
    doc.insert()
    
    return doc

# ============================================================================
# User Pump Settings APIs
# ============================================================================

@frappe.whitelist()
def get_user_default_pump():
    """Get current user's default pump settings"""
    user = frappe.session.user
    
    # REMOVED: Don't skip Administrator - let it return settings
    settings = frappe.db.get_value("User Pump Settings", 
        {"user": user, "is_active": 1},
        ["default_pump", "default_warehouse"],
        as_dict=True
    )
    
    return settings or {}



@frappe.whitelist()
def set_my_pump_settings(pump):
    """Set or update current user's default pump"""
    user = frappe.session.user
    
    if user in ["Administrator", "Guest"]:
        frappe.throw("Cannot set settings for system users")
    if not pump or not frappe.db.exists("Petrol Pump Location", {"name": pump, "is_active": 1}):
        frappe.throw(_("Please select a valid active petrol pump"))
    warehouse = frappe.db.get_value("Petrol Pump Location", pump, "warehouse")
    
    existing = frappe.db.exists("User Pump Settings", {"user": user})
    
    if existing:
        doc = frappe.get_doc("User Pump Settings", existing)
        doc.default_pump = pump
        doc.default_warehouse = warehouse
        doc.is_active = 1
        doc.save()
    else:
        doc = frappe.get_doc({
            "doctype": "User Pump Settings",
            "user": user,
            "default_pump": pump,
            "default_warehouse": warehouse,
            "is_active": 1
        })
        doc.insert()
    
    return doc


# ============================================================================
# Gift Redemption - Multiple Items Support
# ============================================================================

@frappe.whitelist()
def get_available_gifts(petrol_pump):
    """Get available gift items for a pump with stock"""
    _require_clp_staff()
    pump = frappe.get_doc("Petrol Pump Location", petrol_pump)
    
    if not pump.warehouse:
        return []
    
    gifts = []
    for item in pump.gift_items:
        stock = frappe.db.get_value("Bin", {
            "item_code": item.gift_item,
            "warehouse": pump.warehouse
        }, "actual_qty") or 0
        
        gifts.append({
            "gift_item": item.gift_item,
            "item_name": item.item_name,
            "points_required": item.points_required,
            "available_stock": stock
        })
    
    return gifts


@frappe.whitelist()
def get_gift_item_details(petrol_pump, gift_item):
    """Get single gift item details with stock"""
    _require_clp_staff()
    from frappe import _
    
    pump = frappe.get_doc("Petrol Pump Location", petrol_pump)
    
    # Find gift in pump settings
    gift_config = None
    for item in pump.gift_items:
        if item.gift_item == gift_item:
            gift_config = item
            break
    
    if not gift_config:
        frappe.throw(_("Gift item {0} is not configured for {1}").format(gift_item, petrol_pump))
    
    # Get stock
    stock = frappe.db.get_value("Bin", {
        "item_code": gift_item,
        "warehouse": pump.warehouse
    }, "actual_qty") or 0
    
    return {
        "gift_item": gift_item,
        "item_name": gift_config.item_name,
        "points_required": gift_config.points_required,
        "available_stock": stock
    }



# ============================================================================
# WhatsApp Integration
# ============================================================================

@frappe.whitelist()
def get_whatsapp_link(customer_id, pump_name=None):
    """Generate WhatsApp link with customer loyalty info"""
    _require_clp_staff({"System Manager", "Pump Owner", "Pump Manager", "CLM Incharge"})
    from urllib.parse import quote  # Import here too for safety
    
    customer = frappe.get_doc("Loyalty Customer", customer_id)
    
    # Format phone number - remove spaces, add 91
    phone = customer.mobile_number.replace(" ", "").replace("-", "").replace("+", "")
    if not phone.startswith("91"):
        phone = "91" + phone
    
    # Use provided pump name or generic
    if not pump_name:
        pump_name = "our pump"
    
    # Build message
    message = f"""Hello {customer.customer_name}! 🎉

Your Loyalty Program Status:
━━━━━━━━━━━━━━━━━━
✅ Current Points: {customer.current_cycle_liters} Liters
🎁 Total Gifts Redeemed: {customer.total_gifts_received}
📊 Total Fuel Purchased: {customer.total_liters_purchased}L

Check your points anytime here:
https://clm.abmtech.in/loyality/check

Thank you for choosing {pump_name}!

Keep fueling with us! ⛽"""
    
    # URL encode using quote instead of urllib.parse.quote
    encoded_message = quote(message)
    
    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
    return {
        "url": whatsapp_url,
        "phone": phone,
        "customer_name": customer.customer_name
    }

    

@frappe.whitelist(allow_guest=True)
@rate_limit(limit=30, seconds=60, ip_based=True)
def check_loyalty_points(vehicle=None, mobile=None):
    """Public API to check loyalty points - accepts vehicle, mobile number, or both with smart auto-detection."""
    import re
    
    clean_vehicle = str(vehicle or '').strip()
    clean_mobile = str(mobile or '').strip()

    # Smart auto-detection: if mobile looks like a vehicle or vehicle looks like a mobile
    digits_in_vehicle = re.sub(r'\D', '', clean_vehicle)
    if len(digits_in_vehicle) == 10 and not clean_mobile:
        clean_mobile = digits_in_vehicle
        clean_vehicle = ''
    elif re.search(r'[A-Za-z]', clean_mobile) and not clean_vehicle:
        clean_vehicle = clean_mobile
        clean_mobile = ''

    # Normalize parameters
    norm_vehicle = re.sub(r'[\s\-\./\\]+', '', clean_vehicle).upper() if clean_vehicle else None
    norm_mobile = re.sub(r'\D', '', clean_mobile) if clean_mobile else None
    if norm_mobile and len(norm_mobile) > 10:
        norm_mobile = norm_mobile[-10:]

    result = {
        'found': False,
        'error': '',
        'customer': None,
        'purchases': [],
        'redemptions': []
    }

    if not norm_vehicle and not norm_mobile:
        result['error'] = "Please provide your vehicle number or 10-digit mobile number."
        return result

    try:
        customer_record = None

        # 1. Search by mobile number if provided
        if norm_mobile and len(norm_mobile) >= 7:
            mobile_matches = frappe.db.sql("""
                SELECT name, customer_name, vehicle_number, mobile_number,
                       current_cycle_liters, total_liters_purchased, total_gifts_received,
                       registration_date, referral_points_balance
                FROM `tabLoyalty Customer`
                WHERE RIGHT(REPLACE(REPLACE(mobile_number, ' ', ''), '-', ''), 10) = %s
                   OR mobile_number LIKE %s
                ORDER BY current_cycle_liters DESC
                LIMIT 1
            """, (norm_mobile, f"%{norm_mobile}%"), as_dict=1)
            if mobile_matches:
                customer_record = mobile_matches[0]

        # 2. Search by vehicle or doc name if not yet found
        if not customer_record and norm_vehicle:
            vehicle_matches = frappe.db.sql("""
                SELECT name, customer_name, vehicle_number, mobile_number,
                       current_cycle_liters, total_liters_purchased, total_gifts_received,
                       registration_date, referral_points_balance
                FROM `tabLoyalty Customer`
                WHERE REPLACE(REPLACE(REPLACE(UPPER(vehicle_number), ' ', ''), '-', ''), '.', '') = %s
                   OR UPPER(name) = %s
                ORDER BY current_cycle_liters DESC
                LIMIT 1
            """, (norm_vehicle, norm_vehicle), as_dict=1)
            if vehicle_matches:
                customer_record = vehicle_matches[0]

        # 3. Fallback: Search Fuel Purchase Entry by vehicle number to find linked customer
        if not customer_record and norm_vehicle:
            fpe_matches = frappe.db.sql("""
                SELECT customer FROM `tabFuel Purchase Entry`
                WHERE REPLACE(REPLACE(REPLACE(UPPER(vehicle_number), ' ', ''), '-', ''), '.', '') = %s
                  AND customer IS NOT NULL AND customer != ''
                ORDER BY creation DESC
                LIMIT 1
            """, (norm_vehicle,), as_dict=1)
            if fpe_matches and fpe_matches[0].get('customer'):
                cust_doc = frappe.db.sql("""
                    SELECT name, customer_name, vehicle_number, mobile_number,
                           current_cycle_liters, total_liters_purchased, total_gifts_received,
                           registration_date, referral_points_balance
                    FROM `tabLoyalty Customer`
                    WHERE name = %s
                    LIMIT 1
                """, (fpe_matches[0]['customer'],), as_dict=1)
                if cust_doc:
                    customer_record = cust_doc[0]

        if not customer_record:
            searched_terms = []
            if norm_vehicle: searched_terms.append(f"vehicle '{clean_vehicle}'")
            if norm_mobile: searched_terms.append(f"mobile '{clean_mobile}'")
            result['error'] = f"No customer found matching {' or '.join(searched_terms)}. Please check the number or contact pump support."
            return result

        result['found'] = True
        result['customer'] = {
            'name': customer_record['name'],
            'customer_name': customer_record['customer_name'] or 'Valued Customer',
            'vehicle_number': customer_record['vehicle_number'] or 'N/A',
            'mobile_number': customer_record['mobile_number'] or 'N/A',
            'current_cycle_liters': round(float(customer_record.get('current_cycle_liters') or 0.0), 2),
            'total_liters_purchased': round(float(customer_record.get('total_liters_purchased') or 0.0), 2),
            'total_gifts_received': int(customer_record.get('total_gifts_received') or 0),
            'registration_date': str(customer_record.get('registration_date') or ''),
            'referral_points_balance': round(float(customer_record.get('referral_points_balance') or 0.0), 2)
        }

        # Fetch recent purchases (daily transactions up to 15 entries)
        purchases = frappe.db.sql("""
            SELECT purchase_date, liters, amount, fuel_type, petrol_pump
            FROM `tabFuel Purchase Entry`
            WHERE customer = %s AND docstatus IN (0, 1)
            ORDER BY purchase_date DESC
            LIMIT 15
        """, (customer_record['name'],), as_dict=1)

        result['purchases'] = [
            {
                'purchase_date': str(p['purchase_date']),
                'liters': round(float(p['liters'] or 0.0), 2),
                'amount': round(float(p['amount'] or 0.0), 2),
                'fuel_type': p.get('fuel_type') or 'Fuel',
                'petrol_pump': p.get('petrol_pump') or 'Main Pump Station'
            }
            for p in purchases
        ] if purchases else []

        # Fetch recent gift redemptions
        redemptions = frappe.db.sql("""
            SELECT DISTINCT name, redemption_date, petrol_pump, total_points
            FROM `tabGift Redemption`
            WHERE customer = %s AND docstatus IN (0, 1)
            ORDER BY redemption_date DESC
            LIMIT 10
        """, (customer_record['name'],), as_dict=1)

        redemptions_with_items = []
        for red in redemptions:
            items = frappe.db.sql("""
                SELECT gift_item, item_name, points_required
                FROM `tabGift Redemption Item`
                WHERE parent = %s
                ORDER BY idx
            """, (red['name'],), as_dict=1)

            redemptions_with_items.append({
                'name': red['name'],
                'redemption_date': str(red['redemption_date']),
                'petrol_pump': red.get('petrol_pump') or 'Station Store',
                'total_points': round(float(red.get('total_points') or 0.0), 2),
                'items': [
                    {
                        'gift_item': i.get('gift_item') or '',
                        'item_name': i.get('item_name') or 'Gift Reward',
                        'points_required': round(float(i.get('points_required') or 0.0), 2)
                    }
                    for i in items
                ] if items else []
            })

        result['redemptions'] = redemptions_with_items

    except Exception as e:
        frappe.log_error(str(e), "Loyalty Check API Error")
        result['error'] = f"Unable to retrieve records: {str(e)}"

    return result


# ---------------------------------------------------------------------------
# Additional CLP requirements: time-based registrations, dynamic roles, QR
# token lookup and referral reporting.
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_registration_report(start_datetime, end_datetime, petrol_pump=None, limit=500):
    """Return registrations in [start_datetime, end_datetime), optionally by pump.

    Uses standard Frappe creation timestamp as the exact registration timestamp.
    """
    if not (_has_role("System Manager") or _has_role("Pump Owner") or _has_role("CLM Incharge") or _has_role("CLP Reports Viewer")):
        frappe.throw(_("Not permitted to view registration reports"), frappe.PermissionError)
    start = frappe.utils.get_datetime(start_datetime)
    end = frappe.utils.get_datetime(end_datetime)
    if end <= start:
        frappe.throw(_("End date/time must be after start date/time"))
    try:
        limit = min(max(int(limit or 500), 1), 5000)
    except (TypeError, ValueError):
        frappe.throw(_("Limit must be an integer between 1 and 5000"))
    conditions = ["creation >= %s", "creation < %s"]
    params = [start, end]
    if petrol_pump:
        # Registration pump is optional in the legacy schema; use a field only if present.
        if frappe.db.has_column("Loyalty Customer", "registration_pump"):
            conditions.append("registration_pump = %s")
            params.append(petrol_pump)
        else:
            frappe.throw(_("Pump-wise registration filtering requires a registration_pump field on Loyalty Customer."))
    where_sql = " AND ".join(conditions)
    rows = frappe.db.sql(f"""SELECT name, customer_name, mobile_number, vehicle_number, creation, created_by_user
        FROM `tabLoyalty Customer` WHERE {where_sql} ORDER BY creation ASC LIMIT %s""", tuple(params + [limit]), as_dict=True)
    total = frappe.db.sql(f"SELECT COUNT(*) FROM `tabLoyalty Customer` WHERE {where_sql}", tuple(params))[0][0]
    return {"count": total, "returned": len(rows), "registrations": rows, "start_datetime": str(start), "end_datetime_exclusive": str(end)}


@frappe.whitelist()
def set_user_roles(user, roles):
    """Assign/deassign roles using Frappe's native User roles. Only owner/admin."""
    if not (_has_role("System Manager") or _has_role("Pump Owner")):
        frappe.throw(_("Only a Pump Owner or System Manager can manage user roles"), frappe.PermissionError)
    if isinstance(roles, str):
        roles = frappe.parse_json(roles)
    if not isinstance(roles, list):
        frappe.throw(_("Roles must be a list"))
    allowed_managed = {"Pump Manager", "CLM Incharge", "Pump Owner", "CLP Stock Add", "CLP Stock Subtract", "CLP Stock Transfer", "CLP Reports Viewer", "CLP Referral Manager"}
    cleaned = []
    for role in roles:
        if role not in allowed_managed:
            frappe.throw(_("Role not allowed for assignment: {0}").format(role))
        if not frappe.db.exists("Role", role):
            frappe.throw(_("Role does not exist: {0}").format(role))
        cleaned.append(role)
    doc = frappe.get_doc("User", user)
    if doc.name == "Administrator" and frappe.session.user != "Administrator":
        frappe.throw(_("Cannot modify Administrator roles"), frappe.PermissionError)
    # System Manager is intentionally outside this UI-managed set; never remove it here.
    managed_roles = allowed_managed
    preserved = [row.role for row in (doc.roles or []) if row.role not in managed_roles]
    doc.set("roles", [])
    for role in sorted(set(preserved + cleaned)):
        doc.append("roles", {"role": role})
    doc.save(ignore_permissions=True)
    frappe.get_doc({"doctype":"Comment", "comment_type":"Info", "reference_doctype":"User", "reference_name":user,
                    "content":frappe.as_json({"action":"roles_updated","roles":sorted(set(cleaned)),"by":frappe.session.user})}).insert(ignore_permissions=True)
    return {"user": user, "roles": sorted(set(cleaned))}


@frappe.whitelist(allow_guest=True)
def get_customer_portal_by_token(token):
    """Return the customer's transaction history through an unguessable QR token."""
    if not token or len(token) < 32:
        frappe.throw(_("Invalid or expired customer access token"), frappe.PermissionError)
    customer_name = frappe.db.get_value("Loyalty Customer", {"qr_access_token": token, "status": "Active"}, "name")
    if not customer_name:
        frappe.throw(_("Invalid or expired customer access token"), frappe.PermissionError)
    customer = frappe.get_doc("Loyalty Customer", customer_name)
    purchases = frappe.db.sql("""SELECT name, purchase_date, petrol_pump, liters, amount, fuel_type, slip_no
        FROM `tabFuel Purchase Entry` WHERE customer = %s AND docstatus = 1
        ORDER BY purchase_date DESC""", (customer.name,), as_dict=True)
    redemptions = frappe.db.sql("""SELECT name, redemption_date, petrol_pump, total_points
        FROM `tabGift Redemption` WHERE customer = %s AND docstatus = 1
        ORDER BY redemption_date DESC""", (customer.name,), as_dict=True)
    for redemption in redemptions:
        redemption["items"] = frappe.db.sql("""SELECT gift_item, item_name, points_required
            FROM `tabGift Redemption Item` WHERE parent = %s ORDER BY idx""", (redemption.name,), as_dict=True)
    mobile = customer.mobile_number or ""
    masked_mobile = ("*" * max(0, len(mobile) - 4) + mobile[-4:]) if mobile else ""
    return {"found": True, "customer": {"name": customer.name, "customer_name": customer.customer_name,
        "mobile_number": masked_mobile, "vehicle_number": customer.vehicle_number,
        "registration_date": str(customer.registration_date or customer.creation),
        "current_cycle_liters": customer.current_cycle_liters, "total_liters_purchased": customer.total_liters_purchased,
        "total_gifts_received": customer.total_gifts_received, "referral_points_balance": customer.referral_points_balance or 0},
        "purchases": [{"purchase_date": str(p.purchase_date), "petrol_pump": p.petrol_pump, "liters": p.liters,
                       "amount": p.amount, "fuel_type": p.fuel_type, "slip_no": p.slip_no} for p in purchases],
        "redemptions": [{"name": r.name, "redemption_date": str(r.redemption_date), "petrol_pump": r.petrol_pump,
                         "total_points": r.total_points, "items": r.items} for r in redemptions]}


@frappe.whitelist()
def get_referral_report(start_datetime=None, end_datetime=None, petrol_pump=None):
    """Referral points report for CLP owners/managers with reporting access."""
    _require_clp_staff({"System Manager", "Pump Owner", "CLM Incharge", "CLP Reports Viewer", "CLP Referral Manager"})
    conditions = ["r.status IN ('Awarded','Reversed')"]
    params = []
    if start_datetime:
        conditions.append("r.reward_date >= %s"); params.append(frappe.utils.get_datetime(start_datetime))
    if end_datetime:
        conditions.append("r.reward_date < %s"); params.append(frappe.utils.get_datetime(end_datetime))
    if start_datetime and end_datetime and frappe.utils.get_datetime(end_datetime) <= frappe.utils.get_datetime(start_datetime):
        frappe.throw(_("End date/time must be after start date/time"))
    if petrol_pump:
        conditions.append("r.petrol_pump = %s"); params.append(petrol_pump)
    return frappe.db.sql(f"""SELECT r.name, r.referrer, ref.customer_name AS referrer_name,
        r.referred_customer, rc.customer_name AS referred_customer_name, r.fuel_purchase_entry,
        r.petrol_pump, r.points_awarded, r.status, r.reward_date
        FROM `tabReferral Reward Entry` r
        LEFT JOIN `tabLoyalty Customer` ref ON ref.name = r.referrer
        LEFT JOIN `tabLoyalty Customer` rc ON rc.name = r.referred_customer
        WHERE {' AND '.join(conditions)} ORDER BY r.reward_date DESC LIMIT 5000""", tuple(params), as_dict=True)
