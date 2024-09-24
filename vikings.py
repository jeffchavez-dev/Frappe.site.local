def recalculate_salary_slip(salary_slip):
    
    if salary_slip.payroll_frequency != "Bimonthly":
        return  # Exit the function if not "Bimonthly"
    
    def number_to_words(number):
        # Define lists of words to represent numbers
        ones = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        teens = ['eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens = ['ten', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        thousands = [''] + ['thousand', 'million', 'billion', 'trillion']
        
        def convert_group_of_3(num):
            if num == '000':
                return ''
            elif num[0] == '0':
                return convert_group_of_3(num[1:])
            elif num[0] == '1':
                return teens[int(num[1])] + ' ' + thousands[len(num) - 1]
            elif num[1] == '0':
                return tens[int(num[0]) - 1] + ' ' + thousands[len(num) - 1]
            else:
                return tens[int(num[0]) - 1] + ' ' + ones[int(num[1])] + ' ' + thousands[len(num) - 1]
                
        number = str(number)
        number_length = len(number)
        if number_length > 12:
            raise ValueError("Number is too large to convert to words.")
            
        if number == '0':
            return 'zero'
            
        words = ''
        for i in range((number_length - 1) // 3 + 1):
            group_of_3 = number[max(number_length - (i + 1) * 3, 0):number_length - i * 3]
            words = convert_group_of_3(group_of_3) + ' ' + words
            
        return words.strip()
        
    employee = salary_slip.employee
    start_date = salary_slip.start_date
    end_date = salary_slip.end_date
    posting_date = salary_slip.posting_date
    frappe.msgprint(f"posting date {posting_date}")
    late_in_query = """
        SELECT
            SUM(attendance.late_in) AS total_late_in
        FROM
            `tabAttendance` AS attendance
        WHERE
            attendance.employee = %s
            AND attendance.attendance_date BETWEEN %s AND %s
    """
    result = frappe.db.sql(late_in_query, (employee, start_date, end_date), as_dict=True)
    total_late_in = round(result[0].total_late_in if result and result[0].total_late_in else 0.0,3)
    
    salary_slip.late_in
    undertime_query = """
        SELECT
            SUM(attendance.undertime) AS total_undertime
        FROM
            `tabAttendance` AS attendance
        WHERE
            attendance.employee = %s
            AND attendance.attendance_date BETWEEN %s AND %s
    """
    result = frappe.db.sql(undertime_query, (employee, start_date, end_date), as_dict=True)
    total_undertime = round(result[0].total_undertime if result and result[0].total_undertime else 0.0,3)
    frappe.msgprint(f"Total Undertime: {total_undertime}")
    
    # Fetch the most recent submitted Salary Structure Assignment for the employee
    salary_structure_assignment = frappe.get_all(
        "Salary Structure Assignment",
        filters={"employee": employee, "docstatus": 1},
        fields=["name"],
        order_by="creation DESC",
        limit=1,
    )
    daily_hours = 0
    base_wage = 0 
    days_of_work_per_year = 0
    tax_shield_allowance = 0
    if salary_structure_assignment:
        assignment_doc = frappe.get_doc(
            "Salary Structure Assignment", salary_structure_assignment[0].name
        )
        # Get the daily_hours from the Salary Structure Assignment
        daily_hours = assignment_doc.daily_hours
        base_wage = assignment_doc.base
        days_of_work_per_year = int(assignment_doc.days_of_work_per_year)
        tax_shield_allowance = assignment_doc.tax_shield_allowance
        
    # frappe.msgprint(f"Base: {base_wage}")

    ph_taxshield_tardiness = 0
    # for row in salary_slip.statistical_earnings:
    #     if row.salary_component == "PH_TAXSHIELD (HOURLY RATE)":
    #         ph_taxshield_tardiness = (row.amount * total_late_in) * -1
            
    
    for row in salary_slip.earnings:
        if row.salary_component == "PH - TAXSHIELD Tardiness":
            row.amount = ph_taxshield_tardiness
    daily_rate = (base_wage * 12) / days_of_work_per_year
    daily_rate_sum = ((base_wage + tax_shield_allowance) * 12) / days_of_work_per_year
    daily_rate_tsa = (tax_shield_allowance * 12) /days_of_work_per_year
    
    # frappe.msgprint(f"Daily Rate: {daily_rate}")
    # frappe.msgprint(f"Daily Rate: {daily_rate_sum}")
    absent_days = salary_slip.absent_days
    # frappe.msgprint(f"Absent Days: {absent_days}")
    
    
    
    # daily_rate_tsa = (float(assignment_doc.tax_shield_allowance) * 12 / float(assignment_doc.days_of_work_per_year))
    # for row in salary_slip.statistical_earnings:
    #         if row.salary_component == "PH - TAXSHIELD (DAILY RATE)":
    #             row.amount = daily_rate_tsa
                
    sm_absences = (absent_days * -daily_rate_tsa) + (absent_days * - round(daily_rate,2))
    sm_absences_basic = absent_days * - round(daily_rate,2)
    # frappe.msgprint(f"absent_days: {absent_days}")
    # frappe.msgprint(f"daily_rate: {daily_rate}")
    sm_absences_tsa = absent_days * -daily_rate_tsa
    # frappe.msgprint(f"SM- Absences: {sm_absences}")
    # frappe.msgprint(f"SM- Absences - Basic : {sm_absences_basic}")
    # frappe.msgprint(f"SM- Absences(TSA): {sm_absences_tsa}")
    
    for row in salary_slip.statistical_earnings:
            if row.salary_component == "SM- Absences (Basic)":
                row.amount = sm_absences_basic 
                
    for row in salary_slip.earnings:
            if row.salary_component == "SM - Absences":
                row.amount = sm_absences 
                # frappe.msgprint(f"Absences {sm_absences}")
                
    for row in salary_slip.statistical_earnings:
            if row.salary_component == "SM- Absences(TSA)":
                row.amount = sm_absences_tsa 

    #HOURLYRATE
    hourly_rate = daily_rate / daily_hours
    hourly_rate_sum = daily_rate_sum / daily_hours
    hourly_rate_tsa = daily_rate_tsa / daily_hours
    # frappe.msgprint(f"Hourly Rate TSA: {hourly_rate_tsa}")
    
    
    #TARDINESS
    sm_tardiness_basic = (hourly_rate * total_late_in)
    sm_tardiness_tsa = (hourly_rate_tsa * total_late_in)
    sm_tardiness_sum = (hourly_rate_sum * total_late_in)
    ph_tardiness = (hourly_rate * total_late_in)
    # frappe.msgprint(f"Tardiness (TSA): {sm_tardiness_tsa}")
    
    #UNDERTIME
    sm_undertime_basic = (hourly_rate * total_undertime)
    frappe.msgprint(f"sm_undertime_basic: {sm_undertime_basic}")
    
    for row in salary_slip.earnings:
        if row.salary_component == "SM - Tardiness":
            row.amount = sm_tardiness_sum
    for row in salary_slip.statistical_earnings:
        if row.salary_component == "SM - Tardiness (Basic)":
            row.amount = sm_tardiness_basic
    for row in salary_slip.statistical_earnings:
        if row.salary_component == "SM - Tardiness(TSA)":
            row.amount = sm_tardiness_tsa
    for row in salary_slip.earnings:
        if row.salary_component == "PH - Tardiness":
            row.amount = ph_tardiness * -1
            
    for row in salary_slip.statistical_earnings:
        if row.salary_component == "SM - Undertime(BASIC)":
            sm_undertime_basic = row.amount
            
    total_earnings = 0
    for row in salary_slip.earnings:
        total_earnings = total_earnings + row.amount
            
    salary_slip.gross_pay = total_earnings
    
    #There is no sc_basic_pay in the recent tests 9.11.24
    # sc_basic_pay = 0
    # for row in salary_slip.statistical_earnings:
    #     if row.salary_component == "SC- BASIC PAY":
    #         sc_basic_pay = row.amount
    #         break
                
    # salary_slip.basic_pay = sc_basic_pay + .1 - ph_tardiness            
    
    previous_cut_off_basic_pay = 0
    previous_total_taxable_income = 0
    basic_pay = base_wage
    salary_slip.basic_pay = base_wage / 2
    calculated_phic_contribution = 0.00
    
    if not salary_slip.day:  # Check if "day" is empty or evaluates to False (0, None, False, etc.)
        date_parts = posting_date.split("-")
        cut_off_day = int(date_parts[2])
        salary_slip.day = cut_off_day
        frappe.msgprint(f"posting date day {cut_off_day}")
    else:
        cut_off_day = salary_slip.day
        frappe.msgprint(f"posting date day else{cut_off_day}")
    
    # total_taxable_income should be Basic pay + All basic SM Absences + Undertime + Tardiness
    basic_taxable_income = 0 #All basic SM Absences + Undertime + Tardiness
    basic_taxable_income = sm_undertime_basic + sm_tardiness_basic + sm_absences_basic
    frappe.msgprint(f" basic_taxable_income:  {basic_taxable_income}")
    salary_slip.total_taxable_income = salary_slip.basic_pay + basic_taxable_income 
    frappe.msgprint(f" total_taxable_income:  {salary_slip.total_taxable_income}")
    sumtotal_taxable_income = 0 # for sss_contribution and ph_tax calculation
    sumtotal_taxable_income = salary_slip.total_taxable_income
    
    sss_contribution = frappe.get_doc("SSS Contribution", "2024 SSS CONTRIBUTION TABLE")
    sss_contribution_table = sss_contribution.contribution_table
        
    employee_con = 0
    if sss_contribution_table:
          # frappe.msgprint(f"SSS Contribution Table:")
        for table in sss_contribution_table:
            if table.from_amount <= sumtotal_taxable_income <= table.to_amount:
                frappe.msgprint(f" SSS EMP: {table.employee_contribution}")
                employee_con = table.employee_contribution
                employer_con = table.employer_contribution
                employee_com = table.employee_compensation
                break
    
    
    #updated PHIC AND HDMF AMOUNT
    if cut_off_day not in [28, 29, 30, 31]:
        frappe.msgprint(f"cut_off_day {cut_off_day}")
        phic = 0
        if salary_slip.basic_pay <= 10000:
            frappe.msgprint(f"salary_slip.basic_pay: {salary_slip.basic_pay}")
            phic = 250
        elif salary_slip.basic_pay > 40000:
            phic = 1600 
        else:
            phic = salary_slip.basic_pay * 0.02
            
        hdmf = 0
        if salary_slip.gross_pay <= 1500:
            hdmf = salary_slip.gross_pay * 0.01
        elif salary_slip.gross_pay >= 5000:
            hdmf = 200
        else:
            hdmf = salary_slip.gross_pay * 0.02
            
            
        for row in salary_slip.deductions:
            if row.salary_component == "PH - PHIC Contribution":
                row.amount = phic
            elif row.salary_component == "PH - HDMF Contribution":
                row.amount = hdmf
            elif row.salary_component == "PH - Withholding Tax":
                row.amount = 0
                
        for row in salary_slip.statistical_deductions:
            if row.salary_component == "PH - PHIC Employer Contribution":
                row.amount = phic
            elif row.salary_component == "PH - HDMF Employer Contribution":
                row.amount = hdmf
                

            
        for row in salary_slip.deductions:
            if row.salary_component == "PH - SSS Contribution":
                    # employee_con = row.amount
                    row.amount = employee_con  
                    frappe.msgprint(f" There is SSS")
                    
        for row in salary_slip.statistical_deductions:
            if row.salary_component == "PH - SSS Employee Compensation":
                row.amount = employee_com
            elif row.salary_component == "PH - SSS Employer Contribution":
                row.amount = employer_con
        
        deductions_to_show = []
        for row in salary_slip.deductions:
            if row.salary_component not in ["PH - SSS Contribution", "PH - PHIC Contribution", "PH - Withholding Tax", "PH - HDMF Contribution"] or row.amount != 0:
                deductions_to_show.append(row)
        salary_slip.deductions = deductions_to_show
                
            # Add logic to hide the "Mobile Allowance" in the salary slip
        # for row in salary_slip.earnings:
        #     if row.salary_component == "Mobile Load Allowance":
        #         row.amount = 0  # Set the amount to 0 to hide the Mobile Allowance
        # You may also want to remove the Mobile Allowance from total_earnings if it was hidden
        total_earnings = sum(row.amount for row in salary_slip.earnings) 
        total_deduction = 0
        total_taxable_deduction = 0
        for row in salary_slip.deductions:
            total_deduction = total_deduction + row.amount
            if row.salary_component == "PH - PHIC Contribution" or row.salary_component == "PH - HDMF Contribution" or row.salary_component == "PH - SSS Contribution":
                total_taxable_deduction = total_taxable_deduction + row.amount
            
        salary_slip.total_deduction = total_deduction
        salary_slip.total_taxable_deduction = total_taxable_deduction
        salary_slip.net_pay = salary_slip.gross_pay - salary_slip.total_deduction
        salary_slip.base_net_pay = salary_slip.net_pay
        salary_slip.rounded_total = round(salary_slip.net_pay)
        salary_slip.year_to_date = salary_slip.net_pay
        salary_slip.month_to_date = salary_slip.net_pay
        salary_slip.total_taxable_income = sumtotal_taxable_income
        frappe.msgprint(f"BASIC PAY: {salary_slip.basic_pay}")    
        # return  # Exit the function if it's not the 2nd cutoff
        
    else: 
        #if posting_date is in [28, 29, 30, 31] and there is a previous salary slip 
        filters = {
        "employee": employee,
        "end_date": ("<", start_date),
        "docstatus": 1  # Consider only submitted salary slips
        }
        
        previous_slip = frappe.get_list("Salary Slip", filters=filters, fields=["name"], limit=1, order_by="end_date desc")
        if previous_slip:
            previous_slip_name = previous_slip[0].name
            previous_slip_cut_off_day = previous_slip[0].posting_date
            frappe.msgprint(f"there was a previous slip: {previous_slip_cut_off_day}")
            previous_slip_doc = frappe.get_doc("Salary Slip", previous_slip_name)
            previous_cut_off_basic_pay = previous_slip_doc.basic_pay
            previous_total_taxable_income = previous_slip_doc.total_taxable_income
            salary_slip.previous_cut_off_basic_pay = previous_cut_off_basic_pay
            
            previous_cut_off_phic = 0
            
            for row in previous_slip_doc.get("deductions"):
                if row.salary_component == "PH - PHIC Contribution":
                    previous_cut_off_phic = row.amount
                    break
                    
            salary_slip.previous_cut_off_phic = previous_cut_off_phic
            
            calculated_phic_contribution = (salary_slip.previous_cut_off_basic_pay + salary_slip.basic_pay) * 0.02 - previous_cut_off_phic
            
            
            
            for row in salary_slip.deductions:
                if row.salary_component == "PH - PHIC Contribution":
                    if salary_slip.basic_pay > 40000:
                        row.amount = 800  # Set PHIC component to 800 if gross pay exceeds 40,000
                    else:
                        salary_slip.total_month_basic_pay = salary_slip.previous_cut_off_basic_pay + salary_slip.basic_pay
                        if salary_slip.total_month_basic_pay <= 10000:
                            row.amount = 0  # Set PHIC component to 0 for gross pay <= 10,000
                        else:
                            row.amount = calculated_phic_contribution
                            
            for row in salary_slip.statistical_deductions:
                if row.salary_component == "PH - PHIC Employer Contribution":
                    if salary_slip.basic_pay > 40000:
                        row.amount = 800  # Set PHIC component to 800 if gross pay exceeds 40,000
                    else:
                        salary_slip.total_month_basic_pay = salary_slip.previous_cut_off_basic_pay + salary_slip.basic_pay
                        if salary_slip.total_month_basic_pay <= 10000:
                            row.amount = 0  # Set PHIC component to 0 for gross pay <= 10,000
                        else:
                            row.amount = calculated_phic_contribution
                     
            hdmf = 0
            for row in salary_slip.deductions:
                if row.salary_component == "PH - HDMF Contribution":
                    row.amount = hdmf
        
                    
            for row in salary_slip.statistical_deductions:
                if row.salary_component == "PH - HDMF Employer Contribution":
                    row.amount = hdmf
            
            
            previous_cut_off_sss = 0
            monthly_sss_contribution = 0
            monthly_total_taxable_income = 0 
            monthly_total_taxable_income = previous_total_taxable_income + sumtotal_taxable_income
            frappe.msgprint(f"previous_total_taxable_income {previous_total_taxable_income}")
            frappe.msgprint(f"total_taxable_income {sumtotal_taxable_income}")
            frappe.msgprint(f" monthly_total_taxable_income {monthly_total_taxable_income}")
            
            for row in previous_slip_doc.get("deductions"):
                if row.salary_component == "PH - SSS Contribution":
                    previous_cut_off_sss = row.amount
                    frappe.msgprint(f" There was SSS {previous_cut_off_sss}")
                    break
            
            for table in sss_contribution_table:
                if table.from_amount <= monthly_total_taxable_income <= table.to_amount:
                    frappe.msgprint(f" SSS EMP: {table.employee_contribution}")
                    employee_con = table.employee_contribution - previous_cut_off_sss
                    frappe.msgprint(f" Monthly SSS_con {table.employee_contribution}")
                    break
                
            for row in salary_slip.deductions:
                if row.salary_component == "PH - SSS Contribution":
                        # employee_con = row.amount
                        row.amount = employee_con  
                        frappe.msgprint(f" There is SSS")
                        
                for row in salary_slip.statistical_deductions:
                    if row.salary_component == "PH - SSS Employee Compensation":
                        row.amount = employee_com
                    elif row.salary_component == "PH - SSS Employer Contribution":
                        row.amount = employer_con
        else: 
             frappe.msgprint(f"there was no previous slip")
         

    
 
                        
    total_earnings = 0
    for row in salary_slip.earnings:
        total_earnings = total_earnings + row.amount
        
    total_deduction = 0
    total_taxable_deduction = 0
    for row in salary_slip.deductions:
        total_deduction = total_deduction + row.amount
        if row.salary_component == "PH - PHIC Contribution" or row.salary_component == "PH - HDMF Contribution" or row.salary_component == "PH - SSS Contribution":
                total_taxable_deduction = total_taxable_deduction + row.amount
        
    total_deduction = round(total_deduction - .1,2)
    salary_slip.gross_pay = total_earnings
    salary_slip.total_taxable_deduction = total_taxable_deduction
    

    monthly_total_taxable_income = previous_total_taxable_income + salary_slip.total_taxable_income
    frappe.msgprint(f"SUM: {monthly_total_taxable_income}")
    
    #calculate PH WITHHOLDING TAX 
    ph_withholding_tax_table = frappe.get_doc("PH Withholding Tax Table", "2024 Witholding Tax Table")
    ph_withholding_tax_slabs = ph_withholding_tax_table.slabs
    withholding_percent = 0
    from_amount = 0
    ph_withholding = 0
    
    

    if ph_withholding_tax_slabs:
        for ph_withholding_tax_slab in ph_withholding_tax_slabs:
            if ph_withholding_tax_slab.from_amount <= sumtotal_taxable_income <= ph_withholding_tax_slab.to_amount:
                withholding_percent = ph_withholding_tax_slab.percent_withheld
                from_amount = ph_withholding_tax_slab.from_amount
                break
        
        ph_withholding = round((sumtotal_taxable_income - from_amount) * (withholding_percent/100),2)
        for row in salary_slip.deductions:
            if row.salary_component == "PH - Withholding Tax":
                frappe.msgprint("PH_tax shows: {ph_withholding}")
                row.amount = ph_withholding    
    salary_slip.total_deduction = total_deduction + ph_withholding
    salary_slip.net_pay = salary_slip.gross_pay - salary_slip.total_deduction
    salary_slip.base_net_pay = salary_slip.net_pay
    salary_slip.rounded_total = round(salary_slip.net_pay)
    salary_slip.year_to_date = salary_slip.net_pay
    salary_slip.month_to_date = salary_slip.net_pay
recalculate_salary_slip(doc)
