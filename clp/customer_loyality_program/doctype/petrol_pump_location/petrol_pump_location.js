// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.ui.form.on('Petrol Pump Location', {
    refresh: function(frm) {
        // Add refresh stock button
        if (!frm.is_new() && frm.doc.warehouse && frm.doc.gift_items) {
            frm.add_custom_button(__('🔄 Refresh Stock'), function() {
                refresh_all_gift_stock(frm);
            });
        }
        
        // Auto-refresh on load
        if (!frm.is_new() && frm.doc.warehouse && frm.doc.gift_items) {
            refresh_all_gift_stock(frm);
        }
    },
    
    warehouse: function(frm) {
        // Refresh stock when warehouse changes
        if (frm.doc.warehouse && frm.doc.gift_items) {
            refresh_all_gift_stock(frm);
        }
    }
});


// Child table events
frappe.ui.form.on('Pump Gift Item', {
    gift_item: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.gift_item && frm.doc.warehouse) {
            // Fetch item name and stock
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Item',
                    filters: {name: row.gift_item},
                    fieldname: 'item_name'
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'item_name', r.message.item_name);
                    }
                }
            });
            
            // Fetch actual stock
            fetch_gift_stock(frm, cdt, cdn, row.gift_item, frm.doc.warehouse);
        }
    },
    
    gift_items_add: function(frm, cdt, cdn) {
        // When new row is added
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'available_stock', 0);
    }
});


function refresh_all_gift_stock(frm) {
    if (!frm.doc.warehouse || !frm.doc.gift_items) {
        return;
    }
    
    frappe.show_alert({
        message: __('Refreshing stock...'),
        indicator: 'blue'
    }, 2);
    
    let updated = 0;
    
    frm.doc.gift_items.forEach(function(item) {
        if (item.gift_item) {
            fetch_gift_stock(frm, item.doctype, item.name, item.gift_item, frm.doc.warehouse)
                .then(() => {
                    updated++;
                    if (updated === frm.doc.gift_items.length) {
                        frappe.show_alert({
                            message: __('Stock updated for {0} items', [updated]),
                            indicator: 'green'
                        }, 3);
                    }
                });
        }
    });
}


function fetch_gift_stock(frm, cdt, cdn, item_code, warehouse) {
    return new Promise((resolve) => {
        frappe.call({
            method: 'clp.api.get_item_stock_at_warehouse',
            args: {
                item_code: item_code,
                warehouse: warehouse
            },
            callback: function(r) {
                if (r.message !== undefined) {
                    frappe.model.set_value(cdt, cdn, 'available_stock', r.message);
                    frm.refresh_field('gift_items');
                }
                resolve();
            }
        });
    });
}
