frappe.pages['clp-qr-scanner'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Quick QR Scanner',
        single_column: true
    });


    let html = `
        <style>
            .qr-scanner-page {
                padding: 20px;
                max-width: 100%;
            }
            
            @media (min-width: 768px) {
                .qr-scanner-page {
                    padding: 30px;
                }
            }
            
            .scanner-container {
                max-width: 900px;
                margin: 0 auto;
                width: 100%;
            }
            
            .qr-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                color: white;
                text-align: center;
            }
            
            @media (min-width: 768px) {
                .qr-header {
                    padding: 40px;
                }
            }
            
            .qr-header h1 {
                margin: 0 0 10px 0;
                color: white;
                font-size: 24px;
            }
            
            @media (min-width: 768px) {
                .qr-header h1 {
                    font-size: 32px;
                }
            }
            
            .customer-card {
                margin-bottom: 15px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s;
                background: white;
                overflow: hidden;
            }
            
            .customer-card:hover {
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
                transform: translateY(-2px);
            }
            
            .customer-card-body {
                padding: 15px;
            }
            
            @media (min-width: 768px) {
                .customer-card-body {
                    padding: 20px;
                }
            }
            
            .customer-card-content {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            @media (min-width: 768px) {
                .customer-card-content {
                    flex-direction: row;
                    justify-content: space-between;
                    align-items: center;
                }
            }
            
            .customer-info h5 {
                margin: 0 0 5px 0;
                color: #2c3e50;
                font-size: 16px;
                font-weight: 600;
            }
            
            @media (min-width: 768px) {
                .customer-info h5 {
                    font-size: 18px;
                }
            }
            
            .customer-info small {
                color: #6c757d;
                font-size: 12px;
            }
            
            @media (min-width: 768px) {
                .customer-info small {
                    font-size: 14px;
                }
            }
            
            .customer-stats {
                text-align: right;
            }
            
            .customer-stats h4 {
                margin: 0;
                color: #667eea;
                font-size: 20px;
                font-weight: bold;
            }
            
            @media (min-width: 768px) {
                .customer-stats h4 {
                    font-size: 24px;
                }
            }
            
            .customer-stats small {
                color: #6c757d;
                font-size: 12px;
            }
            
            .section-title {
                border-bottom: 3px solid #667eea;
                padding-bottom: 15px;
                margin-bottom: 25px;
                color: #36414C;
                font-size: 18px;
            }
            
            @media (min-width: 768px) {
                .section-title {
                    font-size: 20px;
                }
            }
            
            .scan-result-success {
                background: white;
                border: 2px solid #28a745;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
                text-align: left;
            }
            
            .scan-result-warning {
                background: white;
                border: 2px solid #ff9800;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
            }
            
            .result-table {
                width: 100%;
                margin-bottom: 20px;
            }
            
            .result-table td {
                padding: 8px;
                color: #2c3e50;
            }
            
            .result-table td:first-child {
                font-weight: 600;
                width: 40%;
            }
            
            @media (min-width: 768px) {
                .result-table td:first-child {
                    width: 30%;
                }
            }
            
            .btn-quick-sale {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 18px;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.3s;
                margin-left: 10px;
            }
            
            .btn-quick-sale:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(240, 147, 251, 0.3);
            }
        </style>
        
        <div class="qr-scanner-page">
            <div class="scanner-container">
                <div class="qr-header">
                    <h1><i class="fa fa-qrcode"></i> QR Scanner</h1>
                    <p style="margin: 0; font-size: 16px;">Scan customer QR code or search customer</p>
                </div>
                
                <div style="text-align: center; margin-bottom: 40px;">
                    <button class="btn btn-primary btn-lg" id="start-scanner" 
                            style="padding: 15px 40px; font-size: 18px; border-radius: 10px; margin-right: 10px; margin-bottom: 10px;">
                        <i class="fa fa-camera"></i> Scan QR
                    </button>
                    <button class="btn btn-success btn-lg" id="search-customer" 
                            style="padding: 15px 40px; font-size: 18px; border-radius: 10px; margin-right: 10px; margin-bottom: 10px;">
                        <i class="fa fa-search"></i> Search
                    </button>
                    <button class="btn-quick-sale btn-lg" id="quick-sale">
                        <i class="fa fa-bolt"></i> Quick Sale
                    </button>
                </div>
                
                <div id="scan-result" style="margin-bottom: 40px;"></div>
                
                <div id="recent-customers">
                    <h3 class="section-title">
                        <i class="fa fa-history"></i> Recent Customers
                    </h3>
                    <div id="customer-list"></div>
                </div>
            </div>
        </div>
    `;


    $(page.body).html(html);


    $('#start-scanner').click(function() {
        start_qr_scanner();
    });


    $('#search-customer').click(function() {
        search_customer();
    });


    $('#quick-sale').click(function() {
        quick_sale();
    });


    load_recent_customers();


    function start_qr_scanner() {
        new frappe.ui.Scanner({
            dialog: true,
            multiple: false,
            on_scan(data) {
                let scanned_text = data.decodedText;
                process_scanned_qr(scanned_text);
            }
        });
    }


    function search_customer() {
        frappe.prompt([
            {
                fieldname: 'search_text',
                fieldtype: 'Data',
                label: 'Search (ID, Name, Vehicle, Mobile)',
                reqd: 1,
                description: 'Enter any part of the customer details'
            }
        ],
        function(values) {
            frappe.call({
                method: 'clp.api.search_customer_for_scanner',
                args: {
                    search_text: values.search_text
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        show_customer_list_with_actions(r.message);
                    } else {
                        frappe.msgprint(__('No customers found'));
                    }
                }
            });
        },
        __('Search Customer'),
        __('Search')
        );
    }


    function quick_sale() {
    // First, fetch user's default pump
        frappe.call({
            method: 'clp.api.get_user_default_pump',
            callback: function(pump_data) {
                let default_pump = pump_data.message && pump_data.message.default_pump ? pump_data.message.default_pump : null;
            
                let d = new frappe.ui.Dialog({
                    title: __('Quick Sale - Walk-in Customer'),
                    fields: [
                        {
                            fieldname: 'customer_section',
                            fieldtype: 'Section Break',
                            label: 'Customer Details'
                        },
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
                        },
                        {
                            fieldname: 'col_break_1',
                            fieldtype: 'Column Break'
                        },
                        {
                            fieldname: 'petrol_pump',
                            fieldtype: 'Link',
                            label: 'Petrol Pump',
                            options: 'Petrol Pump Location',
                            reqd: 1,
                            default: default_pump  // AUTO-FILL from user settings
                        },
                        {
                            fieldname: 'fuel_type',
                            fieldtype: 'Select',
                            label: 'Fuel Type',
                            options: '\nPetrol\nDiesel\nCNG\nN/A',
                            default: 'N/A',
                            reqd: 1
                        },
                        {
                            fieldname: 'purchase_section',
                            fieldtype: 'Section Break',
                            label: 'Fuel Purchase'
                        },
                        {
                            fieldname: 'liters',
                            fieldtype: 'Float',
                            label: 'Liters',
                            reqd: 1
                        },
                        {
                            fieldname: 'amount',
                            fieldtype: 'Currency',
                            label: 'Amount',
                            reqd: 0,
                            description: 'Optional - Leave blank if not needed'
                        }
                    ],
                    primary_action_label: __('Create & Process'),
                    primary_action: function(values) {
                    if (!values.amount) {
                        values.amount = 0;
                    }
                    
                    // Show loading
                    frappe.show_alert({
                        message: __('Creating quick sale...'),
                        indicator: 'blue'
                    }, 2);
                    
                    frappe.call({
                        method: 'clp.api.create_quick_sale',
                        args: values,
                        callback: function(r) {
                            if (r.message) {
                                frappe.show_alert({
                                    message: __('Quick sale created successfully!'),
                                    indicator: 'green'
                                }, 5);
                                d.hide();
                                
                                // Show customer with options
                                show_quick_sale_result(r.message);
                            }
                        },
                        error: function() {
                            frappe.msgprint(__('Failed to create quick sale'));
                        }
                    });
                }
            });
            
            // Show alert if pump was auto-filled
            if (default_pump) {
                d.$wrapper.find('.modal-body').prepend(`
                    <div class="alert alert-success" style="margin-bottom: 15px;">
                        <i class="fa fa-check-circle"></i> 
                        Default pump auto-filled: <strong>${default_pump}</strong>
                    </div>
                `);
            }
            
            d.show();
        }
    });
}



    function show_quick_sale_result(result) {
        $('#scan-result').html(`
            <div class="scan-result-success">
                <h3 style="margin-top: 0; color: #28a745;">
                    <i class="fa fa-check-circle"></i> Quick Sale Completed!
                </h3>
                <table class="result-table">
                    <tr>
                        <td>Customer:</td>
                        <td><strong>${result.customer_name}</strong></td>
                    </tr>
                    <tr>
                        <td>Customer ID:</td>
                        <td><strong>${result.customer_id}</strong></td>
                    </tr>
                    <tr>
                        <td>Vehicle:</td>
                        <td>${result.vehicle_number}</td>
                    </tr>
                    <tr>
                        <td>Fuel Purchased:</td>
                        <td>${result.liters}L (${result.fuel_type})</td>
                    </tr>
                    <tr>
                        <td>Amount:</td>
                        <td>₹${result.amount}</td>
                    </tr>
                    <tr>
                        <td>Points Earned:</td>
                        <td><span class="badge badge-success">${result.points_earned}L</span></td>
                    </tr>
                </table>
                <div style="text-align: center; margin-top: 20px;">
                    <button class="btn btn-success btn-lg" onclick="redeem_gift('${result.customer_id}')" 
                            style="margin-right: 10px; margin-bottom: 10px;">
                        <i class="fa fa-gift"></i> Redeem Gift
                    </button>
                    <button class="btn btn-secondary" onclick="view_customer('${result.customer_id}')">
                        <i class="fa fa-eye"></i> View Customer
                    </button>
                </div>
            </div>
        `);
        
        // Reload recent customers
        load_recent_customers();
    }


    function show_customer_list_with_actions(customers) {
        let html = '<div style="margin-top: 20px;">';
        customers.forEach(function(customer) {
            html += `
                <div class="customer-card">
                    <div class="customer-card-body">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div>
                                <h5 style="margin: 0; color: #2c3e50;">${customer.customer_name}</h5>
                                <small style="color: #6c757d;">${customer.name} | ${customer.vehicle_number} | ${customer.mobile_number}</small>
                            </div>
                            <div style="text-align: right;">
                                <h4 style="margin: 0; color: #667eea;">${customer.current_cycle_liters}L</h4>
                                <small style="color: #6c757d;">Gifts: ${customer.total_gifts_received}</small>
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <button class="btn btn-primary btn-sm" onclick="create_fuel_purchase('${customer.name}')" style="margin-right: 5px;">
                                <i class="fa fa-plus"></i> Fuel
                            </button>
                            <button class="btn btn-success btn-sm" onclick="redeem_gift('${customer.name}')" style="margin-right: 5px;">
                                <i class="fa fa-gift"></i> Gift
                            </button>
                            <button class="btn btn-secondary btn-sm" onclick="view_customer('${customer.name}')">
                                <i class="fa fa-eye"></i> View
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        $('#scan-result').html(html);
    }


    function process_scanned_qr(qr_data) {
    $('#scan-result').html(`
        <div class="alert alert-info" style="font-size: 16px;">
            <i class="fa fa-spinner fa-spin"></i> Processing scanned QR...
        </div>
    `);
    
    // Extract customer ID from URL if it's a full URL
    let customer_id = qr_data;
    
    // Check if scanned data is a URL
    if (qr_data.includes('qr-redirect?id=') || qr_data.includes('qr-redirect&id=')) {
        try {
            // Extract ID from URL parameter
            const url = new URL(qr_data);
            const id_param = url.searchParams.get('id');
            if (id_param) {
                customer_id = id_param;
            }
        } catch (e) {
            // If URL parsing fails, try regex extraction
            const match = qr_data.match(/[?&]id=([^&]+)/);
            if (match && match[1]) {
                customer_id = match[1];
            }
        }
    }
    
    frappe.call({
        method: 'clp.api.scan_and_process_qr',
        args: { qr_data: customer_id },
        callback: function(r) {
            if (r.message.exists) {
                let c = r.message;
                $('#scan-result').html(`
                    <div class="scan-result-success">
                        <h3 style="margin-top: 0; color: #28a745;">
                            <i class="fa fa-check-circle"></i> Customer Found!
                        </h3>
                        <table class="result-table">
                            <tr>
                                <td>Name:</td>
                                <td><strong>${c.customer_name}</strong></td>
                            </tr>
                            <tr>
                                <td>ID:</td>
                                <td><strong>${c.customer_id}</strong></td>
                            </tr>
                            <tr>
                                <td>Vehicle:</td>
                                <td>${c.vehicle_number}</td>
                            </tr>
                            <tr>
                                <td>Mobile:</td>
                                <td>${c.mobile_number}</td>
                            </tr>
                            <tr>
                                <td>Loyalty Points:</td>
                                <td><span class="badge badge-primary" style="font-size: 16px;">${c.current_cycle_liters}L</span></td>
                            </tr>
                            <tr>
                                <td>Total Gifts:</td>
                                <td><span class="badge badge-warning">${c.total_gifts_received}</span></td>
                            </tr>
                        </table>
                        <div style="text-align: center; margin-top: 20px;">
                            <button class="btn btn-primary btn-lg" onclick="create_fuel_purchase('${c.customer_id}')" 
                                    style="margin-right: 10px; margin-bottom: 10px;">
                                <i class="fa fa-plus"></i> Add Fuel Purchase
                            </button>
                            <button class="btn btn-success btn-lg" onclick="redeem_gift('${c.customer_id}')" 
                                    style="margin-right: 10px; margin-bottom: 10px;">
                                <i class="fa fa-gift"></i> Redeem Gift
                            </button>
                            <button class="btn btn-secondary" onclick="view_customer('${c.customer_id}')">
                                <i class="fa fa-eye"></i> View Customer
                            </button>
                        </div>
                    </div>
                `);
            } else {
                show_register_dialog(customer_id);
            }
        }
    });
}



    function show_register_dialog(qr_data) {
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
                    qr_code: qr_data,
                    customer_name: values.customer_name,
                    mobile_number: values.mobile_number,
                    vehicle_number: values.vehicle_number
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Customer {0} registered!', [r.message.name]),
                            indicator: 'green'
                        }, 5);
                        
                        $('#scan-result').html(`
                            <div class="scan-result-success">
                                <h3 style="margin-top: 0; color: #28a745;">
                                    <i class="fa fa-check-circle"></i> Customer Registered!
                                </h3>
                                <p><strong>Customer ID:</strong> ${r.message.name}</p>
                                <p><strong>Name:</strong> ${values.customer_name}</p>
                                <div style="text-align: center; margin-top: 20px;">
                                    <button class="btn btn-primary btn-lg" onclick="create_fuel_purchase('${r.message.name}')" 
                                            style="margin-right: 10px; margin-bottom: 10px;">
                                        <i class="fa fa-plus"></i> Add Fuel Purchase
                                    </button>
                                    <button class="btn btn-success btn-lg" onclick="redeem_gift('${r.message.name}')" 
                                            style="margin-right: 10px; margin-bottom: 10px;">
                                        <i class="fa fa-gift"></i> Redeem Gift
                                    </button>
                                    <button class="btn btn-secondary" onclick="view_customer('${r.message.name}')">
                                        <i class="fa fa-eye"></i> View Customer
                                    </button>
                                </div>
                            </div>
                        `);
                        
                        load_recent_customers();
                    }
                }
            });
        },
        __('Register New Customer'),
        __('Register')
        );
    }


    function load_recent_customers() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Loyalty Customer',
                fields: ['name', 'customer_name', 'vehicle_number', 'current_cycle_liters', 'total_gifts_received'],
                filters: [['status', '=', 'Active']],
                order_by: 'modified desc',
                limit: 10
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let html = '';
                    r.message.forEach(function(customer) {
                        html += `
                            <div class="customer-card">
                                <div class="customer-card-body">
                                    <div class="customer-card-content">
                                        <div class="customer-info">
                                            <h5>${customer.customer_name}</h5>
                                            <small>ID: ${customer.name} | Vehicle: ${customer.vehicle_number}</small>
                                        </div>
                                        <div class="customer-stats">
                                            <h4>${customer.current_cycle_liters}L</h4>
                                            <small>Gifts: ${customer.total_gifts_received}</small>
                                        </div>
                                    </div>
                                    <div style="text-align: center; margin-top: 10px;">
                                        <button class="btn btn-primary btn-sm" onclick="create_fuel_purchase('${customer.name}')" style="margin-right: 5px;">
                                            <i class="fa fa-plus"></i> Fuel
                                        </button>
                                        <button class="btn btn-success btn-sm" onclick="redeem_gift('${customer.name}')">
                                            <i class="fa fa-gift"></i> Gift
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    $('#customer-list').html(html);
                } else {
                    $('#customer-list').html('<p style="text-align: center; color: #6c757d;">No customers yet</p>');
                }
            }
        });
    }


    window.create_fuel_purchase = function(customer_id) {
        frappe.new_doc('Fuel Purchase Entry', {
            'customer': customer_id
        });
    };


    window.redeem_gift = function(customer_id) {
        frappe.new_doc('Gift Redemption', {
            'customer': customer_id
        });
    };


    window.view_customer = function(customer_id) {
        frappe.set_route('Form', 'Loyalty Customer', customer_id);
    };
};
