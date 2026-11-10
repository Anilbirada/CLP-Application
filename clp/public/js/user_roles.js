frappe.ui.form.on("User", {
    refresh(frm) {
        // Direct Profile Photo Upload Button on User Form
        if (frm.doc.name === frappe.session.user || frappe.user.has_role("System Manager")) {
            frm.add_custom_button(__("📷 Upload Profile Photo"), () => {
                new frappe.ui.FileUploader({
                    doctype: "User",
                    docname: frm.doc.name,
                    folder: "Home/Attachments",
                    restrictions: {
                        allowed_file_types: ["image/*"]
                    },
                    on_success: (file_doc) => {
                        frappe.call({
                            method: "clp.api.update_profile_photo",
                            args: {
                                photo_url: file_doc.file_url,
                                user: frm.doc.name
                            },
                            freeze: true,
                            freeze_message: __("Updating profile photo..."),
                            callback: (r) => {
                                if (r.message && r.message.success) {
                                    frm.set_value("user_image", file_doc.file_url);
                                    frappe.show_alert({
                                        message: __("Profile photo updated successfully!"),
                                        indicator: "green"
                                    });
                                    setTimeout(() => window.location.reload(), 600);
                                }
                            }
                        });
                    }
                });
            }).css({
                "background-color": "#1769AA",
                "color": "#FFFFFF",
                "font-weight": "600"
            });
        }

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
