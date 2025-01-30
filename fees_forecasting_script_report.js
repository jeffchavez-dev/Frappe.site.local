// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Fees Forecasting"] = {
	filters: [
		{
			fieldname: "academic_year",
			label: __("Academic Year"),
			fieldtype: "Link",
			options: "Academic Year"
		},
		{
			fieldname: "items",
			label: __("Items"),
			fieldtype: "Select",
			options: "Expected Total Collection\nCurrent Actual Collection\nAccount Receivable\nExpenses\nProjected Cash\nActual Cash"
		}
	
	],
};

erpnext.utils.add_dimensions("Fees", 15);
