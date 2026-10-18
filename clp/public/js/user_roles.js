frappe.ui.form.on("User", {
    refresh(frm) {
        if (frappe.user.has_role("System Manager") || frappe.user.has_role("Pump Owner")) {
            frm.add_custom_button(__("Manage CLP Roles"), () => {
                const managed = [
                    "Pump Manager", "CLM Incharge", "Pump Owner",
                    "CLP Stock Add", "CLP Stock Subtract", "CLP Stock Transfer",
                    "CLP Reports Viewer", "CLP Referral Manager"
                ];
                const existing = (frm.doc.roles || []).map(r => r.role);
                const fields = managed.map(role => ({
                    fieldtype: "Check", fieldname: "role_" + role.toLowerCase().replace(/[^a-z0-9]+/g, "_"),
                    label: role, default: existing.includes(role)
                }));
                const d = new frappe.ui.Dialog({
                    title: __("Manage CLP Roles"), fields,
                    primary_action_label: __("Save Roles"),
                    primary_action(values) {
                        const selected = managed.filter(role => values["role_" + role.toLowerCase().replace(/[^a-z0-9]+/g, "_")]);
                        frappe.call({
                            method: "clp.api.set_user_roles",
                            args: { user: frm.doc.name, roles: selected },
                            freeze: true,
                            freeze_message: __("Updating roles..."),
                            callback(r) {
                                if (!r.exc) {
                                    frappe.show_alert({message: __("CLP roles updated"), indicator: "green"});
                                    d.hide(); frm.reload_doc();
                                }
                            }
                        });
                    }
                });
                d.show();
            });
        }
    }
});
