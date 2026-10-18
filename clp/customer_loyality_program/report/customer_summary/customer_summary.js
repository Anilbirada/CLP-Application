// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Summary"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Loyalty Customer",
            "reqd": 1,
            "get_query": function() {
                return {
                    query: "clp.customer_loyality_program.report.customer_summary.customer_summary.get_customers"
                };
            }
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "transaction_type",
            "label": __("Transaction Type"),
            "fieldtype": "Select",
            "options": "\nFuel Purchase\nGift Redemption",
            "default": ""
        },
        {
            "fieldname": "petrol_pump",
            "label": __("Petrol Pump"),
            "fieldtype": "Link",
            "options": "Petrol Pump Location"
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Color code transaction types
        if (column.fieldname === "transaction_type") {
            if (data.transaction_type === "Fuel Purchase") {
                value = `<span class="badge badge-primary" style="font-size: 11px;">⛽ Fuel Purchase</span>`;
            } else if (data.transaction_type === "Gift Redemption") {
                value = `<span class="badge badge-danger" style="font-size: 11px;">🎁 Gift Redemption</span>`;
            }
        }
        
        // Color code points change
        if (column.fieldname === "points_change") {
            let points = data.points_change || 0;
            if (points > 0) {
                value = `<span style="color: #28a745; font-weight: bold;">+${points}L</span>`;
            } else if (points < 0) {
                value = `<span style="color: #dc3545; font-weight: bold;">${points}L</span>`;
            } else {
                value = `<span style="color: #6c757d;">0L</span>`;
            }
        }
        
        // Color code running balance
        if (column.fieldname === "running_balance") {
            let balance = data.running_balance || 0;
            let color = balance >= 0 ? "#28a745" : "#dc3545";
            value = `<span style="color: ${color}; font-weight: bold;">${balance}L</span>`;
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add action buttons
        report.page.add_inner_button(__("New Fuel Entry"), function() {
            let customer = frappe.query_report.get_filter_value('customer');
            if (customer) {
                frappe.new_doc('Fuel Purchase Entry', {customer: customer});
            } else {
                frappe.new_doc('Fuel Purchase Entry');
            }
        }, __("Actions"));
        
        report.page.add_inner_button(__("New Gift Redemption"), function() {
            let customer = frappe.query_report.get_filter_value('customer');
            if (customer) {
                frappe.new_doc('Gift Redemption', {customer: customer});
            } else {
                frappe.new_doc('Gift Redemption');
            }
        }, __("Actions"));
        
        report.page.add_inner_button(__("Print"), function() {
            window.print();
        }, __("Actions"));
        
        report.page.add_inner_button(__("Download Excel"), function() {
            report.export_report();
        }, __("Actions"));
        
        // Style summary cards
        setTimeout(function() {
            $('.report-summary .summary-value').css({
                'font-size': '24px',
                'font-weight': 'bold'
            });
        }, 500);
    }
};
