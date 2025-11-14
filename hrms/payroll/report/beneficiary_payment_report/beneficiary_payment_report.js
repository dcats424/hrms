// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Beneficiary Payment Report"] = {
	"filters": [

		{
            "fieldname": "beneficiary_name",
            "label": __("Beneficiary Name"),
            "fieldtype": "Data",
        },

		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
			"default":frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
			"default":frappe.datetime.month_end()
        }

	]
};
