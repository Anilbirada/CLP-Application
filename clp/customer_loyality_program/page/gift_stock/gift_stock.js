frappe.pages['gift-stock'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Gift Stock Management',
        single_column: true
    });

    // Hide Frappe default duplicate page-head so only our branded petroleum banner is shown
    $(wrapper).find('.page-head').hide();

    let html = `
        <style>
            .stock-container {
                padding: 16px 20px 40px 20px;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .gift-stock-hero-banner {
                background: linear-gradient(135deg, rgba(16, 27, 45, 0.94) 0%, rgba(23, 42, 69, 0.90) 100%),
                            url('/assets/clp/images/indian_petrol_pump_bg.jpg') no-repeat center center;
                background-size: cover;
                padding: 28px 30px;
                border-radius: 14px;
                margin-bottom: 22px;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.12);
                box-shadow: 0 6px 20px rgba(16, 27, 45, 0.18);
            }
            
            .gift-stock-hero-banner h1 {
                margin: 0;
                font-size: 26px !important;
                font-weight: 800 !important;
                color: #ffffff !important;
                letter-spacing: -0.02em;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .gift-stock-hero-banner h1 i {
                color: #F2A900 !important;
                font-size: 24px;
            }
            
            .gift-stock-hero-banner p {
                margin: 8px 0 0 0;
                color: #DCE4ED !important;
                font-size: 14.5px;
                font-weight: 500;
            }
            
            .filters-section {
                background: #ffffff;
                padding: 20px 24px;
                border-radius: 12px;
                margin-bottom: 22px;
                border: 1px solid #DCE4ED;
                box-shadow: 0 2px 8px rgba(16, 27, 45, 0.05);
            }
            
            .stock-grid {
                display: grid;
                gap: 20px;
            }
            
            .stock-card {
                background: #ffffff;
                border-radius: 12px;
                padding: 22px;
                border: 1px solid #DCE4ED;
                box-shadow: 0 2px 8px rgba(16, 27, 45, 0.05);
                transition: all 0.25s ease;
            }
            
            .stock-card:hover {
                transform: translateY(-2px);
                border-color: #1769AA;
                box-shadow: 0 8px 20px rgba(23, 105, 170, 0.12);
            }
            
            .stock-header {
                display: grid;
                grid-template-columns: 2fr 1fr 1fr;
                gap: 18px;
                align-items: center;
                margin-bottom: 16px;
                padding-bottom: 16px;
                border-bottom: 1px solid #EDF2F7;
            }
            
            .item-info h4 {
                margin: 0 0 6px 0;
                color: #101B2D;
                font-size: 17px;
                font-weight: 700;
            }
            
            .item-info small {
                color: #526174;
                font-size: 13px;
                font-weight: 500;
            }
            
            .stock-display {
                text-align: center;
                padding: 14px 18px;
                background: #F4F7FA;
                border: 1px solid #DCE4ED;
                border-radius: 10px;
            }
            
            .stock-qty {
                font-size: 32px;
                font-weight: 800;
                color: #159B64;
                line-height: 1;
            }
            
            .stock-qty.low {
                color: #F2A900;
            }
            
            .stock-qty.out {
                color: #dc2626;
            }
            
            .stock-actions {
                display: flex;
                gap: 10px;
                justify-content: center;
            }
            
            .btn-adjust {
                padding: 9px 18px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-size: 13.5px;
                transition: all 0.2s ease;
            }
            
            .btn-add {
                background: #159B64;
                color: white;
            }
            
            .btn-add:hover {
                background: #118152;
                transform: translateY(-1px);
            }
            
            .btn-remove {
                background: #dc2626;
                color: white;
            }
            
            .btn-remove:hover {
                background: #b91c1c;
                transform: translateY(-1px);
            }
            
            @media (max-width: 768px) {
                .stock-header {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        
        <div class="stock-container">
            <div class="gift-stock-hero-banner">
                <h1>
                    <i class="fa fa-boxes"></i> Gift Stock Management
                </h1>
                <p>
                    Manage gift item inventory, physical balances, and stock transfers across all pump locations
                </p>
            </div>
            
            <div class="filters-section">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 16px; align-items: end;">
                    <div>
                        <label style="display: block; margin-bottom: 6px; font-weight: 600; font-size: 13.5px; color: #202B3C;">Pump Location</label>
                        <select id="pump-filter" class="form-control" style="height: 42px; border: 1px solid #DCE4ED; border-radius: 8px; font-size: 14px; color: #202B3C; font-weight: 500;">
                            <option value="">All Pumps</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 6px; font-weight: 600; font-size: 13.5px; color: #202B3C;">Gift Item</label>
                        <select id="item-filter" class="form-control" style="height: 42px; border: 1px solid #DCE4ED; border-radius: 8px; font-size: 14px; color: #202B3C; font-weight: 500;">
                            <option value="">All Items</option>
                        </select>
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 6px; font-weight: 600; font-size: 13.5px; color: #202B3C;">Stock Status</label>
                        <select id="status-filter" class="form-control" style="height: 42px; border: 1px solid #DCE4ED; border-radius: 8px; font-size: 14px; color: #202B3C; font-weight: 500;">
                            <option value="">All Status</option>
                            <option value="in_stock">In Stock</option>
                            <option value="low_stock">Low Stock</option>
                            <option value="out_of_stock">Out of Stock</option>
                        </select>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="load_stock_data()" style="height: 42px; padding: 0 22px; font-weight: 600; font-size: 14px; background: #1769AA; border: none; border-radius: 8px; box-shadow: 0 2px 6px rgba(23,105,170,0.3); display: flex; align-items: center; gap: 8px;">
                            <i class="fa fa-refresh"></i> Refresh
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="stock-grid" id="stock-container">
                <div style="text-align: center; padding: 40px; color: #526174;">
                    <i class="fa fa-spinner fa-spin" style="font-size: 42px; color: #1769AA;"></i>
                    <p style="margin-top: 12px; font-weight: 500; font-size: 14px;">Loading stock data...</p>
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
