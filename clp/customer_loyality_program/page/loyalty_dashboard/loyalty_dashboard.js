frappe.pages['loyalty-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Loyalty Program Dashboard',
        single_column: true
    });

    let html = `
        <style>
            .dashboard-container {
                padding: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .dashboard-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                border-radius: 15px;
                margin-bottom: 30px;
                color: white;
                text-align: center;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.3s;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            }
            
            .stat-value {
                font-size: 36px;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .stat-label {
                color: #6c757d;
                font-size: 14px;
                text-transform: uppercase;
            }
            
            .quick-actions {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .action-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 12px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                color: white;
            }
            
            .action-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            
            .action-card i {
                font-size: 48px;
                margin-bottom: 15px;
            }
            
            .action-card h4 {
                margin: 0;
                color: white;
            }
            
            .reports-section {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .report-link {
                display: block;
                padding: 15px;
                margin-bottom: 10px;
                background: #f8f9fa;
                border-radius: 8px;
                text-decoration: none;
                color: #2c3e50;
                transition: all 0.3s;
            }
            
            .report-link:hover {
                background: #667eea;
                color: white;
                transform: translateX(5px);
            }
        </style>
        
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h1 style="margin: 0; font-size: 42px;">🎁 Loyalty Program</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">
                    Customer Rewards & Gift Management System
                </p>
            </div>
            
            <div class="stats-grid" id="stats-container">
                <div class="stat-card">
                    <div class="stat-value"><i class="fa fa-spinner fa-spin"></i></div>
                    <div class="stat-label">Loading...</div>
                </div>
            </div>
            
            <h3 style="margin: 30px 0 20px 0; color: #36414C;">Quick Actions</h3>
            <div class="quick-actions">
                <div class="action-card" onclick="frappe.set_route('clp-qr-scanner')">
                    <i class="fa fa-qrcode"></i>
                    <h4>QR Scanner</h4>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">
                        Scan customer QR codes
                    </p>
                </div>
                
                <div class="action-card" onclick="frappe.new_doc('Fuel Purchase Entry')" 
                     style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                    <i class="fa fa-plus-circle"></i>
                    <h4>Fuel Purchase</h4>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">
                        Add fuel purchase entry
                    </p>
                </div>
                
                <div class="action-card" onclick="frappe.new_doc('Gift Redemption')"
                     style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                    <i class="fa fa-gift"></i>
                    <h4>Gift Redemption</h4>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">
                        Redeem customer gifts
                    </p>
                </div>
                
                <div class="action-card" onclick="frappe.new_doc('Loyalty Customer')"
                     style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <i class="fa fa-user-plus"></i>
                    <h4>New Customer</h4>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">
                        Register new customer
                    </p>
                </div>
                
                <div class="action-card" onclick="frappe.set_route('gift-stock')"
                     style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <i class="fa fa-boxes"></i>
                    <h4>Manage Stock</h4>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">
                        Gift stock management
                    </p>
                </div>
            </div>
            
            <h3 style="margin: 30px 0 20px 0; color: #36414C;">Reports & Analytics</h3>
            <div class="reports-section">
                <a href="/app/query-report/Customer Loyalty Dashboard" class="report-link">
                    <i class="fa fa-chart-bar"></i> Customer Loyalty Dashboard
                </a>
                <a href="/app/query-report/Gift Redemption Summary" class="report-link">
                    <i class="fa fa-gift"></i> Gift Redemption Summary
                </a>
                <a href="/app/query-report/Pump-wise Gift Stock" class="report-link">
                    <i class="fa fa-cubes"></i> Pump-wise Gift Stock
                </a>
            </div>
        </div>
    `;

    $(page.body).html(html);
    
    // Load stats
    load_dashboard_stats();
};

function load_dashboard_stats() {
    frappe.call({
        method: 'clp.api.get_loyalty_dashboard_stats',
        callback: function(r) {
            if (r.message) {
                let stats = r.message;
                let html = `
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_customers}</div>
                        <div class="stat-label">Total Customers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #43e97b;">${stats.active_customers}</div>
                        <div class="stat-label">Active Customers</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #f5576c;">${stats.total_points}L</div>
                        <div class="stat-label">Total Points</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #fa709a;">${stats.total_gifts}</div>
                        <div class="stat-label">Gifts Redeemed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #4facfe;">${stats.today_purchases}</div>
                        <div class="stat-label">Today's Purchases</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: #fee140;">${stats.today_redemptions}</div>
                        <div class="stat-label">Today's Redemptions</div>
                    </div>
                `;
                $('#stats-container').html(html);
            }
        }
    });
}
