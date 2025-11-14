# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# -*- coding: utf-8 -*-
import frappe
from frappe.utils import getdate, add_months

def execute(filters=None):
    if filters is None:
        filters = {}

    # Fetch Salary Slips with project/cost_center from Payroll Entry and designation from Employee
    salary_slips = get_salary_slips(filters)

    # Get all unique salary components for these salary slips
    components = get_unique_components(salary_slips)

    # Build columns dynamically
    columns = get_columns(components)

    # Build data
    data = get_data(salary_slips, components)

    return columns, data

def get_salary_slips(filters):
    conditions = ["ss.docstatus = 1"]
    params = {}

    if filters.get("company"):
        conditions.append("ss.company = %(company)s")
        params["company"] = filters.get("company")
    if filters.get("employee"):
        conditions.append("ss.employee = %(employee)s")
        params["employee"] = filters.get("employee")
    if filters.get("project"):
        conditions.append("pe.project = %(project)s")
        params["project"] = filters.get("project")
    if filters.get("designation"):
        conditions.append("e.designation = %(designation)s")
        params["designation"] = filters.get("designation")
    if filters.get("from_date"):
        conditions.append("ss.start_date >= %(from_date)s")
        params["from_date"] = filters.get("from_date")
    if filters.get("to_date"):
        conditions.append("ss.end_date <= %(to_date)s")
        params["to_date"] = filters.get("to_date")

    # Join with Employee for designation, Payroll Entry for project & cost_center
    query = f"""
        SELECT
            ss.name AS salary_slip,
            ss.employee,
            ss.employee_name,
            e.designation,
            pe.project,
            pe.cost_center,
            ss.start_date,
            ss.end_date
        FROM `tabSalary Slip` ss
        LEFT JOIN `tabEmployee` e ON e.name = ss.employee
        LEFT JOIN `tabPayroll Entry` pe ON pe.name = ss.payroll_entry
        WHERE {" AND ".join(conditions)}
        ORDER BY ss.start_date DESC
    """
    return frappe.db.sql(query, params, as_dict=True)

def get_unique_components(salary_slips):
    if not salary_slips:
        return []

    salary_slip_names = [d.salary_slip for d in salary_slips]
    components = frappe.db.sql("""
        SELECT DISTINCT salary_component
        FROM `tabSalary Detail`
        WHERE parent IN (%s)
    """ % (", ".join(["%s"]*len(salary_slip_names))), tuple(salary_slip_names), as_list=True)

    return [c[0] for c in components]

def get_columns(components):
    cols = [
        {"label": "Employee", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 120},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150},
        {"label": "Project", "fieldname": "project", "fieldtype": "Data", "width": 200},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Data", "width": 150},
        {"label": "Salary Slip", "fieldname": "salary_slip", "fieldtype": "Link", "options": "Salary Slip", "width": 150},
        {"label": "From Date", "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": "To Date", "fieldname": "end_date", "fieldtype": "Date", "width": 100},
    ]

    for comp in components:
        cols.append({
            "label": comp,
            "fieldname": frappe.scrub(comp),
            "fieldtype": "Currency",
            "width": 120
        })

    cols += [
        {"label": "Total Earnings", "fieldname": "total_earnings", "fieldtype": "Currency", "width": 150},
        {"label": "Total Deductions", "fieldname": "total_deductions", "fieldtype": "Currency", "width": 150},
        {"label": "Net Pay", "fieldname": "net_pay", "fieldtype": "Currency", "width": 150},
    ]
    return cols

def get_data(salary_slips, components):
    data = []
    for ss in salary_slips:
        row = ss.copy()

        # Initialize salary components to 0
        for comp in components:
            row[frappe.scrub(comp)] = 0

        # Fetch components and their type from Salary Component doctype
        details = frappe.db.sql("""
            SELECT sd.salary_component, sd.amount, sc.type AS salary_component_type
            FROM `tabSalary Detail` sd
            LEFT JOIN `tabSalary Component` sc ON sc.name = sd.salary_component
            WHERE sd.parent = %s
        """, ss.salary_slip, as_dict=True)

        total_earnings = 0
        total_deductions = 0
        for d in details:
            fieldname = frappe.scrub(d.salary_component)
            row[fieldname] = d.amount
            if d.salary_component_type == "Earning":
                total_earnings += d.amount
            else:
                total_deductions += d.amount

        row["total_earnings"] = total_earnings
        row["total_deductions"] = total_deductions
        row["net_pay"] = total_earnings - total_deductions

        data.append(row)

    return data

def get_months_in_range(start_date, end_date):
    """Generate all months in the range from start_date to end_date"""
    months = []
    current_month = getdate(start_date).replace(day=1)
    end_date = getdate(end_date)

    while current_month <= end_date:
        months.append(current_month)
        current_month = add_months(current_month, 1)

    return months
