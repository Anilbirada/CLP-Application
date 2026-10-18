// Copyright (c) 2026, Aman Boora and contributors
// For license information, please see license.txt

frappe.query_reports["Gift Item Stock Ledger Report"] = {
  filters: [
    {
      fieldname: "petrol_pump",
      label: __("Petrol Pump"),
      fieldtype: "Link",
      options: "Petrol Pump Location"
    },
    {
      fieldname: "gift_item",
      label: __("Gift Item"),
      fieldtype: "Link",
      options: "Item"
    },
    {
      fieldname: "voucher_type",
      label: __("Transaction Type"),
      fieldtype: "Select",
      options: "\nStock Addition\nStock Subtraction\nGift Redemption\nStock Transfer In\nStock Transfer Out\nOpening Balance"
    },
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
    }
  ]
};
