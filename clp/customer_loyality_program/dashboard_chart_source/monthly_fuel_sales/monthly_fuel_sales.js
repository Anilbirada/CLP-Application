frappe.dashboards.chart_sources["Monthly Fuel Sales"] = {
    method: "clp.api.get_monthly_fuel_sales",
    filters: [
        {
            fieldname: "months",
            label: __("Months"),
            fieldtype: "Select",
            options: "3\n6\n12",
            default: "6"
        }
    ]
};
