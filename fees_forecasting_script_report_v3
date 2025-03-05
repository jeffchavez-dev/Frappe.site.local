# Copyright (c) 2025, SERVIO Enterprise and contributors
# For license information, please see license.txt

from collections import OrderedDict

import frappe
from frappe.utils import flt 
from frappe import _


def execute(filters=None):
		"""
		Executes the SQL query to fetch report data.

		Args:
			filters: Dictionary of filters applied to the report.

		Returns:
			tuple: A tuple containing:
				- columns: List of columns to be included in the report.
				- data: List of dictionaries, where each dictionary represents a row of data.
		"""
		if not filters or all(value == "" for value in filters.values()):
			return [], []  
		
		academic_year = filters.get('academic_year') 
		items = filters.get('items') 
		selected_month = filters.get('selected_month')

		columns = get_columns(filters) 
		data = get_data(filters) 
		return columns, data

def get_columns(filters):
    selected_month = filters.get('selected_month')
    columns = [
        {"fieldname": "Campus:Data:150", "fieldtype": "Data", "label": "Campus"},
        {"fieldname": "Total Students:Int:150", "fieldtype": "Int", "label": "Total Students"},
        {"fieldname": "Paying Students:Int:150", "fieldtype": "Int", "label": "Paying Students"},
        {"fieldname": "Non-Paying Student:Int:150", "fieldtype": "Int", "label": "Non-Paying Student"},
        {"fieldname": "Availed IEE:Int:150", "fieldtype": "Int", "label": "Availed IEE"},
        {"fieldname": "Regular:Int:150", "fieldtype": "Int", "label": "Regular"},
        {"fieldname": "Late Enrollees:Int:150", "fieldtype": "Int", "label": "Late Enrollees"},
    ]

    months = {  
		"May - July": "May - July:Currency/PHP:150",  
        "August": "August:Currency/PHP:150",
        "September": "September:Currency/PHP:150",
        "October": "October:Currency/PHP:150",
        "November": "November:Currency/PHP:150",
        "December": "December:Currency/PHP:150",
		"January": "January:Currency/PHP:150",
        "February": "February:Currency/PHP:150",
        "March": "March:Currency/PHP:150",
        "April": "April:Currency/PHP:150",
        "May": "May:Currency/PHP:150",
    }

    if selected_month and selected_month in months:
        month_fieldname = months[selected_month]
        columns.append({
            "fieldname": month_fieldname,
            "fieldtype": "Currency",
            "label": selected_month,
            "options": "PHP"
        })
    else:  # Default: Show all months
        for month, fieldname in months.items():
            columns.append({
                "fieldname": fieldname,
                "fieldtype": "Currency",
                "label": month,
                "options": "PHP"
            })

    remaining_columns = [
        {"fieldname": "IEE Amount:Currency/PHP:150", "fieldtype": "Currency", "label": "IEE Amount", "options": "PHP"},
        {"fieldname": "Total Regular Enrollees:Currency/PHP:150", "fieldtype": "Currency", "label": "Total Regular Enrollees", "options": "PHP"},
        {"fieldname": "Total with IEE:Currency/PHP:150", "fieldtype": "Currency", "label": "Total with IEE", "options": "PHP"},
        {"fieldname": "Total Bond:Currency/PHP:150", "fieldtype": "Currency", "label": "Total Bond", "options": "PHP"},
        {"fieldname": "Total Without Bond:Currency/PHP:150", "fieldtype": "Currency", "label": "Total Without Bond", "options": "PHP"},
    ]
    columns.extend(remaining_columns) #Extends the remaining columns to the list.

    return columns

# def get_previous_month_cash_balance(today):
#     """
#     Retrieves the cash balance at the beginning of the current month.
#     """
#     first_day_of_month = datetime.date(today.year, today.month, 1)
#     previous_month_end = first_day_of_month - datetime.timedelta(days=1)

	
#     gl_entries = frappe.db.sql(
#         """
#         SELECT SUM(`gle`.`debit` - `gle`.`credit`)
#         FROM `tabGL Entry` AS `gle`
#         WHERE `gle`.`posting_date` <= %s
#         """,
#         (previous_month_end,),
#         as_list=True,
#     )

#     if gl_entries and gl_entries[0] and gl_entries[0][0] is not None:
#         return flt(gl_entries[0][0])
#     else:
#         return 0.0

def get_actual_cash_condition(today):
    """
    Calculates the actual cash based on previous balance, collections, and disbursements.
    """

    # Calculate the previous balance of the month
    # previous_balance = get_previous_month_cash_balance(today)
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')


    # Calculate the actual collection (payment entry receive)
    actual_collection_condition = """
        SELECT SUM(`pe`.`paid_amount`)
        FROM `tabPayment Entry` AS `pe`
        WHERE `pe`.`posting_date` >= '{today_str}'
        AND `pe`.`payment_type` = 'Receive'
    """.format(today_str=today_str)

    # Calculate the actual disbursements (payment entry pay)
    actual_disbursements_condition = """
        SELECT SUM(`pe`.`paid_amount`)
        FROM `tabPayment Entry` AS `pe`
        WHERE `pe`.`posting_date` >= '{today_str}'
        AND `pe`.`payment_type` = 'Pay'
    """.format(today_str=today_str)

    actual_cash_condition = f"""
       ({actual_collection_condition}) - ({actual_disbursements_condition})
    """

    return actual_cash_condition

def get_data(filters):
		
		academic_year = filters.get('academic_year')
		items = filters.get('items')
		selected_month = filters.get('selected_month')
		print(academic_year)
		data = []

		if not items:
			return []
		
		today = datetime.date.today()
		conditions = []  
		# sql = ""

		if academic_year:
			conditions.append(f"`TabProgram Enrollment`.`academic_year` = '{academic_year}'")

			if items:
				items_list = [item.strip() for item in items.split(',')]
			
				if "Expected Total Collection" in items_list:
					conditions.append("`TabFees`.`outstanding_amount` = 0.0") # add submitted accounts only 
					conditions.append("`TabFees`.`docstatus` = 1")
				if "Current Actual Collection" in items_list:
					conditions.append("`TabFees`.`outstanding_amount` > 0.0") # compare with grand total 
				if "Account Receivable" in items_list: # reverse of Current Actual Collection
					overdue_condition = get_overdue_condition(today, filters, academic_year)
					if overdue_condition:
						conditions.append(overdue_condition)
				if "Expenses" in items_list:
					conditions.append("`gle`.`credit` > 0.0")
					# conditions.append("`ta`.`account_type` = 'Expense Account'")

				if "Projected Cash" in items_list:
					today_str = today.strftime('%Y-%m-%d')  

					projected_cash_condition = f"""
							`tabFees`.`outstanding_amount` > 0
							AND `tabFees`.`due_date` >= '{today_str}'
							AND DAY(`tabFees`.`due_date`) = 7  -- Monthly payment on the 7th
						)
					"""

					if conditions:
						where_clause = " AND ".join(conditions) + " AND " + projected_cash_condition
					else:
						where_clause = projected_cash_condition
				
				if "Actual Cash" in items_list:
					today_str = today.strftime('%Y-%m-%d')  
					# Actual collection same with Current Actual Collection
					actual_collection_condition = "`TabFees`.`outstanding_amount` > 0.0"

					# Calculate the actual disbursements (payment entry pay)
					actual_disbursements_condition = f"""
						(SELECT SUM(`pe`.`paid_amount`)
						FROM `tabPayment Entry` AS `pe`
						WHERE `pe`.`posting_date` >= '{today_str}'
						AND `pe`.`payment_type` = 'Pay')
					"""
					#Calculate the actual cash condition.
					actual_cash_condition = actual_collection_condition

					# Append as a SQL condition.
					conditions.append(actual_cash_condition)


				where_clause = " AND ".join(conditions) if conditions else "1=1" 
            
				sql = f"""
				SELECT `source`.`Campus:Data:150` AS `Campus:Data:150`,
						SUM(
							CASE
							WHEN (`source`.`PE Docstatus Aggregate` <> 0)
							OR (`source`.`PE Docstatus Aggregate` IS NULL) THEN 1
							ELSE 0.0
							END
						) AS `Total Students:Int:150`,
						SUM(
							CASE
							WHEN (`source`.`Paying Student Aggregate` <> 0)
							OR (`source`.`Paying Student Aggregate` IS NULL) THEN 1
							ELSE 0.0
							END
						) AS `Paying Students:Int:150`,
						SUM(
							CASE
							WHEN (`source`.`Non-Paying Aggregate` <> 0)
							OR (`source`.`Non-Paying Aggregate` IS NULL) THEN 1
							ELSE 0.0
							END
						) AS `Non-Paying Student:Int:150`,
						SUM(
							CASE
							WHEN (`source`.`Availed IEE Aggregate` <> 0)
							OR (`source`.`Availed IEE Aggregate` IS NULL) THEN 1
							ELSE 0.0
							END
						) AS `Availed IEE:Int:150`,
						SUM(
							CASE
							WHEN (`source`.`Regular Student Aggregate` <> 0)
							OR (`source`.`Regular Student Aggregate` IS NULL) THEN 1
							ELSE 0.0
							END
						) AS `Regular:Int:150`,
						SUM(
							CASE
							WHEN (`source`.`Late Student Aggregate` <> 0)
							OR (`source`.`Late Student Aggregate` IS NULL) THEN 1
							ELSE 0.0
							END
						) AS `Late Enrollees:Int:150`,
						SUM(`source`.`May to July OF Aggregate`) AS `May - July:Currency/PHP:150`,
						SUM(`source`.`August OF Aggregate`) AS `August:Currency/PHP:150`,
						SUM(`source`.`September OF Aggregate`) AS `September:Currency/PHP:150`,
						SUM(`source`.`October OF Aggregate`) AS `October:Currency/PHP:150`,
						SUM(`source`.`November OF Aggregate`) AS `November:Currency/PHP:150`,
						SUM(`source`.`December OF Aggregate`) AS `December:Currency/PHP:150`,
						SUM(`source`.`January OF Aggregate`) AS `January:Currency/PHP:150`,
						SUM(`source`.`February OF Aggregate`) AS `February:Currency/PHP:150`,
						SUM(`source`.`March OF Aggregate`) AS `March:Currency/PHP:150`,
						SUM(`source`.`April OF Aggregate`) AS `April:Currency/PHP:150`,
						SUM(`source`.`May OF Aggregate`) AS `May:Currency/PHP:150`,
						SUM(`source`.`IEE Amount Aggregate`) AS `IEE Amount:Currency/PHP:150`,
						SUM(`source`.`Regular Enrollees OA Aggregate`) AS `Total Regular Enrollees:Currency/PHP:150`,
						SUM(`source`.`Total with IEE Aggregate`) AS `Total with IEE:Currency/PHP:150`,
						SUM(`source`.`Total Bond Aggregate`) AS `Total Bond:Currency/PHP:150`,
						SUM(`source`.`Total Without Bond Aggregate`) AS `Total Without Bond:Currency/PHP:150`
						FROM (
							SELECT `tabStudent`.`name` AS `name`,
							SUM(
								CASE
								WHEN (
									`TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN 1
								ELSE 0.0
								END
							) AS `Availed IEE Aggregate`,
							MIN(`TabProgram Enrollment`.`campus`) AS `Campus:Data:150`,
							SUM(
								CASE
								WHEN (
									NOT (
									`TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
									)
									OR (
									`TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
									)
								)
								AND (
									`TabProgram Enrollment`.`fees_due_schedule_template` IS NOT NULL
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN 1
								ELSE 0.0
								END
							) AS `Regular Student Aggregate`,
							SUM(
								CASE
								WHEN (
									`TabProgram Enrollment`.`student_category` = 'Non-paying Student'
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1) THEN 1
								ELSE 0.0
								END
							) AS `Non-Paying Aggregate`,
							SUM(
								CASE
								WHEN (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1) THEN 1
								ELSE 0.0
								END
							) AS `Paying Student Aggregate`,
							SUM(
								CASE
								WHEN (
									`TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								)
								AND (`TabFees`.`student_cart_item` IS NULL) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `IEE Amount Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 8)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `August OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 9)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `September OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 10)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `October OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 11)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `November OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 12)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `December OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 1)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `January OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 2)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `February OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 3)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `March OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 4)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `April OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 5)
								AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_end_date`)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `May OF Aggregate`,
							SUM(
								CASE
								WHEN (MONTH(`TabFees`.`due_date`) = 5)
								OR (MONTH(`TabFees`.`due_date`) = 6)
								OR (
									(MONTH(`TabFees`.`due_date`) = 7)
									AND (
									YEAR(`TabFees`.`due_date`) = YEAR(`TabAcademic Year`.`year_start_date`)
									)
									AND (`TabProgram Enrollment`.`docstatus` = 1)
									AND (`TabFees`.`docstatus` = 1)
									AND (`TabFees`.`student_cart_item` IS NULL)
									AND (
									(
										`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
										`TabProgram Enrollment`.`student_category` IS NULL
									)
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `May to July OF Aggregate`,
							SUM(
								CASE
								WHEN (
									(
									NOT (
										`TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
									)
									OR (
										`TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
									)
									)
									OR (
									`TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
									)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								)
								AND (`TabFees`.`student_cart_item` IS NULL) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `Total with IEE Aggregate`,
							SUM(
								CASE
								WHEN (
									NOT (
									`TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
									)
									OR (
									`TabProgram Enrollment`.`fees_due_schedule_template` IS NULL
									)
								)
								AND (
									`TabProgram Enrollment`.`fees_due_schedule_template` IS NOT NULL
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								)
								AND (`TabFees`.`student_cart_item` IS NULL) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `Regular Enrollees OA Aggregate`,
							SUM(
								CASE
								WHEN (
									`TabProgram Enrollment`.`fees_due_schedule_template` LIKE '%%Late%%'
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN 1
								ELSE 0.0
								END
							) AS `Late Student Aggregate`,
							SUM(
								CASE
								WHEN (
									`TabFee Component`.`fees_category` LIKE '%%Bond%%'
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `Total Bond Aggregate`,
							SUM(
								CASE
								WHEN (
									NOT (
									`TabFee Component`.`fees_category` LIKE '%%Bond%%'
									)
									OR (`TabFee Component`.`fees_category` IS NULL)
								)
								AND (`TabProgram Enrollment`.`docstatus` = 1)
								AND (`TabFees`.`docstatus` = 1)
								AND (`TabFees`.`student_cart_item` IS NULL)
								AND (
									(
									`TabProgram Enrollment`.`student_category` <> 'Non-paying Student'
									)
									OR (
									`TabProgram Enrollment`.`student_category` IS NULL
									)
								) THEN `TabFee Component`.`amount`
								ELSE 0.0
								END
							) AS `Total Without Bond Aggregate`,
							SUM(
								CASE
								WHEN `TabProgram Enrollment`.`docstatus` = 1 THEN 1
								ELSE 0.0
								END
							) AS `PE Docstatus Aggregate`
							FROM `tabStudent`
							LEFT JOIN `tabProgram Enrollment` AS `TabProgram Enrollment` ON `tabStudent`.`name` = `TabProgram Enrollment`.`student`
							LEFT JOIN `tabFees` AS `TabFees` ON `tabStudent`.`name` = `TabFees`.`student`
							LEFT JOIN `tabAcademic Year` AS `TabAcademic Year` ON `TabProgram Enrollment`.`academic_year` = `TabAcademic Year`.`name`
							LEFT JOIN `tabFee Component` AS `TabFee Component` ON `TabFees`.`name` = `TabFee Component`.`parent`
							LEFT JOIN `tabDragonPay Payment Request` AS `TabDPPR` on `TabFees`.`dragonpay_payment_request` = `TabDPPR`.`name`
						"""
				
				
				if "Expenses" in items_list: 
					sql += """
								LEFT JOIN `tabGL Entry` AS `gle` ON `TabFees`.`name` = `gle`.`against_voucher`
								INNER JOIN `tabAccount` AS `ta` ON `gle`.`account` = `ta`.`name`
					"""

				sql += f"""
								WHERE {where_clause}
								GROUP BY `tabStudent`.`name`
								ORDER BY `tabStudent`.`name` ASC
							) AS `source`
							GROUP BY `source`.`Campus:Data:150`
							ORDER BY `source`.`Campus:Data:150` ASC
						"""

		
				data = frappe.db.sql(
							sql,
							as_dict=1
				)
        
		return data



def get_overdue_condition(today, filters, academic_year):
    """Generates the SQL condition for overdue fees."""

    case_statements = []
    if academic_year:
        for month in range(1, 13):
            # Get the last day of the month
            if month == 12:
                next_month = 1
                year = int(frappe.db.get_value("Academic Year", filters={"name":academic_year}, fieldname="year_end_date").year) + 1
            else:
                next_month = month + 1
                year = int(frappe.db.get_value("Academic Year", filters={"name":academic_year}, fieldname="year_end_date").year)
            _, last_day = calendar.monthrange(year, month)
            last_day_of_month = datetime.date(year, month, last_day)

            if last_day_of_month.year <= today.year and last_day_of_month.month < today.month or last_day_of_month.year < today.year:
                case_statements.append(
                    f"WHEN (MONTH(`TabFees`.`due_date`) = {month} AND `TabFees`.`outstanding_amount` > 0) THEN 1"
                )
            elif last_day_of_month.month == today.month and last_day_of_month.year == today.year:
                case_statements.append(
                    f"WHEN (MONTH(`TabFees`.`due_date`) = {month} AND `TabFees`.`due_date` < '{today}' AND `TabFees`.`outstanding_amount` > 0) THEN 1"
                )

    if case_statements:
        overdue_condition = f"CASE {' '.join(case_statements)} ELSE 0 END = 1"
        return overdue_condition
    else:
        return None

import calendar
import datetime
