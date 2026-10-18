// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gift Stock Request', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status === "Approved" && !frm.doc.stock_entry) {
            frm.add_custom_button(__('Create Stock Entry'), function() {
                frappe.call({
                    method: 'create_stock_entry',
                    doc: frm.doc,
                    callback: function(r) {
                        frm.reload_doc();
                    }
                });
            }).css({'background-color': '#28a745', 'color': 'white'});
        }
        
        if (frm.doc.stock_entry) {
            frm.add_custom_button(__('View Stock Entry'), function() {
                frappe.set_route('Form', 'Stock Entry', frm.doc.stock_entry);
            });
        }
        
        // Add approve/reject buttons
        if (frm.doc.docstatus === 0 && frm.doc.status === "Pending") {
            frm.add_custom_button(__('Approve'), function() {
                frm.set_value('status', 'Approved');
                frm.save();
            }).css({'background-color': '#28a745', 'color': 'white'});
            
            frm.add_custom_button(__('Reject'), function() {
                frm.set_value('status', 'Rejected');
                frm.save();
            }).css({'background-color': '#dc3545', 'color': 'white'});
        }
    },
    
    requesting_pump: function(frm) {
        update_stock_levels(frm);
    },
    
    source_pump: function(frm) {
        update_stock_levels(frm);
    },
    
    gift_item: function(frm) {
        update_stock_levels(frm);
    },
    
    before_submit: function(frm) {
        if (frm.doc.status !== "Approved") {
            frappe.throw(__("Only approved requests can be submitted"));
        }
    }
});

function update_stock_levels(frm) {
    if (frm.doc.source_warehouse && frm.doc.gift_item) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Bin',
                filters: {
                    item_code: frm.doc.gift_item,
                    warehouse: frm.doc.source_warehouse
                },
                fieldname: 'actual_qty'
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value('available_stock', r.message.actual_qty || 0);
                }
            }
        });
    }
    
    if (frm.doc.requesting_warehouse && frm.doc.gift_item) {
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Bin',
                filters: {
                    item_code: frm.doc.gift_item,
                    warehouse: frm.doc.requesting_warehouse
                },
                fieldname: 'actual_qty'
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value('current_stock_requesting', r.message.actual_qty || 0);
                }
            }
        });
    }
}
