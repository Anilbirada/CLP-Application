frappe.pages['qr-redirect'].on_page_load = function(wrapper) {
    // Get customer ID from URL parameters
    let urlParams = new URLSearchParams(window.location.search);
    let customer_id = urlParams.get('id');
    
    if (customer_id) {
        frappe.db.exists('Loyalty Customer', customer_id).then(exists => {
            if (exists) {
                // Redirect to existing customer
                frappe.set_route('Form', 'Loyalty Customer', customer_id);
            } else {
                // Show dialog to register new customer
                let d = new frappe.ui.Dialog({
                    title: __('Register New Customer'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            options: `
                                <div style="padding: 20px; text-align: center;">
                                    <div style="font-size: 60px; color: #667eea;">📱</div>
                                    <h3 style="color: #36414C; margin: 20px 0;">Customer ID: <strong>${customer_id}</strong></h3>
                                    <p style="color: #6c757d;">This customer is not registered yet. Would you like to register them now?</p>
                                </div>
                            `
                        }
                    ],
                    primary_action_label: __('Register Customer'),
                    primary_action: function() {
                        d.hide();
                        
                        // Show prompt to get customer details
                        frappe.prompt([
                            {
                                fieldname: 'customer_name',
                                fieldtype: 'Data',
                                label: 'Customer Name',
                                reqd: 1
                            },
                            {
                                fieldname: 'mobile_number',
                                fieldtype: 'Data',
                                label: 'Mobile Number',
                                reqd: 1
                            },
                            {
                                fieldname: 'vehicle_number',
                                fieldtype: 'Data',
                                label: 'Vehicle Number',
                                reqd: 1
                            }
                        ],
                        function(values) {
                            frappe.call({
                                method: 'clp.api.register_customer_with_qr',
                                args: {
                                    qr_code: customer_id,
                                    customer_name: values.customer_name,
                                    mobile_number: values.mobile_number,
                                    vehicle_number: values.vehicle_number
                                },
                                callback: function(r) {
                                    if (r.message) {
                                        frappe.show_alert({
                                            message: __('Customer registered successfully!'),
                                            indicator: 'green'
                                        });
                                        frappe.set_route('Form', 'Loyalty Customer', r.message.name);
                                    }
                                }
                            });
                        },
                        __('Enter Customer Details'),
                        __('Register')
                        );
                    },
                    secondary_action_label: __('Scan Another QR'),
                    secondary_action: function() {
                        d.hide();
                        frappe.set_route('clp-qr-scanner');
                    }
                });
                d.show();
            }
        });
    } else {
        // No ID provided, redirect to scanner
        frappe.set_route('clp-qr-scanner');
    }
}
