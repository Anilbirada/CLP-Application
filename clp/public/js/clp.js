// CLP Global Client Enhancement, Route Protection & Seamless Slug Translation
frappe.provide('clp');

(function() {
    const SLUG_MAP = {
        'fuel-entry': 'fuel-purchase-entry',
        'customer-clp': 'loyalty-customer',
        'vehicle-clp': 'loyalty-customer',
        'qr-scanner': 'clp-qr-scanner',
        'petrol-pump': 'petrol-pump-location',
        'gift': 'gift-stock',
        'gift-stock-entry': 'clp-gift-stock-ledger',
        'gift-stock-transfer': 'gift-stock-request'
    };

    function translateSubPath(sub_path) {
        if (!sub_path) return sub_path;
        
        let parts = sub_path.split('/');
        let first = parts[0].toLowerCase();
        
        // Exact doc slug translations
        if (SLUG_MAP[first]) {
            parts[0] = SLUG_MAP[first];
            if (first === 'fuel-entry' && parts[1] && parts[1].startsWith('new-fuel-entry')) {
                parts[1] = 'new-fuel-purchase-entry-1';
            }
            return parts.join('/');
        }
        
        // Reports translation
        if (first === 'query-report' && parts[1]) {
            let rep = decodeURIComponent(parts[1]).toLowerCase();
            if (rep === 'pump stock summary') {
                parts[1] = 'Pump-wise Gift Stock';
            } else if (rep === 'customer activity report') {
                parts[1] = 'CLP Activity Audit Report';
            } else if (rep === 'customer registration summary') {
                parts[1] = 'Customer Loyalty Summary';
            }
            return parts.join('/');
        }
        
        // Workspace translation
        if (first === 'customer-loyalty-program') {
            return 'clp';
        }

        return sub_path;
    }

    function applyHooks() {
        if (!window.frappe || !frappe.router) return;

        // 1. Hook frappe.router.get_sub_path
        if (!frappe.router._clp_subpath_hooked) {
            frappe.router._clp_subpath_hooked = true;
            const orig_get_sub_path = frappe.router.get_sub_path.bind(frappe.router);
            frappe.router.get_sub_path = function(route) {
                let sub = orig_get_sub_path(route);
                return translateSubPath(sub);
            };
        }

        // 2. Hook frappe.router.setup
        if (!frappe.router._clp_setup_hooked) {
            frappe.router._clp_setup_hooked = true;
            const orig_setup = frappe.router.setup.bind(frappe.router);
            frappe.router.setup = function() {
                orig_setup();
                injectRoutes();
            };
        }

        // 3. Inject routes and native re_routes immediately
        injectRoutes();
        setupReRoutes();

        // 4. Hook frappe.router.convert_to_standard_route
        if (!frappe.router._clp_convert_hooked) {
            frappe.router._clp_convert_hooked = true;
            const orig_convert = frappe.router.convert_to_standard_route.bind(frappe.router);
            frappe.router.convert_to_standard_route = async function(route) {
                if (route && route[0]) {
                    let first = (route[0] || '').toLowerCase();
                    if (SLUG_MAP[first]) {
                        route[0] = SLUG_MAP[first];
                        if (first === 'fuel-entry' && route[1] && route[1].startsWith('new-fuel-entry')) {
                            route[1] = 'new-fuel-purchase-entry-1';
                        }
                    }
                    if (first === 'query-report' && route[1]) {
                        let rep = decodeURIComponent(route[1]).toLowerCase();
                        if (rep === 'pump stock summary') route[1] = 'Pump-wise Gift Stock';
                        else if (rep === 'customer activity report') route[1] = 'CLP Activity Audit Report';
                        else if (rep === 'customer registration summary') route[1] = 'Customer Loyalty Summary';
                    }
                    if (first === 'customer-loyalty-program' || (first === 'workspaces' && (route[1] || '').toLowerCase() === 'customer-loyalty-program')) {
                        if (frappe.workspaces && !frappe.workspaces['customer-loyalty-program'] && frappe.workspaces['clp']) {
                            return ['Workspaces', 'CLP'];
                        }
                    }
                }
                return await orig_convert(route);
            };
        }

        // 5. Intercept show_not_found if page matches any alias
        if (!frappe._clp_not_found_hooked && typeof frappe.show_not_found === 'function') {
            frappe._clp_not_found_hooked = true;
            const orig_not_found = frappe.show_not_found.bind(frappe);
            frappe.show_not_found = function(page_name) {
                let p = (page_name || '').toLowerCase();
                if (SLUG_MAP[p]) {
                    frappe.set_route(SLUG_MAP[p]);
                    return;
                }
                return orig_not_found(page_name);
            };
        }

        // 6. Intercept and suppress any stray "Module Stock not found" alerts
        if (!frappe._clp_stock_msg_hooked && typeof frappe.msgprint === 'function') {
            frappe._clp_stock_msg_hooked = true;
            const orig_msgprint = frappe.msgprint.bind(frappe);
            frappe.msgprint = function(msg, title) {
                let text = '';
                if (typeof msg === 'string') {
                    text = msg;
                } else if (msg && typeof msg === 'object') {
                    text = (msg.message || '') + ' ' + (msg.title || '') + ' ' + (title || '');
                }
                if (text && text.toLowerCase().includes('module stock not found')) {
                    console.warn('Suppressed Module Stock not found modal:', msg);
                    return null;
                }
                return orig_msgprint.apply(this, arguments);
            };
        }
    }

    function setupReRoutes() {
        if (!window.frappe) return;
        if (!frappe.re_route) frappe.re_route = {};
        frappe.re_route['fuel-entry'] = 'fuel-purchase-entry';
        frappe.re_route['fuel-entry/new-fuel-entry-1'] = 'fuel-purchase-entry/new-fuel-purchase-entry-1';
        frappe.re_route['qr-scanner'] = 'clp-qr-scanner';
        frappe.re_route['customer-clp'] = 'loyalty-customer';
        frappe.re_route['vehicle-clp'] = 'loyalty-customer';
        frappe.re_route['gift'] = 'gift-stock';
        frappe.re_route['gift-stock-entry'] = 'clp-gift-stock-ledger';
        frappe.re_route['gift-stock-transfer'] = 'gift-stock-request';
    }

    function injectRoutes() {
        if (!frappe.router || !frappe.router.routes) return;
        frappe.router.routes['fuel-entry'] = { doctype: 'Fuel Purchase Entry' };
        frappe.router.routes['customer-clp'] = { doctype: 'Loyalty Customer' };
        frappe.router.routes['vehicle-clp'] = { doctype: 'Loyalty Customer' };
        frappe.router.routes['petrol-pump'] = { doctype: 'Petrol Pump Location' };
        frappe.router.routes['gift'] = { page: 'gift-stock' };
        frappe.router.routes['gift-stock-entry'] = { doctype: 'CLP Gift Stock Ledger' };
        frappe.router.routes['gift-stock-transfer'] = { doctype: 'Gift Stock Request' };
    }

    // 7. Universal Bottom-Center Save / Primary Action Button for All Forms
    function setupBottomSaveButton() {
        if (!window.frappe) return;

        function updateBottomButton() {
            let $container = $('#clp-bottom-save-container');
            if (!$container.length) {
                $('body').append(`
                    <div id="clp-bottom-save-container" style="display:none;">
                        <button type="button" id="clp-bottom-save-btn" class="btn" aria-label="Save">
                            <span class="btn-icon">💾</span>
                            <span class="btn-text">Save</span>
                        </button>
                    </div>
                `);
                $container = $('#clp-bottom-save-container');

                $(document).on('click', '#clp-bottom-save-btn', function(e) {
                    e.preventDefault();
                    e.stopPropagation();

                    // Animate click feedback
                    $(this).css('transform', 'scale(0.95)');
                    setTimeout(() => $(this).css('transform', ''), 150);

                    // 1. If active cur_frm, trigger save
                    if (window.cur_frm && typeof cur_frm.save === 'function') {
                        cur_frm.save();
                        return;
                    }

                    // 2. Fallback to trigger top primary-action
                    const $primary = $('.page-container:visible .page-head .primary-action:visible, .page-container:visible .standard-actions .primary-action:visible').first();
                    if ($primary.length) {
                        $primary.trigger('click');
                    }
                });
            }

            // Check if we are currently on a form page with a visible primary action
            const isFormView = Boolean(window.cur_frm && cur_frm.$wrapper && cur_frm.$wrapper.is(':visible'));
            const $topPrimary = $('.page-container:visible .page-head .primary-action, .page-container:visible .standard-actions .primary-action').first();

            if (isFormView && $topPrimary.length && $topPrimary.is(':visible')) {
                const rawText = ($topPrimary.text() || 'Save').trim();
                const isDisabled = $topPrimary.prop('disabled');
                const $btn = $('#clp-bottom-save-btn');

                $btn.find('.btn-text').text(rawText);

                // Set relevant icon based on action
                let icon = '💾';
                const lower = rawText.toLowerCase();
                if (lower.includes('submit')) icon = '🚀';
                else if (lower.includes('update')) icon = '🔄';
                else if (lower.includes('saved')) icon = '✓';
                else if (lower.includes('saving')) icon = '⏳';
                $btn.find('.btn-icon').text(icon);

                if (lower === 'saved') {
                    $btn.addClass('btn-saved');
                } else {
                    $btn.removeClass('btn-saved');
                }

                $btn.prop('disabled', isDisabled);
                if (!$container.is(':visible')) {
                    $container.stop(true, true).fadeIn(200);
                }
            } else {
                if ($container.is(':visible')) {
                    $container.stop(true, true).fadeOut(200);
                }
            }
        }

        // Event hooks
        if (frappe.router && frappe.router.on) {
            frappe.router.on('change', () => setTimeout(updateBottomButton, 250));
        }
        $(window).on('hashchange', () => setTimeout(updateBottomButton, 250));
        $(document).on('form-refresh page-change after_save', () => setTimeout(updateBottomButton, 150));
        $(document).on('input change', 'input, select, textarea', () => setTimeout(updateBottomButton, 150));

        // Periodic sync to track form state changes (500ms)
        setInterval(updateBottomButton, 500);

        // Immediate first check
        updateBottomButton();
    }

    // Apply as early as possible
    applyHooks();

    // Re-apply on DOMContentLoaded and app_ready
    $(document).ready(function() {
        applyHooks();
        setupReRoutes();
        setupBottomSaveButton();
    });
    $(document).on('app_ready', function() {
        applyHooks();
        setupReRoutes();
        setupBottomSaveButton();
    });
})();
