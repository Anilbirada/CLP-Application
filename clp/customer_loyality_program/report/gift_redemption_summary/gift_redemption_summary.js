// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Gift Redemption Summary"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1
        },
        {
            "fieldname": "petrol_pump",
            "label": __("Petrol Pump"),
            "fieldtype": "Link",
            "options": "Petrol Pump Location"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Loyalty Customer",
            "get_query": function() {
                return {
                    query: "clp.customer_loyality_program.report.gift_redemption_summary.gift_redemption_summary.get_customers"
                };
            }
        },
        {
            "fieldname": "gift_item",
            "label": __("Gift Item"),
            "fieldtype": "Link",
            "options": "Item"
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Highlight rows with negative balance indicators
        if (column.fieldname === "points_required" && data.points_required > 0) {
            value = `<span style="color: #dc3545; font-weight: bold;">${data.points_required}L</span>`;
        }
        
        // Color code total points
        if (column.fieldname === "total_points" && data.total_points) {
            let color = data.total_points >= 0 ? "#28a745" : "#dc3545";
            value = `<span style="color: ${color}; font-weight: bold;">${data.total_points}L</span>`;
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add Print button
        report.page.add_inner_button(__("Print"), function() {
            window.print();
        }, __("Actions"));
        
        // Add Download Excel button
        report.page.add_inner_button(__("Download Excel"), function() {
            report.export_report();
        }, __("Actions"));
        
        // Add custom summary cards styling
        setTimeout(function() {
            $('.report-summary .summary-value').css({
                'font-size': '24px',
                'font-weight': 'bold'
            });
        }, 500);
    }
};
