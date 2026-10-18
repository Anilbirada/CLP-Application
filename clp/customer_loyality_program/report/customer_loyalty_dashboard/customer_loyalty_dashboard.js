// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Loyalty Dashboard"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nActive\nInactive",
            "default": "Active"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "description": __("Filter by registration date")
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "description": __("Filter by registration date")
        },
        {
            "fieldname": "min_points",
            "label": __("Minimum Points"),
            "fieldtype": "Float",
            "description": __("Show customers with points >= this value (use negative for below zero)")
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Color code current points - BOLD for emphasis
        if (column.fieldname === "current_cycle_liters") {
            let points = data.current_cycle_liters || 0;
            let color, icon;
            
            if (points > 0) {
                color = "#28a745"; // Green
                icon = "🟢";
            } else if (points < 0) {
                color = "#dc3545"; // Red
                icon = "🔴";
            } else {
                color = "#6c757d"; // Gray
                icon = "⚪";
            }
            
            value = `<span style="color: ${color}; font-weight: bold;">${icon} ${points}L</span>`;
        }
        
        // Color code status with badges
        if (column.fieldname === "status") {
            if (data.status === "Active") {
                value = `<span class="badge badge-success" style="font-size: 11px; padding: 4px 8px;">Active</span>`;
            } else {
                value = `<span class="badge badge-secondary" style="font-size: 11px; padding: 4px 8px;">Inactive</span>`;
            }
        }
        
        // Highlight high-value customers (>100L purchased)
        if (column.fieldname === "total_liters_purchased") {
            let purchased = data.total_liters_purchased || 0;
            if (purchased > 100) {
                value = `<span style="color: #667eea; font-weight: bold;">⭐ ${purchased}L</span>`;
            } else if (purchased > 50) {
                value = `<span style="color: #764ba2; font-weight: 600;">${purchased}L</span>`;
            }
        }
        
        // Highlight customers with many gifts
        if (column.fieldname === "total_gifts_received") {
            let gifts = data.total_gifts_received || 0;
            if (gifts > 10) {
                value = `<span style="color: #f093fb; font-weight: bold;">🎁🎁 ${gifts}</span>`;
            } else if (gifts > 5) {
                value = `<span style="color: #f093fb; font-weight: 600;">🎁 ${gifts}</span>`;
            }
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add quick filter buttons
        report.page.add_inner_button(__("Show Negative Balance"), function() {
            frappe.query_report.set_filter_value('min_points', -9999);
            frappe.query_report.set_filter_value('status', '');
            frappe.query_report.refresh();
        }, __("Quick Filters"));
        
        report.page.add_inner_button(__("Show High Value (>50L)"), function() {
            frappe.query_report.set_filter_value('min_points', 50);
            frappe.query_report.refresh();
        }, __("Quick Filters"));
        
        report.page.add_inner_button(__("Show All"), function() {
            frappe.query_report.set_filter_value('min_points', null);
            frappe.query_report.set_filter_value('status', 'Active');
            frappe.query_report.set_filter_value('from_date', null);
            frappe.query_report.set_filter_value('to_date', null);
            frappe.query_report.refresh();
        }, __("Quick Filters"));
        
        // Action buttons
        report.page.add_inner_button(__("New Customer"), function() {
            frappe.new_doc('Loyalty Customer');
        }, __("Actions"));
        
        report.page.add_inner_button(__("Print Report"), function() {
            window.print();
        }, __("Actions"));
        
        report.page.add_inner_button(__("Download Excel"), function() {
            report.export_report();
        }, __("Actions"));
        
        report.page.add_inner_button(__("Refresh Data"), function() {
            frappe.query_report.refresh();
        }, __("Actions"));
        
        // Add custom styling to summary cards
        setTimeout(function() {
            $('.report-summary .summary-value').css({
                'font-size': '24px',
                'font-weight': 'bold'
            });
            
            $('.report-summary .summary-label').css({
                'font-size': '13px',
                'color': '#6c757d'
            });
        }, 500);
    }
};
