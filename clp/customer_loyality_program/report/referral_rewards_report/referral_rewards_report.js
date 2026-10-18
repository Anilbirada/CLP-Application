frappe.query_reports["Referral Rewards Report"] = {
  filters: [
    {fieldname: "from_datetime", label: __("From Date & Time"), fieldtype: "Datetime"},
    {fieldname: "to_datetime", label: __("To Date & Time"), fieldtype: "Datetime"},
    {fieldname: "petrol_pump", label: __("Petrol Pump"), fieldtype: "Link", options: "Petrol Pump Location"},
    {fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nAwarded\nReversed"}
  ]
};
