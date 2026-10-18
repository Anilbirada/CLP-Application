// Copyright (c) 2026, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["CLP Activity Audit Report"] = {
  filters: [
    {
      fieldname: "from_datetime",
      label: __("From Date & Time"),
      fieldtype: "Datetime",
      default: frappe.datetime.add_days(frappe.datetime.now_datetime(), -7)
    },
    {
      fieldname: "to_datetime",
      label: __("To Date & Time"),
      fieldtype: "Datetime",
      default: frappe.datetime.now_datetime()
    },
    {
      fieldname: "actor",
      label: __("User"),
      fieldtype: "Link",
      options: "User"
    },
    {
      fieldname: "reference_doctype",
      label: __("Document Type"),
      fieldtype: "Select",
      options: "\nLoyalty Customer\nFuel Purchase Entry\nGift Redemption\nGift Stock Request\nUser\nReferral Reward Entry\nCLP Customer Balance Adjustment"
    },
    {
      fieldname: "action",
      label: __("Action"),
      fieldtype: "Data"
    }
  ]
};
