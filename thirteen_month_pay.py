def calculate_13th_month(salary_slip):
    
    employee = salary_slip.employee
    start_date = salary_slip.start_date 
    end_date = salary_slip.end_date 
    
    posting_date = salary_slip.posting_date
    
    posting_month_day = str(posting_date.split("-")[1]) + "-" + str(posting_date.split("-")[2])
    start_month_day = str(start_date.split("-")[1]) + "-" + str(start_date.split("-")[2])
    end_month_day = str(end_date.split("-")[1]) + "-" + str(end_date.split("-")[2])
    # frappe.msgprint(f"posting_date: {posting_date}")
    # frappe.msgprint(f"posting_date: {month_day}")
   
    thirteen_month = 0
    if posting_month_day == "12-08" or posting_month_day == "12-24":
        for row in salary_slip.earnings:
            if row.salary_component == "PH - 13th Month Pay":
                thirteen_month = row.amount
                row.amount = 0
                salary_slip.thirteen_month_pay = 0
                # salary_slip.net_pay = salary_slip.net_pay - thirteen_month
                # salary_slip.rounded_total = round(salary_slip.rounded_total - thirteen_month, 0)
                # salary_slip.gross_pay = salary_slip.gross_pay - thirteen_month
      
    if posting_month_day == "12-15":
        try:
            if start_month_day != "12-01" and end_month_day != "12-15":
                frappe.msgprint(f"{start_month_day} and {end_month_day}")
                frappe.msgprint("Start and End Date must be 12-15")
                components_to_show = []
                for row in salary_slip.earnings:
                            components_to_show.append(row)
                
                return
            else: 
                components_to_show = []
                for row in salary_slip.earnings:
                        if row.salary_component == "PH - 13th Month Pay":
                            thirteen_month = row.amount
                            components_to_show.append(row)
                for row in salary_slip.deductions:
                            components_to_show.append(row)
                for row in salary_slip.statistical_earnings:
                            components_to_show.append(row)
                for row in salary_slip.statistical_deductions:
                            components_to_show.append(row)
                salary_slip.earnings = components_to_show
                salary_slip.basic_pay = 0
                salary_slip.net_pay = thirteen_month
                salary_slip.rounded_total = thirteen_month
                salary_slip.gross_pay = thirteen_month
                salary_slip.thirteen_month_pay = thirteen_month
        except ValueError:
            frappe.msgprint("Invalid date format or missing data.")
    
    # frappe.msgprint(f"thirteen_month: {thirteen_month}")    
    # frappe.msgprint(f"salary_slip.thirteen_month_pay: {salary_slip.thirteen_month_pay}")    

     if posting_month_day != "12-15":
        hide_thirteen_month = []
        for row in salary_slip.earnings:
            if row.salary_component != "DV - 13th Month Pay":
                # frappe.msgprint("Cut off not 12-15")
                hide_thirteen_month.append(row)
        salary_slip.earnings = hide_thirteen_month
        
    
    frappe.msgprint(f"thirteen_month: {thirteen_month}")    
  

    

    
calculate_13th_month(doc)