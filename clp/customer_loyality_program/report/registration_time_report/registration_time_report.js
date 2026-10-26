frappe.query_reports["Registration Time Report"] = {
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
