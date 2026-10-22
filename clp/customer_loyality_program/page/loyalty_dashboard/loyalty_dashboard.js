frappe.pages['loyalty-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Customer Loyalty Dashboard',
        single_column: true
    });

    let html = `
        <style>
            .clp-dash-wrap {
                padding: 24px;
                max-width: 1350px;
                margin: 0 auto;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            
            .clp-dash-banner {
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.86) 100%),
                            url('/assets/clp/images/indian_petrol_pump_bg.jpg') no-repeat center center !important;
                background-size: cover !important;
                padding: 38px 34px;
                border-radius: 14px;
                margin-bottom: 28px;
                color: #ffffff;
                border: 1px solid rgba(255,255,255,0.12);
                box-shadow: 0 8px 24px rgba(15,23,42,0.18);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 16px;
            }
            
            .clp-dash-banner h1 {
                margin: 0;
                font-size: 26px;
                font-weight: 800;
                letter-spacing: -0.02em;
                color: #ffffff;
            }
            
            .clp-dash-banner p {
                margin: 6px 0 0 0;
                font-size: 14px;
                color: #94a3b8;
            }

            .clp-live-pill {
                background: rgba(16,185,129,0.15);
                border: 1px solid rgba(16,185,129,0.3);
                color: #34d399;
                font-size: 12.5px;
                font-weight: 600;
                padding: 6px 14px;
                border-radius: 9999px;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }
            
            .clp-stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin-bottom: 32px;
            }
            
            .clp-stat-card {
                background: #ffffff;
                border-radius: 12px;
                padding: 22px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
                transition: all 0.2s ease;
                position: relative;
                overflow: hidden;
            }

            .clp-stat-card::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: #2563eb;
            }
            
            .clp-stat-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.08);
                border-color: #cbd5e1;
            }
            
            .clp-stat-value {
                font-size: 30px;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 6px;
                letter-spacing: -0.02em;
            }
            
            .clp-stat-label {
                color: #64748b;
                font-size: 12.5px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .clp-section-heading {
                margin: 0 0 16px 0;
                color: #0f172a;
                font-size: 17px;
                font-weight: 700;
                letter-spacing: -0.01em;
            }

            .clp-quick-actions {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
                gap: 16px;
                margin-bottom: 32px;
            }
            
            .clp-action-card {
                background: #ffffff;
                border: 1.5px solid #e2e8f0;
                padding: 24px 20px;
                border-radius: 12px;
                text-align: left;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 1px 3px rgba(0,0,0,0.03);
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .clp-action-card:hover {
                border-color: #2563eb;
                transform: translateY(-3px);
                box-shadow: 0 10px 20px -4px rgba(37,99,235,0.12);
            }
            
            .clp-action-icon {
                width: 44px;
                height: 44px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                margin-bottom: 6px;
            }

            .icon-blue   { background: #eff6ff; color: #2563eb; }
            .icon-green  { background: #ecfdf5; color: #059669; }
            .icon-purple { background: #f5f3ff; color: #7c3aed; }
            .icon-amber  { background: #fffbeb; color: #d97706; }
            .icon-slate  { background: #f1f5f9; color: #475569; }
            
            .clp-action-card h4 {
                margin: 0;
                color: #0f172a;
                font-size: 15px;
                font-weight: 700;
            }

            .clp-action-card p {
                margin: 0;
                font-size: 12.5px;
                color: #64748b;
                line-height: 1.4;
            }
            
            .clp-reports-box {
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            }
            
            .clp-report-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 14px 18px;
                margin-bottom: 8px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                text-decoration: none;
                color: #0f172a;
                font-weight: 600;
                font-size: 13.5px;
                transition: all 0.2s ease;
            }

            .clp-report-row:last-child {
                margin-bottom: 0;
            }
            
            .clp-report-row:hover {
                background: #eff6ff;
                border-color: #bfdbfe;
                color: #1d4ed8;
                transform: translateX(3px);
                text-decoration: none;
            }
        </style>
        
        <div class="clp-dash-wrap">
            <div class="clp-dash-banner">
                <div>
                    <h1><i class="fa fa-gas-pump" style="color: #38bdf8; margin-right: 8px;"></i> Customer Loyalty Program</h1>
                    <p>Executive Oversight & Transaction Operations</p>
                </div>
                <div class="clp-live-pill">
                    <i class="fa fa-circle" style="font-size: 8px;"></i> Live Operational System
                </div>
            </div>
            
            <div class="clp-stats-grid" id="stats-container">
                <div class="clp-stat-card">
                    <div class="clp-stat-value"><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #2563eb;"></i></div>
                    <div class="clp-stat-label">Loading Metrics...</div>
                </div>
            </div>
            
            <div class="clp-section-heading">Operational Actions</div>
            <div class="clp-quick-actions">
                <div class="clp-action-card" onclick="frappe.set_route('clp-qr-scanner')">
                    <div class="clp-action-icon icon-blue"><i class="fa fa-qrcode"></i></div>
                    <h4>QR Code Scanner</h4>
                    <p>Instant camera resolution of customer loyalty accounts</p>
                </div>
                
                <div class="clp-action-card" onclick="frappe.new_doc('Fuel Purchase Entry')">
                    <div class="clp-action-icon icon-green"><i class="fa fa-plus-circle"></i></div>
                    <h4>Fuel Purchase Entry</h4>
                    <p>Record fuel purchase and award loyalty liters</p>
                </div>
                
                <div class="clp-action-card" onclick="frappe.new_doc('Gift Redemption')">
                    <div class="clp-action-icon icon-purple"><i class="fa fa-gift"></i></div>
                    <h4>Gift Redemption</h4>
                    <p>Claim milestone rewards with points validation</p>
                </div>
                
                <div class="clp-action-card" onclick="frappe.new_doc('Loyalty Customer')">
                    <div class="clp-action-icon icon-amber"><i class="fa fa-user-plus"></i></div>
                    <h4>Register Customer</h4>
                    <p>Add new customer profile and vehicle mapping</p>
                </div>
                
                <div class="clp-action-card" onclick="frappe.set_route('gift-stock')">
                    <div class="clp-action-icon icon-slate"><i class="fa fa-boxes"></i></div>
                    <h4>Manage Gift Stock</h4>
                    <p>Allocate gift items to petrol pump warehouses</p>
                </div>
            </div>
            
            <div class="clp-section-heading">Reports & Analytical Insights</div>
            <div class="clp-reports-box">
                <a href="/app/query-report/Customer Loyalty Dashboard" class="clp-report-row">
                    <span><i class="fa fa-chart-bar" style="color: #2563eb; margin-right: 10px;"></i> Customer Loyalty Leaderboard & Summary</span>
                    <i class="fa fa-chevron-right" style="color: #94a3b8; font-size: 12px;"></i>
                </a>
                <a href="/app/query-report/Gift Redemption Summary" class="clp-report-row">
                    <span><i class="fa fa-gift" style="color: #7c3aed; margin-right: 10px;"></i> Gift Distribution & Redemption Summary</span>
                    <i class="fa fa-chevron-right" style="color: #94a3b8; font-size: 12px;"></i>
                </a>
                <a href="/app/query-report/Pump-wise Gift Stock" class="clp-report-row">
                    <span><i class="fa fa-cubes" style="color: #059669; margin-right: 10px;"></i> Pump-wise Gift Inventory Stock Balance</span>
                    <i class="fa fa-chevron-right" style="color: #94a3b8; font-size: 12px;"></i>
                </a>
            </div>
        </div>
    `;

    $(page.body).html(html);
    load_dashboard_stats();
};

function load_dashboard_stats() {
    frappe.call({
        method: 'clp.api.get_loyalty_dashboard_stats',
        callback: function(r) {
            if (r.message) {
                let stats = r.message;
                let html = `
                    <div class="clp-stat-card">
                        <div class="clp-stat-value">${stats.total_customers}</div>
                        <div class="clp-stat-label">Total Customers</div>
                    </div>
                    <div class="clp-stat-card">
                        <div class="clp-stat-value" style="color: #059669;">${stats.active_customers}</div>
                        <div class="clp-stat-label">Active Customers</div>
                    </div>
                    <div class="clp-stat-card">
                        <div class="clp-stat-value" style="color: #2563eb;">${stats.total_points}L</div>
                        <div class="clp-stat-label">Total Loyalty Points</div>
                    </div>
                    <div class="clp-stat-card">
                        <div class="clp-stat-value" style="color: #7c3aed;">${stats.total_gifts}</div>
                        <div class="clp-stat-label">Gifts Redeemed</div>
                    </div>
                    <div class="clp-stat-card">
                        <div class="clp-stat-value" style="color: #0284c7;">${stats.today_purchases}</div>
                        <div class="clp-stat-label">Today's Purchases</div>
                    </div>
                    <div class="clp-stat-card">
                        <div class="clp-stat-value" style="color: #d97706;">${stats.today_redemptions}</div>
                        <div class="clp-stat-label">Today's Redemptions</div>
                    </div>
                `;
                $('#stats-container').html(html);
            }
        }
    });
}
