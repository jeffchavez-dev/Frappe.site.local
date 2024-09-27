def calculate_thirteen_month:
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

calculate