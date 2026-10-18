frappe.dashboards.chart_sources["Top Customers"] = {
    method: "clp.api.get_top_customers_chart",
    filters: [
        {
            fieldname: "limit",
            label: __("Top"),
            fieldtype: "Select",
            options: "5\n10\n15\n20",
            default: "10"
        }
    ]
};
