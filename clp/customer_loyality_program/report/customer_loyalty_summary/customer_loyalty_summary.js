// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Loyalty Summary"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nActive\nInactive",
            "default": "Active"
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Color code current points - RED for negative, GREEN for positive
        if (column.fieldname === "current_cycle_liters") {
            let points = data.current_cycle_liters || 0;
            let color = points >= 0 ? "#28a745" : "#dc3545";
            let icon = points >= 0 ? "✓" : "⚠";
            value = `<span style="color: ${color}; font-weight: bold;">${icon} ${points}L</span>`;
        }
        
        // Color code status
        if (column.fieldname === "status") {
            if (data.status === "Active") {
                value = `<span class="badge badge-success">Active</span>`;
            } else {
                value = `<span class="badge badge-secondary">Inactive</span>`;
            }
        }
        
        // Highlight high-value customers (>50L purchased)
        if (column.fieldname === "total_liters_purchased" && data.total_liters_purchased > 50) {
            value = `<span style="color: #667eea; font-weight: bold;">🌟 ${data.total_liters_purchased}L</span>`;
        }
        
        // Highlight customers with many gifts
        if (column.fieldname === "total_gifts_received" && data.total_gifts_received > 5) {
            value = `<span style="color: #f093fb; font-weight: bold;">🎁 ${data.total_gifts_received}</span>`;
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add Create New Customer button
        report.page.add_inner_button(__("New Customer"), function() {
            frappe.new_doc('Loyalty Customer');
        }, __("Actions"));
        
        // Add Print button
        report.page.add_inner_button(__("Print"), function() {
            window.print();
        }, __("Actions"));
        
        // Add Export to Excel
        report.page.add_inner_button(__("Download Excel"), function() {
            report.export_report();
        }, __("Actions"));
        
        // Add WhatsApp Bulk Message button
        report.page.add_inner_button(__("Send Bulk WhatsApp"), function() {
            send_bulk_whatsapp(report);
        }, __("Actions"));
    }
};


function send_bulk_whatsapp(report) {
    let data = report.data;
    
    if (!data || data.length === 0) {
        frappe.msgprint(__('No customers in the report'));
        return;
    }
    
    frappe.confirm(
        __('Send WhatsApp message to {0} customers?', [data.length]),
        function() {
            frappe.msgprint({
                title: __('Bulk WhatsApp'),
                message: __('Feature coming soon! Contact support for bulk messaging.'),
                indicator: 'blue'
            });
        }
    );
}
