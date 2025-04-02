frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Fotara Status"] = {
	// method: "erpnext.stock.dashboard_chart_source.warehouse_wise_stock_value.warehouse_wise_stock_value.get",
	method: "jo_fotara.jo_fotara.dashboard_chart_source.fotara_status.fotara_status.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
	],
};