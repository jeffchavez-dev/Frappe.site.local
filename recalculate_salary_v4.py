def recalculate_salary_slip(salary_slip):
    
    if salary_slip.payroll_frequency != "Bimonthly":
        return  # Exit the function if not "Bimonthly"
    
    def number_to_words(number):
        # Define lists of words to represent numbers
        ones = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eiglatht', 'nine']
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
        hdmf_contribution = assignment_doc.hdmf_contribution
        daily_hours = assignment_doc.daily_hours
        base_wage = assignment_doc.base
        days_of_work_per_year = int(assignment_doc.days_of_work_per_year)
        tax_shield_allowance = assignment_doc.tax_shield_allowance
        temporary_allowance = assignment_doc.temporary_allowance
     
    # temp_all =  ((temporary_allowance * 12) / days_of_work_per_year) * 

    
    salary_slip.basic_allowance_amount = tax_shield_allowance / 2
    salary_slip.monthly_rate_for_slip = base_wage

   
    
    daily_rate = (base_wage * 12) / days_of_work_per_year
    daily_rate_sum = ((base_wage + tax_shield_allowance) * 12) / days_of_work_per_year
    daily_rate_tsa = (tax_shield_allowance * 12) /days_of_work_per_year
    

    #HOURLYRATE
    hourly_rate = daily_rate / daily_hours
    hourly_rate_sum = daily_rate_sum / daily_hours
    hourly_rate_tsa = daily_rate_tsa / daily_hours
    

    rest_day_duty = round(hourly_rate_sum * 1.3 * 8, 2)
    rest_day_ot =  round(hourly_rate_sum * 1.69 * 1, 2)
    regular_ot = round(hourly_rate_sum * 1.25 * 2, 2)

    
    
    query = """
        SELECT
            SUM(undertime) AS total_undertime,
            SUM(late_in) AS total_late_in,
            SUM(CASE WHEN status = 'On Leave' THEN `leave` ELSE 0 END) AS total_leave,
            COUNT(CASE WHEN status = 'Present' THEN 1 END) AS total_present,
            COUNT(CASE WHEN status = 'Absent' THEN 1 END) AS total_absences,
            SUM(CASE WHEN legal_holiday = 1 THEN expected_working_hours ELSE 0 END) AS legal_holidays,
            SUM(CASE WHEN special_holiday = 1 THEN expected_working_hours ELSE 0 END) AS special_holidays
        FROM
            `tabAttendance`
        WHERE
            employee = %s
            AND attendance_date BETWEEN %s AND %s
    """

    result = frappe.db.sql(query, (employee, start_date, end_date), as_dict=True)[0]    
    
    total_late_in = round(result['total_late_in'], 3)
    total_undertime = round(result['total_undertime'], 3)

    total_present = result['total_present']
    total_absences = result['total_absences'] # calculated since absent_days in salary slip is incorrect 
    legal_holidays = result['legal_holidays']
    special_holidays = result['special_holidays']
    total_leave = result['total_leave']
    
    # Use the results as needed (e.g., update Salary Slip)
    salary_slip.regular_holiday_hours = legal_holidays
    salary_slip.special_holiday_hours = special_holidays
    salary_slip.regular_holiday_amount = legal_holidays * hourly_rate_sum
    salary_slip.special_holiday_amount = special_holidays * hourly_rate_sum * 0.3
    
    for row in salary_slip.earnings:
            if row.salary_component == "SM -Special Holiday Pay New":
                row.amount = salary_slip.special_holiday_amount 


    
    salary_slip.absent_days = total_absences
    salary_slip.payment_days = total_present
    salary_slip.leave_without_pay = total_leave

    
    
    #HOURS FOR SALARY SLIP FIELD
    
    total_hours = 0
    total_hours = daily_hours * total_present
    
    salary_slip.total_working_hours = total_hours
    salary_slip.basic_pay_hours = total_hours

    
    
    
    
    
    
    ph_taxshield_tardiness = 0
    # for row in salary_slip.statistical_earnings:
    #     if row.salary_component == "PH_TAXSHIELD (HOURLY RATE)":
    #         ph_taxshield_tardiness = (row.amount * total_late_in) * -1
            
    
    for row in salary_slip.earnings:
        if row.salary_component == "PH - TAXSHIELD Tardiness":
            row.amount = ph_taxshield_tardiness
    
    absent_days = salary_slip.absent_days

    sm_absences = 0
    sm_absences_basic = 0
    sm_absences_tsa = 0
    if absent_days > 0:
        sm_absences = -(absent_days * daily_rate_sum)
        sm_absences_basic = -(absent_days * round(daily_rate,2))
        sm_absences_tsa = -(absent_days * daily_rate_tsa)
    
    
    # calculated since absent_days in salary slip is incorrect 
    for row in salary_slip.statistical_earnings:
            if row.salary_component == "SM- Absences (Basic)":
                row.amount = sm_absences_basic 
                
    for row in salary_slip.earnings:
            if row.salary_component == "SM - Absences":
                row.amount = sm_absences 
                salary_slip.absences_amount = sm_absences
                salary_slip.absences_hours = absent_days
                
    for row in salary_slip.statistical_earnings:
            if row.salary_component == "SM- Absences(TSA)":
                row.amount = sm_absences_tsa 

    
    
    
    #TARDINESS
    sm_tardiness_basic = -(hourly_rate * total_late_in)
    sm_tardiness_tsa = -(hourly_rate_tsa * total_late_in)
    sm_tardiness_sum = -(hourly_rate_sum * total_late_in)
    ph_tardiness = (hourly_rate * total_late_in)

    
    #UNDERTIME
    sm_undertime_basic = -(hourly_rate * total_undertime)
    sm_undertime_tsa = -(hourly_rate_tsa * total_undertime)
    sm_undertime_sum = -(hourly_rate_sum * total_undertime)
    
    leave_without_pay = 0
    for row in salary_slip.statistical_earnings:
        if row.salary_component == "SM - Leave without Pay (Basic)":
            leave_without_pay = row.amount

    for row in salary_slip.earnings:
        if row.salary_component == "SM - Leave without Pay":
            frappe.msgprint("LWOP")

            
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
    
    salary_slip.tardy_ut_hours = round((total_undertime + total_late_in) * 60, 0)
    salary_slip.tardy_ut_amount = (sm_tardiness_sum + sm_undertime_sum) * -1
    
    total_earnings = 0
    for row in salary_slip.earnings:
        total_earnings = total_earnings + row.amount
            
    salary_slip.gross_pay = total_earnings
    
    
    
    previous_cut_off_basic_pay = 0
    previous_total_taxable_income = 0
    basic_pay = base_wage
    salary_slip.basic_pay = base_wage / 2
    
    
    
    
    ecola = 0 
    basic_pay = salary_slip.basic_pay
    regular_holiday_amount = salary_slip.regular_holiday_amount
    special_holiday_amount = salary_slip.special_holiday_amount
    basic_allowance_amount = salary_slip.basic_allowance_amount
    gross_pay_for_slip = basic_pay + basic_allowance_amount + regular_holiday_amount
    
    salary_slip.slip_gross_pay = gross_pay_for_slip
    
    
    
    
    
    calculated_phic_contribution = 0.00
    
    date_parts = posting_date.split("-")
    cut_off_day = int(date_parts[2])
    
    # total_taxable_income should be Basic pay + All basic SM Absences + Undertime + Tardiness + leave_without_pay
    basic_taxable_income = 0 #All basic SM Absences + Undertime + Tardiness + leave_without_pay
    basic_taxable_income = sm_undertime_basic + sm_tardiness_basic + sm_absences_basic + leave_without_pay
    salary_slip.total_taxable_income = salary_slip.basic_pay + basic_taxable_income 

    sumtotal_taxable_income = 0 # for sss_contribution and ph_tax calculation
    sumtotal_taxable_income = salary_slip.total_taxable_income
    
    #get the latest SSS TABLE
    sss_table = frappe.get_list("SSS Contribution", fields=["name"], filters = {"docstatus": 1}, limit=1, order_by="effective_date desc")
    latest_sss_taxtable = sss_table[0].name
    frappe.msgprint(f"SSS TABLE USED: {latest_sss_taxtable}")
    
    sss_contribution = frappe.get_doc("SSS Contribution", latest_sss_taxtable)
    sss_contribution_table = sss_contribution.contribution_table
        
    employee_con = 0
    employee_com = 0
    employer_con = 0
    if sss_contribution_table:
        for table in sss_contribution_table:
            if table.from_amount <= sumtotal_taxable_income <= table.to_amount:
                employee_con = table.employee_contribution
                employer_con = table.employer_contribution
                employee_com = table.employee_compensation
                break
    
    
    #updated PHIC AND HDMF AMOUNT
    if cut_off_day not in [27, 28, 29, 30, 31]:
        
        for row in salary_slip.earnings:
            if row.salary_component == "Mobile Load Allowance":
                row.amount = 0
        phic = 0
        if sumtotal_taxable_income <= 10000:
            phic = 250
        elif sumtotal_taxable_income > 40000:
            phic = 1600 
        else:
            frappe.msgprint(f"PHIC Calculate")
            phic = sumtotal_taxable_income * 0.025
            
        hdmf = 200 # constant for first-cutoff
        
        for row in salary_slip.deductions:
            if row.salary_component == "HDMF Loan":
                row.amount = 0
            
        for row in salary_slip.deductions:
            if row.salary_component == "PH - PHIC Contribution":
                row.amount = phic
                salary_slip.slip_philhealth = phic
            if row.salary_component == "PH - HDMF Contribution":
                row.amount = hdmf
                salary_slip.slip_pagibig_share = hdmf
            if row.salary_component == "PH - Withholding Tax":
                row.amount = 0
                salary_slip.slip_withholding_tax = row.amount
                
        for row in salary_slip.statistical_deductions:
            if row.salary_component == "PH - PHIC Employer Contribution":
                row.amount = phic
            if row.salary_component == "PH - HDMF Employer Contribution":
                row.amount = hdmf
                

            
        for row in salary_slip.deductions:
            if row.salary_component == "PH - SSS Contribution":
                    row.amount = employee_con  
                    salary_slip.slip_sss_share = employee_con
        
                    
        for row in salary_slip.statistical_deductions:
            if row.salary_component == "PH - SSS Employee Compensation":
                row.amount = employee_com
            elif row.salary_component == "PH - SSS Employer Contribution":
                row.amount = employer_con
        
        deductions_to_show = []
        for row in salary_slip.deductions:
            if row.salary_component not in ["PH - SSS Contribution", "HDMF Loan", "PH - PHIC Contribution", "PH - Withholding Tax", "PH - HDMF Contribution"] or row.amount != 0:
                deductions_to_show.append(row)
        salary_slip.deductions = deductions_to_show
        
        
        slip_philhealth = salary_slip.slip_philhealth
        slip_pagibig_share = salary_slip.slip_pagibig_share
        slip_sss_share = salary_slip.slip_sss_share
        tardy_ut_amount = salary_slip.tardy_ut_amount
        absences_amount = sm_absences
        deductions_for_slip = slip_philhealth + slip_pagibig_share + slip_sss_share + tardy_ut_amount + absences_amount
        salary_slip.slip_deductions = deductions_for_slip

        
        total_earnings = sum(row.amount for row in salary_slip.earnings) 
        total_deduction = 0
        total_taxable_deduction = 0
        for row in salary_slip.deductions:
            total_deduction = total_deduction + row.amount
            if row.salary_component == "PH - PHIC Contribution" or row.salary_component == "PH - HDMF Contribution" or row.salary_component == "PH - SSS Contribution":
                total_taxable_deduction = total_taxable_deduction + row.amount
            
        salary_slip.total_deduction = total_deduction

        salary_slip.total_taxable_deduction = total_taxable_deduction
        salary_slip.net_pay = round(salary_slip.gross_pay - salary_slip.total_deduction)
        salary_slip.base_net_pay = salary_slip.net_pay
        salary_slip.rounded_total = round(salary_slip.net_pay)
        salary_slip.year_to_date = salary_slip.net_pay
        salary_slip.month_to_date = salary_slip.net_pay
        #salary_slip.total_in_words = number_to_words(10000)
        salary_slip.total_taxable_income = sumtotal_taxable_income
        salary_slip.gross_pay_taxable = sumtotal_taxable_income

        
    else: 
        
        
        #if posting_date is in [28, 29, 30, 31] and there is a previous salary slip 
        for row in salary_slip.earnings:
            if row.salary_component == "Mobile Load Allowance":
                row.amount = row.amount * 2
                
        for row in salary_slip.deductions:
            if row.salary_component == "SSS Loan":
                row.amount = 0
                
                
        deductions_to_show = []
        for row in salary_slip.deductions:
            if row.salary_component not in ["PH - SSS Contribution", "SSS Loan", "PH - PHIC Contribution", "PH - Withholding Tax", "PH - HDMF Contribution"] or row.amount != 0:
                deductions_to_show.append(row)
        salary_slip.deductions = deductions_to_show
                
                
        filters = {
        "employee": employee,
        "end_date": ("<", start_date),
        "docstatus": 1  # Consider only submitted salary slips
        }
        
        previous_slip = frappe.get_list("Salary Slip", filters=filters, fields=["name"], limit=1, order_by="end_date desc")
        
        if previous_slip:
            previous_slip_name = previous_slip[0].name
            previous_slip_cut_off_day = previous_slip[0].posting_date
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
            
            calculated_phic_contribution = (previous_total_taxable_income + sumtotal_taxable_income) * 0.025 - previous_cut_off_phic #updated to total_taxable_income

            
            
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
            hdmf = hdmf_contribution
            for row in salary_slip.deductions:
                if row.salary_component == "PH - HDMF Contribution":
                    row.amount = hdmf
        
                    
            for row in salary_slip.statistical_deductions:
                if row.salary_component == "PH - HDMF Employer Contribution":
                    row.amount = 0
            
            
            previous_cut_off_sss = 0
            previous_cut_off_emp_com = 0
            previous_cut_off_empr_con = 0
            monthly_sss_contribution = 0
            monthly_total_taxable_income = 0 
            monthly_total_taxable_income = previous_total_taxable_income + sumtotal_taxable_income
            
            for row in previous_slip_doc.get("deductions"):
                if row.salary_component == "PH - SSS Contribution":
                    previous_cut_off_sss = row.amount

                    
            for row in previous_slip_doc.get("statistical_deductions"):    
                if row.salary_component == "PH - SSS Employee Compensation":
                    previous_cut_off_emp_com = row.amount
                if row.salary_component == "PH - SSS Employer Contribution":
                    previous_cut_off_empr_con = row.amount
   
            
            for table in sss_contribution_table:
                if table.from_amount <= monthly_total_taxable_income <= table.to_amount:

                    employee_con = table.employee_contribution - previous_cut_off_sss
                    employer_con = table.employer_contribution 
                    employee_com = table.employee_compensation 

                    break
                
            for row in salary_slip.deductions:
                if row.salary_component == "PH - SSS Contribution":
                        row.amount = employee_con  

                        
                for row in salary_slip.statistical_deductions:
                    if row.salary_component == "PH - SSS Employee Compensation":
                        row.amount = employee_com - previous_cut_off_emp_com
                    elif row.salary_component == "PH - SSS Employer Contribution":
                        row.amount = employer_con - previous_cut_off_empr_con
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
        
    other_allowances = 0
    
    for row in salary_slip.earnings:
        if row.salary_component == "Other Allowances":
            other_allowances = -total_deduction
            row.amount =  other_allowances

    total_deduction = round(total_deduction,2)
    salary_slip.gross_pay = total_earnings
    # salary_slip.basic_pay = sc_basic_pay + .1 - ph_tardiness
    # salary_slip.total_taxable_deduction = total_taxable_deduction
    

    monthly_total_taxable_income = previous_total_taxable_income + salary_slip.total_taxable_income
    
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
                row.amount = ph_withholding
                salary_slip.slip_withholding_tax = ph_withholding
    
    
    
    salary_slip.total_deduction = total_deduction + ph_withholding
    salary_slip.net_pay = salary_slip.gross_pay - salary_slip.total_deduction
    salary_slip.base_net_pay = salary_slip.net_pay
    salary_slip.rounded_total = round(salary_slip.net_pay)
    salary_slip.year_to_date = salary_slip.net_pay
    salary_slip.month_to_date = salary_slip.net_pay
    
    
    
recalculate_salary_slip(doc)
