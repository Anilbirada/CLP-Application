// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Registration Time Analysis"] = {
  filters: [
    {
      fieldname: "start_datetime",
      label: __("Start Date & Time"),
      fieldtype: "Datetime",
      reqd: 1,
      default: frappe.datetime.add_months(frappe.datetime.now_datetime(), -1)
    },
    {
      fieldname: "end_datetime",
      label: __("End Date & Time"),
      fieldtype: "Datetime",
      reqd: 1,
      default: frappe.datetime.now_datetime()
    },
    {
      fieldname: "registration_pump",
      label: __("Registration Pump"),
      fieldtype: "Link",
      options: "Petrol Pump Location"
    }
  ]
};
