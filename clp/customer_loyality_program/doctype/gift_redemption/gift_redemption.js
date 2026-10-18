// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gift Redemption', {
    setup: function(frm) {
        // Customer search
        frm.set_query('customer', function() {
            return {
                query: 'clp.api.get_customers_for_search'
            };
        });
        
        // Filter gifts by pump ONLY
        frm.set_query('gift_item', 'items', function(doc) {
            if (!doc.petrol_pump) {
                frappe.msgprint(__('Please select Petrol Pump first'));
                return { filters: { 'name': ['=', ''] } };
            }
            return {
                query: 'clp.api.get_pump_gift_items',
                filters: { 'petrol_pump': doc.petrol_pump }
            };
        });
    },
    
    onload: function(frm) {
        // Auto-fill pump on new form only
        if (frm.is_new() && !frm.doc.petrol_pump) {
            frappe.call({
                method: 'clp.api.get_user_default_pump',
                callback: function(r) {
                    if (r.message && r.message.default_pump) {
                        frm.set_value('petrol_pump', r.message.default_pump);
                        if (r.message.default_warehouse) {
                            frm.set_value('warehouse', r.message.default_warehouse);
                        }
                    }
                }
            });
        }
    },
    
    refresh: function(frm) {
        // Remove any existing buttons first
        frm.clear_custom_buttons();
        
        // Show customer card ONLY if customer exists AND doc is draft or cancelled
        if (frm.doc.customer && frm.doc.docstatus !== 1) {
            load_customer_details(frm);
        }
        
        // WhatsApp button - GREEN, visible if customer exists
        if (frm.doc.customer) {
            frm.add_custom_button(__('📱 WhatsApp'), function() {
                send_whatsapp(frm);
            }).css({
                'background-color': '#25D366',
                'color': 'white',
                'font-weight': 'bold',
                'border': 'none'
            });
        }
        
        // Add Gifts button - only on draft with pump and customer
        if (frm.doc.petrol_pump && frm.doc.customer && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('🎁 Add Gifts'), function() {
                show_gifts_dialog(frm);
            }).css({
                'background-color': '#28a745',
                'color': 'white'
            });
        }
        
        // View buttons - only on submitted
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('View Customer'), function() {
                frappe.set_route('Form', 'Loyalty Customer', frm.doc.customer);
            });
            
            if (frm.doc.stock_entry) {
                frm.add_custom_button(__('View Stock Entry'), function() {
                    frappe.set_route('Form', 'Stock Entry', frm.doc.stock_entry);
                });
            }
        }
        
        // Calculate total ONLY if draft
        if (frm.doc.docstatus === 0) {
            calculate_total(frm);
        }
    },
    
    customer: function(frm) {
        // Only load details if draft
        if (frm.doc.customer && frm.doc.docstatus === 0) {
            load_customer_details(frm);
        }
    },
    
    petrol_pump: function(frm) {
        // Only update warehouse if draft
        if (frm.doc.petrol_pump && frm.doc.docstatus === 0) {
            frappe.db.get_value('Petrol Pump Location', frm.doc.petrol_pump, 'warehouse', function(r) {
                if (r && r.warehouse) {
                    frm.set_value('warehouse', r.warehouse);
                }
            });
        }
    }
});


// Child table events
frappe.ui.form.on('Gift Redemption Item', {
    gift_item: function(frm, cdt, cdn) {
        // Only process if draft
        if (frm.doc.docstatus !== 0) {
            return;
        }
        
        let row = locals[cdt][cdn];
        
        if (row.gift_item && frm.doc.petrol_pump) {
            frappe.call({
                method: 'clp.api.get_gift_item_details',
                args: {
                    petrol_pump: frm.doc.petrol_pump,
                    gift_item: row.gift_item
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'item_name', r.message.item_name);
                        frappe.model.set_value(cdt, cdn, 'points_required', r.message.points_required);
                        frappe.model.set_value(cdt, cdn, 'available_stock', r.message.available_stock);
                        frappe.model.set_value(cdt, cdn, 'stock_after_redeem', r.message.available_stock - 1);
                        calculate_total(frm);
                    }
                }
            });
        }
    },
    
    items_remove: function(frm) {
        if (frm.doc.docstatus === 0) {
            calculate_total(frm);
        }
    }
});


// Helper functions
function calculate_total(frm) {
    // NEVER modify fields if document is submitted
    if (frm.doc.docstatus !== 0) {
        return;
    }
    
    let total = 0;
    if (frm.doc.items) {
        frm.doc.items.forEach(item => total += (item.points_required || 0));
    }
    frm.set_value('total_points', total);
    
    if (frm.doc.liters_accumulated && total > frm.doc.liters_accumulated) {
        let negative = total - frm.doc.liters_accumulated;
        frm.dashboard.set_headline_alert(
            `⚠️ Points exceed available by ${negative}L. Balance will be negative.`,
            'orange'
        );
    } else {
        frm.dashboard.clear_headline();
    }
}


function load_customer_details(frm) {
    // NEVER modify fields if document is submitted
    if (frm.doc.docstatus !== 0) {
        return;
    }
    
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Loyalty Customer',
            name: frm.doc.customer
        },
        callback: function(r) {
            if (r.message) {
                let c = r.message;
                frm.set_value('liters_accumulated', c.current_cycle_liters);
                
                let balance_color = c.current_cycle_liters >= 0 ? '#ffd700' : '#ff4444';
                
                let html = `
                    <div class="customer-card-display" style="padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:10px;margin:10px 0;">
                        <h4 style="margin:0;color:white;">${c.customer_name}</h4>
                        <div style="margin-top:8px;font-size:13px;">
                            ID: ${c.name} | Vehicle: ${c.vehicle_number} | Mobile: ${c.mobile_number}
                        </div>
                        <div style="margin-top:10px;font-size:32px;font-weight:bold;color:${balance_color};">
                            ${c.current_cycle_liters}L <span style="font-size:14px;">Points</span>
                        </div>
                    </div>
                `;
                
                frm.get_field('customer').$wrapper.find('.customer-card-display').remove();
                frm.get_field('customer').$wrapper.append(html);
            }
        }
    });
}


function show_gifts_dialog(frm) {
    frappe.call({
        method: 'clp.api.get_available_gifts',
        args: { petrol_pump: frm.doc.petrol_pump },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;">';
                
                r.message.forEach(gift => {
                    let stock_ok = gift.available_stock > 0;
                    html += `
                        <div style="padding:12px;border:2px solid ${stock_ok ? '#28a745' : '#dc3545'};border-radius:8px;cursor:${stock_ok ? 'pointer' : 'not-allowed'};"
                             onclick="${stock_ok ? `add_gift('${gift.gift_item}', '${gift.item_name}', ${gift.points_required}, ${gift.available_stock})` : ''}">
                            <div style="font-weight:600;margin-bottom:8px;">${gift.item_name}</div>
                            <div><span class="badge badge-primary">${gift.points_required}L</span></div>
                            <div style="margin-top:5px;font-size:12px;color:${stock_ok ? '#28a745' : '#dc3545'};">
                                Stock: ${gift.available_stock}
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                
                let d = new frappe.ui.Dialog({
                    title: 'Select Gifts',
                    fields: [{ fieldtype: 'HTML', options: html }],
                    size: 'large'
                });
                d.show();
            } else {
                frappe.msgprint(__('No gifts configured for this pump'));
            }
        }
    });
}


window.add_gift = function(gift_item, item_name, points, stock) {
    let frm = cur_frm;
    
    // Only allow if draft
    if (frm.doc.docstatus !== 0) {
        frappe.msgprint(__('Cannot modify submitted document'));
        return;
    }
    
    let exists = false;
    if (frm.doc.items) {
        frm.doc.items.forEach(item => {
            if (item.gift_item === gift_item) exists = true;
        });
    }
    
    if (exists) {
        frappe.show_alert({message: 'Already added', indicator: 'orange'}, 2);
        return;
    }
    
    let row = frm.add_child('items');
    row.gift_item = gift_item;
    row.item_name = item_name;
    row.points_required = points;
    row.available_stock = stock;
    row.stock_after_redeem = stock - 1;
    frm.refresh_field('items');
    calculate_total(frm);
    frappe.show_alert({message: '✅ Gift added', indicator: 'green'}, 2);
};


function send_whatsapp(frm) {
    if (!frm.doc.customer) {
        frappe.msgprint(__('No customer selected'));
        return;
    }
    
    let pump_name = frm.doc.pump_name || 'our pump';
    
    frappe.call({
        method: 'clp.api.get_whatsapp_link',
        args: {
            customer_id: frm.doc.customer,
            pump_name: pump_name
        },
        freeze: true,
        freeze_message: __('Generating WhatsApp link...'),
        callback: function(r) {
            if (r.message && r.message.url) {
                window.open(r.message.url, '_blank');
                frappe.show_alert({
                    message: __('📱 WhatsApp opened for {0}', [r.message.customer_name]),
                    indicator: 'green'
                }, 5);
            }
        },
        error: function() {
            frappe.msgprint(__('Failed to generate WhatsApp link'));
        }
    });
}
