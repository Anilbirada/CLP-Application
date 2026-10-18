// Copyright (c) 2025, Aman Boora and contributors
// For license information, please see license.txt

frappe.ui.form.on('Loyalty Customer', {
    refresh: function(frm) {
        // Add QR code button for existing records
        if (!frm.is_new()) {
            frm.add_custom_button(__('Generate QR Code'), function() {
                frappe.call({
                    method: 'clp.api.generate_qr_image',
                    args: {
                        customer_id: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            let d = new frappe.ui.Dialog({
                                title: `QR Code - ${frm.doc.customer_name}`,
                                fields: [
                                    {
                                        fieldtype: 'HTML',
                                        fieldname: 'qr_display'
                                    }
                                ],
                                primary_action_label: __('Print'),
                                primary_action: function() {
                                    window.print();
                                }
                            });
                            
                            d.fields_dict.qr_display.$wrapper.html(`
                                <div style="text-align: center; padding: 20px;">
                                    <img src="${r.message.image}" style="max-width: 300px; border: 2px solid #ddd;"/>
                                    <p style="margin-top: 15px;"><strong>Customer ID: ${frm.doc.name}</strong></p>
                                    <p><strong>${frm.doc.customer_name}</strong></p>
                                    <p>Vehicle: ${frm.doc.vehicle_number}</p>
                                    <p>Mobile: ${frm.doc.mobile_number}</p>
                                    <p style="margin-top: 15px; font-size: 12px; color: #666;">
                                        Scan to check loyalty points
                                    </p>
                                </div>
                            `);
                            
                            d.show();
                        }
                    }
                });
            }, __('Actions'));
            
            // Add customer portal link button
            frm.add_custom_button(__('Customer Portal Link'), function() {
                let portal_url = `${window.location.origin}/loyalty/check?vehicle=${encodeURIComponent(frm.doc.vehicle_number)}&mobile=${encodeURIComponent(frm.doc.mobile_number)}`;
                
                let d = new frappe.ui.Dialog({
                    title: __('Customer Portal Link'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'link_display'
                        }
                    ]
                });
                
                d.fields_dict.link_display.$wrapper.html(`
                    <div style="padding: 20px;">
                        <p style="margin-bottom: 15px;">Share this link with customer to check their points:</p>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; word-break: break-all;">
                            <a href="${portal_url}" target="_blank">${portal_url}</a>
                        </div>
                        <button class="btn btn-primary btn-sm" style="margin-top: 15px;" onclick="navigator.clipboard.writeText('${portal_url}'); frappe.show_alert('Link copied!');">
                            <i class="fa fa-copy"></i> Copy Link
                        </button>
                    </div>
                `);
                
                d.show();
            }, __('Actions'));

            // Feature 18: Owner can add/subtract user notes or balances
            if (frappe.user.has_role('Pump Owner') || frappe.user.has_role('System Manager') || frappe.user.has_role('CLM Incharge')) {
                frm.add_custom_button(__('⚖️ Adjust Points / Notes'), function() {
                    frappe.new_doc('CLP Customer Balance Adjustment', {
                        customer: frm.doc.name
                    });
                }, __('Actions'));
            }

            
            // Show customer summary in dashboard
            if (frm.doc.current_cycle_liters > 0) {
                frm.dashboard.add_indicator(
                    __(`${frm.doc.current_cycle_liters}L Points Available`), 
                    'blue'
                );
            }
            
            if (frm.doc.total_gifts_received > 0) {
                frm.dashboard.add_indicator(
                    __(`${frm.doc.total_gifts_received} Gifts Redeemed`), 
                    'green'
                );
            }
        }
    },
    
    vehicle_number: function(frm) {
        // Auto-uppercase vehicle number
        if (frm.doc.vehicle_number) {
            frm.set_value('vehicle_number', frm.doc.vehicle_number.toUpperCase());
        }
    }
});
