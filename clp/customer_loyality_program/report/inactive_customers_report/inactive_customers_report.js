// Copyright (c) 2026, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Inactive Customers Report"] = {
  filters: [
    {
      fieldname: "days_inactive",
      label: __("Days Since Last Purchase"),
      fieldtype: "Select",
      options: "30\n60\n90\n180",
      default: "60"
    },
    {
      fieldname: "registration_pump",
      label: __("Registration Pump"),
      fieldtype: "Link",
      options: "Petrol Pump Location"
    }
  ]
};
