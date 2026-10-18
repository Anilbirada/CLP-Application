// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fuel Purchase Entry', {
    setup: function(frm) {
        // Enhanced search for customer field
        frm.set_query('customer', function() {
            return {
                query: 'clp.api.get_customers_for_search'
            };
        });
    },
    
    onload: function(frm) {
        // Auto-fill pump from user settings on NEW form only
        if (frm.is_new() && !frm.doc.petrol_pump) {
            frappe.call({
                method: 'clp.api.get_user_default_pump',
                callback: function(r) {
                    if (r.message && r.message.default_pump) {
                        frm.set_value('petrol_pump', r.message.default_pump);
                        frappe.show_alert({
                            message: __('Default pump loaded: {0}', [r.message.default_pump]),
                            indicator: 'green'
                        }, 3);
                    }
                }
            });
        }
    },
    
    refresh: function(frm) {
        // Clear existing custom buttons
        frm.clear_custom_buttons();
        
        // QR Scanner button - only on new forms
        if (frm.is_new()) {
            frm.add_custom_button(__('📷 Scan QR'), function() {
                scan_customer_qr(frm);
            }).css({
                'background-color': '#17a2b8',
                'color': 'white',
                'font-weight': 'bold'
            });
        }
        
        // WhatsApp button - ALWAYS show if customer exists
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
        
        // Show customer info card
        if (frm.doc.customer) {
            show_customer_info(frm);
        }
        
        // Show pump stock indicator
        if (frm.doc.petrol_pump && !frm.is_new()) {
            show_pump_stock(frm);
        }

        // Feature 2 & 5: Bottom Save button & streamlined refuel workflow
        render_bottom_save_button(frm);
    },
    
    customer: function(frm) {
        if (frm.doc.customer) {
            show_customer_info(frm);
            frm.trigger('refresh'); // Refresh to show WhatsApp button
        }
    },
    
    petrol_pump: function(frm) {
        if (frm.doc.petrol_pump && !frm.is_new()) {
            show_pump_stock(frm);
        }
    }
});


function scan_customer_qr(frm) {
    new frappe.ui.Scanner({
        dialog: true,
        multiple: false,
        on_scan(data) {
            let scanned_text = data.decodedText;
            
            // Extract customer ID from URL if needed
            let customer_id = scanned_text;
            
            // Check if scanned data is a URL
            if (scanned_text.includes('qr-redirect?id=') || scanned_text.includes('qr-redirect&id=')) {
                try {
                    const url = new URL(scanned_text);
                    const id_param = url.searchParams.get('id');
                    if (id_param) {
                        customer_id = id_param;
                    }
                } catch (e) {
                    const match = scanned_text.match(/[?&]id=([^&]+)/);
                    if (match && match[1]) {
                        customer_id = match[1];
                    }
                }
            }
            
            // Check if customer exists
            frappe.call({
                method: 'clp.api.scan_and_process_qr',
                args: { qr_data: customer_id },
                callback: function(r) {
                    if (r.message && r.message.exists) {
                        frm.set_value('customer', customer_id);
                        frappe.show_alert({
                            message: __('✅ Customer loaded: {0}', [r.message.customer_name]),
                            indicator: 'green'
                        }, 5);
                    } else {
                        // Customer not found - offer to register
                        frappe.confirm(
                            __('Customer ID <strong>{0}</strong> not found.<br><br>Would you like to register this customer?', [customer_id]),
                            function() {
                                // Yes - open registration
                                frappe.set_route('Form', 'Loyalty Customer', customer_id);
                            },
                            function() {
                                // No - do nothing
                                frappe.msgprint(__('Please register the customer first'));
                            }
                        );
                    }
                }
            });
        }
    });
}


function show_customer_info(frm) {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Loyalty Customer',
            name: frm.doc.customer
        },
        callback: function(r) {
            if (r.message) {
                let c = r.message;
                
                let balance_color = c.current_cycle_liters >= 0 ? '#ffd700' : '#ff4444';
                
                let html = `
                    <div class="customer-info-card" style="padding:15px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border-radius:10px;margin:10px 0;box-shadow:0 4px 12px rgba(0,0,0,0.15);">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
                            <div style="flex:1;min-width:200px;">
                                <h4 style="margin:0 0 8px 0;color:white;font-size:18px;">
                                    <i class="fa fa-user-circle"></i> ${c.customer_name}
                                </h4>
                                <div style="font-size:13px;line-height:1.6;">
                                    <div><i class="fa fa-id-card"></i> ID: <strong>${c.name}</strong></div>
                                    <div><i class="fa fa-car"></i> Vehicle: <strong>${c.vehicle_number}</strong></div>
                                    <div><i class="fa fa-phone"></i> Mobile: <strong>${c.mobile_number}</strong></div>
                                    <div><i class="fa fa-gift"></i> Total Gifts: <strong>${c.total_gifts_received}</strong></div>
                                </div>
                            </div>
                            <div style="text-align:center;padding:15px 20px;background:rgba(255,255,255,0.2);border-radius:10px;margin-top:10px;">
                                <div style="font-size:36px;font-weight:bold;color:${balance_color};line-height:1;">
                                    ${c.current_cycle_liters}
                                </div>
                                <div style="font-size:13px;margin-top:5px;font-weight:500;">
                                    Loyalty Points (L)
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                frm.get_field('customer').$wrapper.find('.customer-info-card').remove();
                frm.get_field('customer').$wrapper.append(html);
            }
        },
        error: function() {
            frappe.msgprint(__('Failed to load customer details'));
        }
    });
}


function show_pump_stock(frm) {
    frappe.call({
        method: 'clp.api.get_pump_gift_stock',
        args: {
            petrol_pump: frm.doc.petrol_pump
        },
        callback: function(r) {
            if (r.message) {
                let stock = r.message;
                let color = stock.qty > 10 ? 'green' : stock.qty > 0 ? 'orange' : 'red';
                frm.dashboard.add_indicator(
                    __('Gift Stock at {0}: {1} units', [stock.pump_name, stock.qty]),
                    color
                );
            }
        }
    });
}


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
            frappe.msgprint({
                title: __('Error'),
                message: __('Failed to generate WhatsApp link'),
                indicator: 'red'
            });
        }
    });
}


function render_bottom_save_button(frm) {
    if (!frm.layout || !frm.layout.wrapper) return;
    frm.layout.wrapper.find('.clp-bottom-save-container').remove();
    if (frm.doc.docstatus !== 0) return;

    const container = $(`
        <div class="clp-bottom-save-container" style="margin-top: 25px; margin-bottom: 25px; padding: 18px; background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 10px; text-align: center;">
            <div style="margin-bottom: 8px; color: #64748b; font-size: 13px;">
                ⚡ <strong>Quick Attendant Action:</strong> Save & submit in 1-click
            </div>
            <button type="button" class="btn btn-primary btn-lg clp-btn-bottom-save" style="min-width: 260px; font-size: 16px; font-weight: 600; padding: 10px 24px; box-shadow: 0 4px 6px rgba(37,99,235,0.2);">
                💾 Save & Submit Purchase
            </button>
            <button type="button" class="btn btn-secondary btn-lg clp-btn-next-customer" style="margin-left: 12px; font-size: 15px; padding: 10px 20px;">
                ➕ Next Refuel
            </button>
        </div>
    `);

    container.find('.clp-btn-bottom-save').on('click', function() {
        if (!frm.doc.customer) {
            frappe.msgprint(__('Please select or scan a Customer ID first.'));
            return;
        }
        if (!frm.doc.petrol_pump) {
            frappe.msgprint(__('Please select a Petrol Pump Location.'));
            return;
        }
        if (!frm.doc.liters || frm.doc.liters <= 0) {
            frappe.msgprint(__('Please enter valid refuel Liters (greater than 0).'));
            return;
        }
        frm.savesubmit();
    });

    container.find('.clp-btn-next-customer').on('click', function() {
        frappe.new_doc('Fuel Purchase Entry');
    });

    frm.layout.wrapper.find('.form-layout').append(container);
}

