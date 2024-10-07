def recalculate_attendance():
  try:
    data_list = frappe.get_list(
      "Attendance",
      fields=["name", "overtime", "undertime", "expected_working_hours", "working_hours", "employee_name", "early_exit", "late_entry", "late_in", "attendance_date", "company", "rest_day", "status"],
      filters=[["docstatus", "=", 1]],
    #   limit = 7
    )
    
     # Fetch the most recent submitted Salary Structure Assignment for the employee
     
    
    if data_list:
      for doc in data_list:
        # frappe.msgprint("Test 4")  
        overtime = float(doc.overtime) if doc.overtime else 0
        undertime = float(doc.undertime) if doc.undertime else 0
        late_in = float(doc.late_in) if doc.late_in else 0
        expected_hours = float(doc.expected_working_hours)
        working_hours = float(doc.working_hours)
        actual_working_hours = 0
        
        if not doc.early_exit:
            if undertime == 4:
                frappe.msgprint(f" {doc.employee_name}'s undertime is {undertime}. Please validate on if it's halfday {doc.attendance_date}.")
            elif undertime != 0: 
                frappe.db.set_value("Attendance", doc.name, "undertime", 0)
                frappe.msgprint(f"Updated Undertime: {undertime} by {doc.employee_name}")
            # else: 
            #     frappe.msgprint(f"No Undertime: {undertime} by {doc.employee_name}")
                
             
        if not doc.late_entry:
            if late_in > 0:
                frappe.msgprint(f"Should be no late entry: {late_in} by {doc.employee_name} ")
                frappe.db.set_value("Attendance", doc.name, "late_in", 0)
                frappepe.msgprint(f"Updated Late_in {doc.employee_name}")
        
        # if doc.company != "HO-Itinerary":
        #     frappe.msgprint(f"{doc.employee_name}'s company is {doc.company}")
        #      # Calculate actual working hours based on policy
        #     actual_working_hours = (overtime - undertime) + expected_hours
        
        # if working_hours > expected_hours:
        #     frappe.msgprint(f" working_hours: {working_hours} is more than {expected_hours} | {doc.employee_name} on {doc.attendance_date}")
        
        
        
        salary_structure_assignment = frappe.get_all(
        "Salary Structure Assignment",
        filters={"employee_name": doc.employee_name, "docstatus": 1},
        fields=["name"],
        order_by="creation DESC",
        limit=1,
        )
        daily_hours = 0
        if salary_structure_assignment:
            assignment_doc = frappe.get_doc(
                "Salary Structure Assignment", salary_structure_assignment[0].name
            )
            # Get the daily_hours from the Salary Structure Assignment
            daily_hours = assignment_doc.daily_hours
            
        # set the status to Rest Day if the employee is rest day according to Attendance Calculation
        if doc.rest_day:
            if working_hours == 0 and doc.status == 'Present':
                # frappe.msgprint(f" status: {doc.status}, but {doc.employee_name} is rest_day on {doc.attendance_date}.")
                frappe.db.set_value("Attendance", doc.name, "Status", "Rest day")
                frappe.msgprint("Changed")
            elif working_hours > 0 and daily_hours > 0:
                frappe.msgprint(f" rest_day_duty {doc.employee_name} on {doc.attendance_date}") 
                if overtime > 0:
                    frappe.msgprint(f" {overtime}") 
                    new_overtime = round(working_hours - daily_hours, 1)
                    frappe.msgprint(f"new_overtime: {new_overtime}") 
            elif working_hours > 0 and daily_hours == 0:
                frappe.msgprint(f"Assign salary structure for {doc.employee_name} ")
            # else:
            #     frappe.msgprint(f" status: {doc.status}, but {doc.employee_name} working_hours is {working_hours} and is rest_day on {doc.attendance_date}.")
            
       
        
        # working hours need to remain as is 
        # Not all employees have expected working hours
        # Update working hours on the server
        # frappe.db.set_value("Attendance", doc.name, "working_hours", actual_working_hours)

        # Print confirmation message
        # frappe.msgprint(f"Actual Working Hours for {doc.name}, {doc.employee_name}: {actual_working_hours}")


  except Exception as e:
    frappe.log_error(f"Error recalculating attendance: {e}")
    frappe.msgprint("Error during attendance recalculation.")
    
    
recalculate_attendance()