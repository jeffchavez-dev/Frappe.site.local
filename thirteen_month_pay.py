def calculate_13th_month(salary_slip):
    """Calculates the 13th month based on salary components tagged as part of 13th month pay."""

    employee = salary_slip.employee
    start_date = salary_slip.start_date # 12/24 (Da Vinci) | 12/28 (HHI) previous year
    
    end_date = salary_slip.end_date # 12/08 (Da Vinci) | 12/12 (HHI)current year
    
    frappe.msgprint(f"start_date: {start_date}")
    frappe.msgprint(f"end_date: {end_date}")
    
    
    posting_date = salary_slip.posting_date
    
    month_day = str(posting_date.split("-")[1]) + "-" + str(posting_date.split("-")[2])
    day = str(posting_date.split("-")[2])
    
    month_day
    frappe.msgprint(f"posting_date: {posting_date}")
    frappe.msgprint(f"posting_date: {month_day}")
   
    if month_day == "12-15":
        earnings_to_show = []
        for row in salary_slip.earnings:
            if row.salary_component == "PH - 13th Month Pay":
                thirteen_month = row.amount
                earnings_to_show.append(row)
        salary_slip.earnings = earnings_to_show
        
    salary_slip.thirteen_month_pay = thirteen_month
    frappe.msgprint(f"thirteen_month: {thirteen_month}")    
    frappe.msgprint(f"salary_slip.thirteen_month_pay: {salary_slip.thirteen_month_pay}")    
    # frappe.get_doc("BIR Form 2316")
  
    
calculate_13th_month(salary_slip)