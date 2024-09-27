


# government deduction

def calculate_government_deduction(doc):
    
    emp = doc.employee 
    frappe.msgprint(f"Emp: {emp}")   
    
    components_as_gov_contribution = frappe.get_list(
        'Salary Component',
        fields=["salary_component", "salary_component_abbr","type", "government_contribution"],
        filters = ["government_contribution"],
        # limit = 1
        )
        
    components_as_overtime = frappe.get_list(
        'Salary Component',
        fields=["salary_component", "salary_component_abbr","type", "is_overtime_pay"],
        filters = ["is_overtime_pay"],
        # limit = 1
        
        )
    
    if components_as_overtime:
        total_amount_ot = 0
        for overtime in components_as_overtime:
            frappe.msgprint(f"With Over Time {overtime.salary_component_abbr}")
            
            sql_query = """
               SELECT
                    ss.employee,
                    sd.abbr,
                    sd.amount,
                    ss.posting_date
                FROM
                    `tabSalary Slip` ss
                LEFT JOIN
                    `tabSalary Detail` sd ON
                    sd.parent = ss.name  -- Linking deductions to the filtered Salary Slip
                WHERE
                    ss.employee = %(emp)s 
                    AND sd.abbr = %(abbr)s
                    AND ss.docstatus = 1  -- Filter based on the 'emp' variable 
                    
                ORDER BY
                    ss.posting_date ASC  -- Ordering by posting date
                """
            
            result = frappe.db.sql(sql_query, {'emp': emp, 'abbr': overtime.salary_component_abbr}, as_dict=True)
            
            if result:
                for row in result:
                    frappe.msgprint(f"Employee: {row.employee}, Salary Component: {row.abbr} Amount: {row.amount} on {row.posting_date}")
                    total_amount_ot = total_amount_ot + row.amount
                    frappe.msgprint(f"total_amount_ot {total_amount_ot}")
                    doc.overtime_pay = total_amount_ot
            else:
                frappe.msgprint("no result")
                
    else:
        frappe.msgprint("No Component with Overtime")
        
    # frappe.msgprint(f"total_amount_ot {total_amount_ot}")
    
        
    if components_as_gov_contribution:
        total_amount_gov = 0
        for com in components_as_gov_contribution:
            # frappe.msgprint(f"Name: {com.salary_component_abbr}")   
            
            
            sql_query = """
               SELECT
                    ss.employee,
                    sd.abbr,
                    sd.amount,
                    ss.posting_date
                FROM
                    `tabSalary Slip` ss
                LEFT JOIN
                    `tabSalary Detail` sd ON
                    sd.parent = ss.name  -- Linking deductions to the filtered Salary Slip
                WHERE
                    ss.employee = %(emp)s 
                    AND sd.abbr = %(abbr)s
                    AND ss.docstatus = 1  -- Filter based on the 'emp' variable 
                    
                ORDER BY
                    ss.posting_date ASC  -- Ordering by posting date
                """
            
            result = frappe.db.sql(sql_query, {'emp': emp, 'abbr': com.salary_component_abbr}, as_dict=True)
        
            if result:
                for row in result:
                    # frappe.msgprint(f"Employee: {row.employee}, Salary Component: {row.abbr} Amount: {row.amount} on {row.posting_date}")
                    total_amount_gov = total_amount_gov + row.amount
                    frappe.msgprint(f"total_amount_gov_con {total_amount}")
                    doc.contributions = total_amount_gov
            else:
                frappe.msgprint("no result")
                
    # frappe.msgprint(f"total_amount_final {total_amount_gov}")   
    

    
    
    
    
    salary_component = "PH_13M_1"
    
    thirteen_month_query = """
               SELECT
                    ss.employee,
                    sd.abbr,
                    sd.amount,
                    ss.posting_date
                FROM
                    `tabSalary Slip` ss
                LEFT JOIN
                    `tabSalary Detail` sd ON
                    sd.parent = ss.name  -- Linking deductions to the filtered Salary Slip
                WHERE
                    ss.employee = %(emp)s 
                    AND sd.abbr = %(abbr)s
                    AND ss.docstatus = 1  -- Filter based on the 'emp' variable 
                    
                ORDER BY
                    ss.posting_date DESC  -- Ordering by posting date
                LIMIT 1
                """
            
    thirteen_month_comp = frappe.db.sql(thirteen_month_query, {'emp': emp, 'abbr': salary_component}, as_dict=True)
        
        
    if thirteen_month_comp:
      if isinstance(thirteen_month_comp, list):
        for row in thirteen_month_comp:
          frappe.msgprint(f"TWO only")
          frappe.msgprint(f"employee {row['employee']}")
          frappe.msgprint(f"posting_date {row['posting_date']}")
          frappe.msgprint(f"thirteen_month {row['abbr']}")
          frappe.msgprint(f"thirteen_month {row['amount']}")
          thirteen_month_amount = row['amount']
 
 
    doc.other_benefits_mwe = thirteen_month_amount
    frappe.msgprint(f"contributions: {doc.contributions}")
    
calculate_government_deduction(doc)





# # # display 13th month pay
# def display_thirteen_month(doc):
    
    #     posting_date = "12"
    # thirteen_month = frappe.get_list("Salary Slip",
    #     filters={"employee": emp },
    #     fields=["employee", "thirteen_month_pay", "posting_date"],
    #     limit = 1
    #     )
# display_thirteen_month(doc)
    
