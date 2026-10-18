// Copyright (c) 2026, Aman Boora and contributors
// For license information, please see license.txt

frappe.ui.form.on('CLP Customer Balance Adjustment', {
    setup: function(frm) {
        frm.set_query('customer', function() {
            return {
                query: 'clp.api.get_customers_for_search'
            };
        });
    },

    customer: function(frm) {
        if (frm.doc.customer) {
            frappe.db.get_value('Loyalty Customer', frm.doc.customer, 'current_cycle_liters', function(r) {
                if (r) {
                    frm.set_value('previous_balance', r.current_cycle_liters || 0);
                    calculate_new_balance(frm);
                }
            });
        }
    },

    adjustment_type: function(frm) {
        calculate_new_balance(frm);
    },

    points: function(frm) {
        calculate_new_balance(frm);
    }
});

function calculate_new_balance(frm) {
    let prev = flt(frm.doc.previous_balance || 0);
    let pts = flt(frm.doc.points || 0);
    let type = frm.doc.adjustment_type;

    if (type === 'Add Points') {
        frm.set_value('new_balance', prev + pts);
    } else if (type === 'Subtract Points') {
        frm.set_value('new_balance', Math.max(0, prev - pts));
    } else {
        frm.set_value('new_balance', prev);
    }
}
