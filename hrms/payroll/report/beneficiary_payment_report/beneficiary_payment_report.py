# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import getdate, add_months

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Beneficiary Name", "fieldname": "beneficiary_name", "fieldtype": "Data", "width": 200},
        {"label": "Bank Name", "fieldname": "bank", "fieldtype": "Data", "width": 180},
        {"label": "Account Name", "fieldname": "bank_account_name", "fieldtype": "Data", "width": 180},
        {"label": "Account Number", "fieldname": "bank_ac_no","fieldtype": "Data", "width": 160},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        
    ]


def get_data(filters):

    conditions = ["bp.docstatus = 1"]
    params = {}

    if filters.get("beneficiary_name"):
        conditions.append("bp.beneficiary_name = %(beneficiary_name)s")
        params["beneficiary_name"] = filters.get("beneficiary_name")

    if filters.get("from_date"):
        conditions.append("bp.payment_date >= %(from_date)s")
        params["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("bp.payment_date <= %(to_date)s")
        params["to_date"] = filters.get("to_date")

    if filters.get("from_month") and filters.get("to_month"):
        month_list = get_months_in_range(filters.get("from_month"), filters.get("to_month"))
        month_strings = [m.strftime("%Y-%m") for m in month_list]

        conditions.append("DATE_FORMAT(bp.payment_date, '%%Y-%%m') IN %(months)s")
        params["months"] = tuple(month_strings)

    query = f"""
        SELECT
            bp.beneficiary_name,
            bp.bank,
            bp.bank_account_name,
            bp.bank_ac_no,
            bp.amount,
            bp.payment_date,
            DATE_FORMAT(bp.payment_date, '%%Y-%%m') AS month
        FROM `tabBeneficiary Payment` bp
        WHERE {" AND ".join(conditions)}
        ORDER BY bp.payment_date DESC
    """

    return frappe.db.sql(query, params, as_dict=True)


def get_months_in_range(start_month, end_month):
    months = []
    current_month = getdate(start_month + "-01").replace(day=1)
    end_date = getdate(end_month + "-01").replace(day=1)

    while current_month <= end_date:
        months.append(current_month)
        current_month = add_months(current_month, 1)

    return months
