frappe.pages['gift-stock'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Gift Stock Management',
        single_column: true
    });

    let html = `
        <style>
            .stock-container {
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .page-header {
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                color: white;
            }
            
            .filters-section {
                background: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .stock-grid {
                display: grid;
                gap: 20px;
            }
            
            .stock-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.3s;
            }
            
            .stock-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);
            }
            
            .stock-header {
                display: grid;
                grid-template-columns: 2fr 1fr 1fr;
                gap: 15px;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f0f0f0;
            }
            
            .item-info h4 {
                margin: 0 0 5px 0;
                color: #2c3e50;
            }
            
            .item-info small {
                color: #6c757d;
            }
            
            .stock-display {
                text-align: center;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }
            
            .stock-qty {
                font-size: 32px;
                font-weight: bold;
                color: #43e97b;
            }
            
            .stock-qty.low {
                color: #ff9800;
            }
            
            .stock-qty.out {
                color: #f5576c;
            }
            
            .stock-actions {
                display: flex;
                gap: 10px;
                justify-content: center;
            }
            
            .btn-adjust {
                padding: 8px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s;
            }
            
            .btn-add {
                background: #43e97b;
                color: white;
            }
            
            .btn-add:hover {
                background: #38d66a;
            }
            
            .btn-remove {
                background: #f5576c;
                color: white;
            }
            
            .btn-remove:hover {
                background: #e04a5f;
            }
            
            @media (max-width: 768px) {
                .stock-header {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        
        <div class="stock-container">
            <div class="page-header">
                <h1 style="margin: 0; font-size: 32px;">
                    <i class="fa fa-boxes"></i> Gift Stock Management
                </h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">
                    Manage gift item inventory across all pump locations
                </p>
            </div>
            
            <div class="filters-section">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 15px; align-items: end;">
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-weight: 600;">Pump Location</label>
                        <select id="pump-filter" class="form-control">
                            <option value="">All Pumps</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-weight: 600;">Gift Item</label>
                        <select id="item-filter" class="form-control">
                            <option value="">All Items</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 5px; font-weight: 600;">Stock Status</label>
                        <select id="status-filter" class="form-control">
                            <option value="">All Status</option>
                            <option value="in_stock">In Stock</option>
                            <option value="low_stock">Low Stock</option>
                            <option value="out_of_stock">Out of Stock</option>
                        </select>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="load_stock_data()">
                            <i class="fa fa-refresh"></i> Refresh
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="stock-grid" id="stock-container">
                <div style="text-align: center; padding: 40px; color: #6c757d;">
                    <i class="fa fa-spinner fa-spin" style="font-size: 48px;"></i>
                    <p>Loading stock data...</p>
                </div>
            </div>
        </div>
    `;

    $(page.body).html(html);
    
    // Load initial data
    load_filters();
    load_stock_data();
    
    // Event listeners
    $('#pump-filter, #item-filter, #status-filter').on('change', load_stock_data);
};

function load_filters() {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Petrol Pump Location',
            filters: {is_active: 1},
            fields: ['name', 'pump_name'],
            order_by: 'pump_name'
        },
        callback: function(r) {
            if (r.message) {
                let html = '<option value="">All Pumps</option>';
                r.message.forEach(pump => {
                    html += `<option value="${pump.name}">${pump.pump_name}</option>`;
                });
                $('#pump-filter').html(html);
            }
        }
    });
    
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Item',
            fields: ['name', 'item_name'],
            order_by: 'item_name',
            limit: 100
        },
        callback: function(r) {
            if (r.message) {
                let html = '<option value="">All Items</option>';
                r.message.forEach(item => {
                    html += `<option value="${item.name}">${item.item_name}</option>`;
                });
                $('#item-filter').html(html);
            }
        }
    });
}

function load_stock_data() {
    let pump = $('#pump-filter').val();
    let item = $('#item-filter').val();
    let status = $('#status-filter').val();
    
    frappe.call({
        method: 'clp.api.get_gift_stock_data',
        args: {
            pump: pump,
            item: item,
            status: status
        },
        callback: function(r) {
            if (r.message) {
                render_stock_cards(r.message);
            }
        }
    });
}

function render_stock_cards(data) {
    if (!data || data.length === 0) {
        $('#stock-container').html(`
            <div style="text-align: center; padding: 40px; color: #6c757d;">
                <i class="fa fa-inbox" style="font-size: 64px; margin-bottom: 20px; opacity: 0.3;"></i>
                <h3>No stock data found</h3>
                <p>Try adjusting your filters or add gift items to pump locations.</p>
            </div>
        `);
        return;
    }
    
    let html = '';
    data.forEach(stock => {
        let qty_class = stock.actual_qty > 10 ? '' : (stock.actual_qty > 0 ? 'low' : 'out');
        let status_text = stock.actual_qty > 10 ? 'In Stock' : (stock.actual_qty > 0 ? 'Low Stock' : 'Out of Stock');
        
        html += `
            <div class="stock-card">
                <div class="stock-header">
                    <div class="item-info">
                        <h4><i class="fa fa-gift"></i> ${stock.item_name}</h4>
                        <small>
                            <i class="fa fa-map-marker-alt"></i> ${stock.pump_name} | 
                            <i class="fa fa-warehouse"></i> ${stock.warehouse}
                        </small>
                        ${stock.points_required ? `<br><small style="color: #667eea;"><i class="fa fa-star"></i> ${stock.points_required}L points required</small>` : ''}
                    </div>
                    <div class="stock-display">
                        <div class="stock-qty ${qty_class}">${stock.actual_qty || 0}</div>
                        <small style="color: #6c757d;">${status_text}</small>
                    </div>
                    <div class="stock-actions">
                        <button class="btn-adjust btn-add" onclick="adjust_stock('${stock.item_code}', '${stock.warehouse}', 'add')">
                            <i class="fa fa-plus"></i> Add
                        </button>
                        <button class="btn-adjust btn-remove" onclick="adjust_stock('${stock.item_code}', '${stock.warehouse}', 'remove')">
                            <i class="fa fa-minus"></i> Remove
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    $('#stock-container').html(html);
}

window.adjust_stock = function(item_code, warehouse, action) {
    let d = new frappe.ui.Dialog({
        title: action === 'add' ? __('Add Stock') : __('Remove Stock'),
        fields: [
            {
                fieldname: 'item',
                fieldtype: 'Data',
                label: 'Item',
                default: item_code,
                read_only: 1
            },
            {
                fieldname: 'warehouse',
                fieldtype: 'Data',
                label: 'Warehouse',
                default: warehouse,
                read_only: 1
            },
            {
                fieldname: 'qty',
                fieldtype: 'Float',
                label: 'Quantity',
                reqd: 1,
                default: 1
            },
            {
                fieldname: 'reason',
                fieldtype: 'Small Text',
                label: 'Reason/Notes',
                reqd: 1
            }
        ],
        primary_action_label: action === 'add' ? __('Add Stock') : __('Remove Stock'),
        primary_action: function(values) {
            frappe.call({
                method: 'clp.api.adjust_gift_stock',
                args: {
                    item_code: item_code,
                    warehouse: warehouse,
                    qty: values.qty,
                    action: action,
                    reason: values.reason
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Stock adjusted successfully'),
                            indicator: 'green'
                        });
                        d.hide();
                        load_stock_data();
                    }
                }
            });
        }
    });
    d.show();
};
