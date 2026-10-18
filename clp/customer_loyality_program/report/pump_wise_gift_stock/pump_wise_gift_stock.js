// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Pump-wise Gift Stock"] = {
    "filters": [
        {
            "fieldname": "petrol_pump",
            "label": __("Petrol Pump"),
            "fieldtype": "Link",
            "options": "Petrol Pump Location"
        },
        {
            "fieldname": "gift_item",
            "label": __("Gift Item"),
            "fieldtype": "Link",
            "options": "Item"
        },
        {
            "fieldname": "show_zero_stock",
            "label": __("Show Zero Stock"),
            "fieldtype": "Check",
            "default": 0
        }
    ],
    
    "onload": function(report) {
        // Add Print button
        report.page.add_inner_button(__("Print"), function() {
            print_report(report);
        }, __("Actions"));
        
        // Add Download PDF button
        report.page.add_inner_button(__("Download PDF"), function() {
            download_pdf(report);
        }, __("Actions"));
        
        // Add Download Excel button
        report.page.add_inner_button(__("Download Excel"), function() {
            download_excel(report);
        }, __("Actions"));
    }
};

function print_report(report) {
    // Get report HTML and print
    let print_settings = frappe.model.get_doc(":Print Settings", "Print Settings");
    let landscape = print_settings ? print_settings.landscape : 1;
    
    frappe.render_grid({
        grid_data: report.data,
        columns: report.columns,
        title: report.report_name
    }, function(html) {
        frappe.render_template("print_template", {
            title: report.report_name,
            html_content: html
        });
    });
    
    window.print();
}

function download_pdf(report) {
    let filters = report.get_values();
    let filter_string = get_filter_string(filters);
    
    window.open(
        `/api/method/frappe.utils.print_format.download_pdf?` +
        `doctype=${encodeURIComponent(report.report_doc.ref_doctype)}&` +
        `name=${encodeURIComponent(report.report_name)}&` +
        `format=Standard&` +
        `no_letterhead=0&` +
        `letterhead=&` +
        `settings={}&` +
        `_lang=en${filter_string}`,
        '_blank'
    );
}

function download_excel(report) {
    // Use built-in export functionality
    report.export_report();
}

function get_filter_string(filters) {
    let str = '';
    for (let key in filters) {
        if (filters[key]) {
            str += `&${key}=${encodeURIComponent(filters[key])}`;
        }
    }
    return str;
}
