def recalculate_salary_slip(salary_slip):
    if salary_slip.payroll_frequency != "Bimonthly":
        return  # Exit the function if not "Bimonthly"
    # Cut-offs
    # 1.21 -- 02.04 > 2.08
    # 2.05 -- 02.20 > 2.24
    employee = salary_slip.employee
    start_date = salary_slip.start_date
    end_date = salary_slip.end_date
    posting_date = salary_slip.posting_date
    posting_date_str = str(posting_date)
    # frappe.msgprint(f"posting_date_str {posting_date_str}")
    posting_date_date = posting_date_str.split(" ")
    posting_date_list = posting_date_date[0].split("-")
    # frappe.msgprint(f"posting_date {posting_date_list}")
    employee_doc = frappe.get_doc("Employee", employee)
    employee_date_joined = str(employee_doc.date_of_joining)
    # frappe.msgprint(f"Joined: {employee_date_joined}")
    
    
    absence_query = """
    SELECT
        COUNT(*) AS total_absences
    FROM
        `tabAttendance` AS attendance
    WHERE
        attendance.employee = %s
        AND attendance.attendance_date BETWEEN %s AND %s
        AND attendance.status = 'Absent'
    """
    result = frappe.db.sql(absence_query, (employee, start_date, end_date), as_dict=True)

    # Access the total_absences value from the result
    
    
    if result:
        total_absences = result[0]['total_absences']
        salary_slip.absent_days = total_absences
    else:
        # Handle the case where no results are found
        total_absences = 0  # Set a default value or raise an exception
    
    

    # frappe.msgprint(f" Absent: {salary_slip.absent_days}") 
    
    
    salary_structure_assignment = frappe.get_all(
        "Salary Structure Assignment",
        filters={"employee": employee, "docstatus": 1},
        fields=["name"],
        order_by="creation DESC",
        limit=1,
    )
    
    base_wage = 0 
    days_of_work_per_year = 0
    if salary_structure_assignment:
        assignment_doc = frappe.get_doc(
            "Salary Structure Assignment", salary_structure_assignment[0].name
        )
        # Get the daily_hours from the Salary Structure Assignment
        daily_hours = assignment_doc.daily_hours
        base_wage = assignment_doc.base
        days_of_work_per_year = int(assignment_doc.days_of_work_per_year)
        
    # frappe.msgprint(f"Base: {base_wage}")
    
    daily_rate = (base_wage * 12) / days_of_work_per_year
    # frappe.msgprint(f"daily_rate: {daily_rate}")
    
    

                
    dv_lwop = 0
    
    for row in salary_slip.earnings:
            if row.salary_component == "DV - LWOP":
                dv_lwop = total_absences * -daily_rate
                row.amount = dv_lwop

                
                
    # check components tagged as basic Pay
    components_is_basic_pay = frappe.get_list(
        'Salary Component',
        fields=["salary_component"#, "salary_component_abbr","type", "is_overtime_pay", "is_basic_pay"
        ],
        filters = ["is_basic_pay"],
        # limit = 1
    )
    
    # get all sc tagged as is_basic_pay
    all_basic_pay = []
    if components_is_basic_pay:
        for is_basic_pay in components_is_basic_pay:
            all_basic_pay.append(is_basic_pay.salary_component)
            # frappe.msgprint(f"is_basic_pay: {all_basic_pay}")
        
        total_basic_pay = 0
        for row in salary_slip.earnings:
            
            if row.salary_component in all_basic_pay:
                # frappe.msgprint(f"is_basic_pay and in_slip: {row.salary_component}")
                total_basic_pay = total_basic_pay + row.amount

    # frappe.msgprint(f"total_basic_pay: {total_basic_pay}")

    
    total_earnings_row_amount = 0        
    for row in salary_slip.earnings:
            total_earnings_row_amount = total_earnings_row_amount + row.amount
    
    
    salary_slip.gross_pay = total_earnings_row_amount
    salary_slip.basic_pay = total_basic_pay
    
    
    
    components_is_statistical = frappe.get_list(
        'Salary Component',
        fields=["salary_component", "statistical_component", "salary_component_abbr", "type", "amount"
        ],
        filters = ["statistical_component"],
    )
    
    if components_is_statistical:
        statistical_components = []
        statistical_deductions = []
        for statistical in components_is_statistical:
            statistical_components.append(statistical.salary_component)
            # frappe.msgprint(f"statistical: {statistical_components}")
            if statistical.type == "Deduction":
                statistical_deductions.append(statistical.salary_component)
                # frappe.msgprint(f"statistical_deductions: {statistical_deductions}")


    
 
    if employee_doc and employee_doc.date_of_joining:
        employee_date_joined = str(employee_doc.date_of_joining)
        # Split the date strings into lists
        
    
        # Assuming YYYY-MM-DD format, calculate days using arithmetic
        try:
            # frappe.msgprint(f"Employee joined: {employee_date_joined}")
            # if posting_date:
            #     posting_date_list = posting_date.split("-")
            #     frappe.msgprint(f"posting_date_list: {posting_date_list}")
            # else:
            #     frappe.msgprint(f"check posting date")
                
            date_joined_list = employee_date_joined.split("-")
            
            if len(posting_date_list) != 3 or len(date_joined_list) != 3:
                frappe.throw("Invalid date format in posting date or date of joining.")
            
            # Calculate year, month, and day differences
            total_days = 0
            year_diff = int(posting_date_list[0]) - int(date_joined_list[0])
            if year_diff == 0:
                month_diff = int(posting_date_list[1]) - int(date_joined_list[1])
                if month_diff == 0:
                   total_days = 0
                #   frappe.msgprint(f"Less than 30 days")
                elif month_diff >= 1:
                    day_diff = int(posting_date_list[2]) - int(date_joined_list[2])
                    if day_diff < 0 and month_diff == 1:
                        total_days = abs(int(posting_date_list[2]) - int(date_joined_list[2]))
                        # frappe.msgprint(f"Still less than 30 days {day_diff}")
                    else:
                        total_days = day_diff = int(posting_date_list[2]) - int(date_joined_list[2])
                        total_days = day_diff + (month_diff * 30)
                        # frappe.msgprint(f"Month > 1: {total_days}")
            else:
                total_days = 30 + (year_diff * 365)
                # frappe.msgprint(f"More than a year : {total_days}")

        except ValueError:
            frappe.msgprint("Invalid date format or missing data.")
    else:
        frappe.msgprint("Employee's date of joining is not set.")
    
    
    
    filters = {
                "employee": employee,
                "end_date": ("<", start_date),
                "docstatus": 1  # Consider only submitted salary slips
    }
        
    previous_slip = frappe.get_list("Salary Slip", filters=filters, fields=["name"], limit=1, order_by="end_date desc")
    
    previous_cut_off_gross = 0
    previous_cut_off_basic_pay = 0
    if previous_slip:
        previous_slip_name = previous_slip[0].name
        previous_slip_doc = frappe.get_doc("Salary Slip", previous_slip_name)
        previous_cut_off_basic_pay = previous_slip_doc.basic_pay
        previous_cut_off_gross = previous_slip_doc.gross_pays
        # frappe.msgprint(f"previous_cut_off_basic_pay: {previous_cut_off_basic_pay}")
        # previous_total_taxable_income = previous_slip_doc.total_taxable_income
        # salary_slip.previous_cut_off_basic_pay = previous_cut_off_basic_pay
    

    
    posting_date_day = posting_date_date[0].split("-")[2]
    
    if posting_date_day == "24" and total_days >= 30:
        # frappe.msgprint(f"Posting Day is: " + posting_date_day)
            
        hdmf = 0
        gross_pay = salary_slip.gross_pay
        for row in salary_slip.deductions:
            if row.salary_component == "PH - HDMF Contribution":
                
                if gross_pay <= 1500:
                    hdmf = 0.01 * gross_pay
                elif gross_pay >= 5000:
                    hdmf = 200
                else:
                    hdmf = 0.02 * gross_pay
                row.amount = hdmf
                # frappe.msgprint(f"HDMF: {row.amount}")
                
        phic = (0.05 * base_wage) * 0.5
        
        for row in salary_slip.deductions:
            if row.salary_component == "PH - PHIC Contribution":
                row.amount = phic
                # frappe.msgprint(f"phic: {phic}")
                
            if row.salary_component == "PH - HDMF Contribution":
                row.amount = hdmf

        for row in salary_slip.statistical_deductions:
            if row.salary_component == "PH - PHIC Employer Contribution":
                frappe.msgprint(f"PHIC ER")
                row.amount = phic
            if row.salary_component == "PH - HDMF Employer Contribution":
                frappe.msgprint(f"HDMF ER")
                row.amount = hdmf
        
        #calculate SSS Contribution        
        sss_contribution = frappe.get_doc("SSS Contribution", "SSS TABLE 2023")
        sss_contribution_table = sss_contribution.contribution_table
        
        
        # frappe.msgprint(f"For SSS {salary_slip.basic_pay + previous_cut_off_basic_pay}")
        # frappe.msgprint(f"previous_cut_off_basic_pay {previous_cut_off_basic_pay}")
        if sss_contribution_table:
            for table in sss_contribution_table:
                if table.from_amount <= (salary_slip.basic_pay + previous_cut_off_basic_pay):
                    if table.from_amount <= (salary_slip.basic_pay + previous_cut_off_basic_pay) <= table.to_amount:
                        employee_con = table.employee_contribution
                        employer_con = table.employer_contribution
                        employee_com = table.employee_compensation
                        mdf = table.mpf_employee_contribution
                        # frappe.msgprint(f"MDF {mdf}")
                        sss_con = employee_con + mdf
                        break
            
            for row in salary_slip.deductions:
                if row.salary_component == "PH - SSS Contribution":
                    #  frappe.msgprint(f"SSS CONTRI")
                     row.amount = sss_con  
                        
            for row in salary_slip.statistical_deductions:
                if row.salary_component == "PH - SSS Employee Compensation":
                    frappe.msgprint(f"SSS EMP")
                    row.amount = employee_com
                elif row.salary_component == "PH - SSS Employer Contribution":
                    frappe.msgprint(f"SSS ER")
                    row.amount = employer_con
                
                
            total_earnings = sum(row.amount for row in salary_slip.earnings) 
            total_deduction = 0
            total_taxable_deduction = 0
            
            total_deduction = hdmf + phic + sss_con #use later for calculation of withholding tax
                
        

            #calculate PH-Withholding Tax
        ph_withholding_tax_table = frappe.get_doc("PH Withholding Tax Table", "2018 - 2022")
        ph_withholding_tax_slabs = ph_withholding_tax_table.slabs
        withholding_percent = 0
        from_amount = 0
        ph_withholding = 0
        monthly_gross = 0


        if ph_withholding_tax_slabs:
            mothly_gross = previous_cut_off_gross + salary_slip.gross_pay
            frappe.msgprint("PH_tax shows")
            for ph_withholding_tax_slab in ph_withholding_tax_slabs:
                # use gross_pay instead of basic pay
                if ph_withholding_tax_slab.from_amount <= mothly_gross <= ph_withholding_tax_slab.to_amount:
                    withholding_percent = ph_withholding_tax_slab.percent_withheld
                    from_amount = ph_withholding_tax_slab.from_amount
                    break
            
            ph_withholding = round((mothly_gross - from_amount) * (withholding_percent/100),2)
            for row in salary_slip.deductions:
                if row.salary_component == "PH - Withholding Tax":
                    frappe.msgprint(f"mothly_gross : {mothly_gross}")
                    frappe.msgprint(f"PH_Tax shows : {ph_withholding}")
                    row.amount = ph_withholding



        salary_slip.total_deduction = total_deduction
        salary_slip.total_taxable_deduction = total_taxable_deduction
        salary_slip.net_pay = salary_slip.gross_pay - salary_slip.total_deduction
        salary_slip.base_net_pay = salary_slip.net_pay
        salary_slip.rounded_total = round(salary_slip.net_pay)
        salary_slip.year_to_date = salary_slip.net_pay
        salary_slip.month_to_date = salary_slip.net_pay
        #salary_slip.total_in_words = number_to_words(10000)
        salary_slip.total_taxable_income = salary_slip.basic_pay - salary_slip.total_taxable_deduction
            
        # return  # Exit the function if it's not the 2nd cutoff
    
    else:
        #set deductions from the first period to 0
        for row in salary_slip.deductions:
            if row.salary_component == "PH - PHIC Contribution":
                    row.amount = 0
            elif row.salary_component == "PH - HDMF Contribution":
                    row.amount = 0
            elif row.salary_component == "PH - Withholding Tax":
                    row.amount = 0    
            elif row.salary_component == "PH - SSS Contribution":
                    row.amount = 0    
                    
        for row in salary_slip.statistical_deductions:
            if row.salary_component == "PH - HDMF Employer Contribution":
                row.amount = 0
            elif row.salary_component == "PH - PHIC Employer Contribution":
                row.amount = 0
            elif row.salary_component == "PH - SSS Employee Compensation":
                row.amount = 0
            elif row.salary_component == "PH - SSS Employer Contribution":
                row.amount = 0
                
    
        
        
        total_deduction = salary_slip.total_deduction
        total_deduction = 0
        
            
         #hide deductions from the first period
        deductions_to_show = []
        for row in salary_slip.deductions:
            if row.salary_component not in ["PH - SSS Contribution", "PH - PHIC Contribution", "PH - Withholding Tax", "PH - HDMF Contribution"]:
                deductions_to_show.append(row)
        salary_slip.deductions = deductions_to_show
        
        statistical_deductions_to_show = []
        for row in salary_slip.statistical_deductions:
            frappe.msgprint(f"statistical_deductions: {row.salary_component}")
            if row.salary_component not in ["PH - SSS Employee Compensation", "PH - SSS Employer Contribution", "PH - PHIC Employer Contribution", "PH - HDMF Employer Contribution"]:
                statistical_deductions_to_show.append(row)
        salary_slip.statistical_deductions = statistical_deductions_to_show
                        
    total_earnings = 0
    for row in salary_slip.earnings:
        total_earnings = total_earnings + row.amount
        # frappe.msgprint(f"total_earnings {total_earnings}")
    
    salary_structure_assignment = frappe.get_all(
        "Salary Structure Assignment",
        filters={"employee": employee, "docstatus": 1},
        fields=["name"],
        order_by="creation DESC",
        limit=1,
    )
    
    total_basic_pay = salary_slip.basic_pay + previous_cut_off_basic_pay
    sumtotal_taxable_income = total_basic_pay - total_deduction  
    # frappe.msgprint(f"sumtotal_taxable_income {sumtotal_taxable_income}")
    


        
    if posting_date_day != "24":
        # frappe.msgprint(f"Posting Day is: " + posting_date_day)
        # for row in salary_slip.deductions:
        #     if row.salary_component == "PH - Withholding Tax":
        #             row.amount = -ph_withholding
        salary_slip.total_deduction = 0
        # frappe.msgprint(f"Total Deduction: {total_deduction}")
        salary_slip.net_pay = salary_slip.gross_pay - salary_slip.total_deduction
        salary_slip.base_net_pay = salary_slip.net_pay
        salary_slip.rounded_total = round(salary_slip.net_pay)
        salary_slip.year_to_date = salary_slip.net_pay
        salary_slip.month_to_date = salary_slip.net_pay
    else: 
        salary_slip.total_deduction = total_deduction + ph_withholding
        # frappe.msgprint(f"total_deduction: {ph_withholding} cut_off: 24")
        salary_slip.net_pay = salary_slip.gross_pay - salary_slip.total_deduction
        salary_slip.base_net_pay = salary_slip.net_pay
        salary_slip.rounded_total = round(salary_slip.net_pay)
        salary_slip.year_to_date = salary_slip.net_pay
        salary_slip.month_to_date = salary_slip.net_pay
        

recalculate_salary_slip(doc)






def calculate_13th_month(salary_slip):
    
    employee = salary_slip.employee
    start_date = salary_slip.start_date
    end_date = salary_slip.end_date 
    start_date_str = str(start_date)
    end_date_str = str(end_date)
    start_date_date = start_date_str.split(" ")
    end_date_date = end_date_str.split(" ")
    
    posting_date = salary_slip.posting_date
    posting_date_str = str(posting_date)
    posting_date_date = posting_date_str.split(" ")
 
    posting_month_day = posting_date_date[0].split("-")[1] + "-" + posting_date_date[0].split("-")[2]
    start_month_day = str(start_date_date[0].split("-")[1]) + "-" + str(start_date_date[0].split("-")[2])
    end_month_day = str(end_date_date[0].split("-")[1]) + "-" + str(end_date_date[0].split("-")[2])
   
    thirteen_month = 0
    if posting_month_day == "12-08" or posting_month_day == "12-24":
        for row in salary_slip.earnings:
            if row.salary_component == "PH - 13th Month Pay":
                thirteen_month = row.amount
                row.amount = 0
                salary_slip.thirteen_month_pay = 0
      
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
                # for row in salary_slip.deductions:
                #             components_to_show.append(row)
                # for row in salary_slip.statistical_earnings:
                #             components_to_show.append(row)
                # for row in salary_slip.statistical_deductions:
                #             components_to_show.append(row)
                salary_slip.earnings = components_to_show
                salary_slip.basic_pay = 0
                salary_slip.net_pay = thirteen_month
                salary_slip.rounded_total = thirteen_month
                salary_slip.gross_pay = 0
                salary_slip.thirteen_month_pay = thirteen_month
        except ValueError:
            frappe.msgprint("Invalid date format or missing data.")
            
            
    if posting_month_day != "12-15":
        hide_thirteen_month = []
        for row in salary_slip.earnings:
            if row.salary_component != "DV - 13th Month Pay":
                # frappe.msgprint("Cut off not 12-15")
                hide_thirteen_month.append(row)
        salary_slip.earnings = hide_thirteen_month
        
    
    # frappe.msgprint(f"thirteen_month: {thirteen_month}")    
  

    
    

    
calculate_13th_month(doc)