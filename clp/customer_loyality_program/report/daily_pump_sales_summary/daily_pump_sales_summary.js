// Copyright (c) 2026, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Pump Sales Summary"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today()
    },
    {
      fieldname: "petrol_pump",
      label: __("Petrol Pump"),
      fieldtype: "Link",
      options: "Petrol Pump Location"
    }
  ]
};
