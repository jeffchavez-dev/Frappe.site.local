def recalculate_attendance():
  try:
    data_list = frappe.get_list(
      "Attendance",
      fields=["name", "overtime", "undertime", "expected_working_hours", "working_hours", "employee_name", "early_exit", "late_entry", "late_in", "attendance_date", "company", "rest_day", "status", "night_differential", "docstatus"],
      filters=[["docstatus", "=", 0]#, 
      ],
    #   limit = 1
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
        night_differential = float(doc.night_differential)
        docstatus = doc.docstatus
        
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
                
        if night_differential:
            # frappe.msgprint(f"Night Differential: {night_differential} by {doc.employee_name} ")
            new_night_diff = round(night_differential - 1)
            # frappe.db.set_value("Attendance", doc.name, "night_differential", new_night_diff)
            frappe.db.set_value("Attendance", doc.name, {"night_differential": new_night_diff, "docstatus": 1})
            frappe.msgprint("ND Updated")
            #  frappe.db.set_value("Attendance", doc.name, docstatus, 1)
            frappe.msgprint(f"status: {docstatus}")
            if new_night_diff <= 0:
                new_night_diff = 0
                frappe.db.set_value("Attendance", doc.name, "night_differential", new_night_diff)
        
        # if doc.company != "HO-Itinerary":
        #     frappe.msgprint(f"{doc.employee_name}'s company is {doc.company}")
        #      # Calculate actual working hours based on policy
        #     actual_working_hours = (overtime - undertime) + expected_hours
        
        # if working_hours > expected_hours:
        #     frappe.msgprint(f" working_hours: {working_hours} is more than {expected_hours} | {doc.employee_name} on {doc.attendance_date}")
        
            
        # set the status to Rest Day if the employee is rest day according to Attendance Calculation
        if doc.rest_day and doc.status == 'Present':
            if working_hours == 0:
                frappe.msgprint(f" status: {doc.status}, but {doc.employee_name} is rest_day on {doc.attendance_date}.")
                frappe.db.set_value("Attendance", doc.name, {"Status": "Rest day", "docstatus": 1})
                frappe.msgprint("Changed")
            # elif working_hours > 0 and overtime > 8:
            #     frappe.msgprint(f" rest_day_duty {doc.employee_name} on {doc.attendance_date}") 
            #     # frappe.db.set_value("Attendance", doc.name, "working_hours", overtime)
            #      # frappe.db.set_value("Attendance", doc.name, "overtime", overtime)
            #     frappe.msgprint(f"working hours should be the overtime: {overtime}")
            # else: #overtime > 8:
            #     frappe.msgprint(f" rest_day_duty {doc.employee_name} on {doc.attendance_date}") 
            #     frappe.msgprint(f"rest day duty: {doc.overtime}")
            #      # frappe.db.set_value("Attendance", doc.name, "working_hours", overtime)
            #      # frappe.db.set_value("Attendance", doc.name, "overtime", overtime)
            #     frappe.msgprint(f"Rest Day OT is: {doc.overtime - 8}")

            
       
        
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