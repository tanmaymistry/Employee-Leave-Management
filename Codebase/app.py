from flask import Flask, request, redirect, url_for, render_template_string, flash
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "leave-system-key"

# These CSV files are stored beside this Python file.
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
EMPLOYEE_FILE = os.path.join(BASE_FOLDER, "company_employee_data.csv")
LEAVE_FILE = os.path.join(BASE_FOLDER, "leave_requests.csv")

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Employee Leave Management System</title>
    <style> 
        * { box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: #f6f3ea;
            color: #2b221a;
            margin: 0;
        }
        header {
            background: #2b221a;
            color: #f6f3ea;
            padding: 16px 26px;
            border-bottom: 3px solid #556b2f;
        }
        header h1 {
            font-size: 22px;
            margin: 0;
            letter-spacing: 0.3px;
        }
        .container {
            display: flex;
            min-height: calc(100vh - 60px);
        }
        nav.sidebar {
            width: 230px;
            background: #1f1914;
            padding: 20px 14px;
            flex-shrink: 0;
        }
        nav.sidebar a {
            display: flex;
            align-items: center;
            color: #cfc6b8;
            text-decoration: none;
            padding: 11px 14px;
            margin-bottom: 6px;
            border-radius: 8px;
            font-size: 14px;
        }
        nav.sidebar a .dot {
            width: 10px;
            height: 10px;
            border-radius: 3px;
            background: #4a3e35;
            margin-right: 12px;
            flex-shrink: 0;
        }
        nav.sidebar a:hover,
        nav.sidebar a.active {
            background: #362c23;
            color: #f6f3ea;
            font-weight: bold;
        }
        nav.sidebar a:hover .dot,
        nav.sidebar a.active .dot {
            background: #6b8e23;
        }
        main {
            flex: 1;
            padding: 28px 34px;
            max-width: 1050px;
        }
        h2 {
            color: #2b221a;
            margin-top: 0;
            margin-bottom: 6px;
        }
        p.subtitle {
            color: #5c4d3c;
            margin-top: 0;
            margin-bottom: 18px;
        }
        .card {
            background: #fffdf8;
            border: 1px solid #dfd8c8;
            border-radius: 10px;
            padding: 18px 20px;
            margin-top: 14px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 12px;
            background: #fffdf8;
            border: 1px solid #dfd8c8;
            border-radius: 8px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #dfd8c8;
            padding: 10px 12px;
            text-align: left;
        }
        th {
            background: #e6ecd8;
            color: #2b221a;
            font-weight: bold;
        }
        tr:hover td {
            background: #faf6ec;
        }
        label {
            display: block;
            margin-top: 12px;
            font-weight: bold;
            color: #3b2f24;
            font-size: 14px;
        }
        input, select {
            padding: 8px 10px;
            margin-top: 5px;
            min-width: 240px;
            border: 1px solid #c9bfa9;
            border-radius: 6px;
            background: #fffdf8;
            color: #2b221a;
        }
        button, .button {
            background: #556b2f;
            color: #fffdf8;
            border: 1px solid #445624;
            border-radius: 6px;
            padding: 8px 14px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            display: inline-block;
        }
        button:hover, .button:hover {
            background: #445624;
        }
        .button-brown {
            background: #4a3728;
            border-color: #36281d;
        }
        .button-brown:hover {
            background: #36281d;
        }
        .inline-form {
            display: inline-block;
            margin-right: 6px;
        }
        .link {
            color: #556b2f;
            font-weight: bold;
            text-decoration: none;
        }
        .link:hover {
            text-decoration: underline;
        }
        .message {
            padding: 10px 14px;
            border-radius: 6px;
            border: 1px solid #c9bfa9;
            margin: 0 0 16px 0;
            background: #fffdf8;
        }
        .error {
            color: #7a231d;
            background: #f9ebe8;
            border-color: #dfb8b2;
        }
        .success {
            color: #354718;
            background: #e6ecd8;
            border-color: #c2d1a3;
        }
    </style>
</head>
<body>
    <header>
        <h1>Employee Leave Management System</h1>
    </header>
    <div class="container">
        <nav class="sidebar">
            <a href="{{ url_for('dashboard') }}" class="{{ 'active' if request.endpoint == 'dashboard' else '' }}">
                <span class="dot"></span>Dashboard
            </a>
            <a href="{{ url_for('employees') }}" class="{{ 'active' if request.endpoint in ['employees', 'employee_detail'] else '' }}">
                <span class="dot"></span>Employees
            </a>
            <a href="{{ url_for('add_employee') }}" class="{{ 'active' if request.endpoint == 'add_employee' else '' }}">
                <span class="dot"></span>Add Employee
            </a>
            <a href="{{ url_for('apply_leave') }}" class="{{ 'active' if request.endpoint == 'apply_leave' else '' }}">
                <span class="dot"></span>Apply for Leave
            </a>
            <a href="{{ url_for('leave_history') }}" class="{{ 'active' if request.endpoint == 'leave_history' else '' }}">
                <span class="dot"></span>Leave History
            </a>
        </nav>
        <main>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% for category, message in messages %}
                    <div class="message {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endwith %}
            {{ content|safe }}
        </main>
    </div>
</body>
</html>
"""


def read_employees():
    employees = []
    if os.path.exists(EMPLOYEE_FILE):
        with open(EMPLOYEE_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                employees.append(row)
    return employees


def write_employees(employees):
    # Saving the whole list updates balances and newly added employees.
    fieldnames = ["employee_id", "name", "department", "designation",
                  "casual_leave", "sick_leave", "earned_leave"]
    with open(EMPLOYEE_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for employee in employees:
            writer.writerow(employee)


def read_leaves():
    leaves = []
    if os.path.exists(LEAVE_FILE):
        with open(LEAVE_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                leaves.append(row)
    return leaves


def write_leaves(leaves):
    fieldnames = ["request_id", "employee_id", "employee_name", "leave_type",
                  "start_date", "end_date", "days", "reason", "status"]
    with open(LEAVE_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for leave in leaves:
            writer.writerow(leave)


def page(content):
    return render_template_string(PAGE, content=content)


@app.route("/")
def dashboard():
    employees = read_employees()
    leaves = read_leaves()
    pending = 0
    approved = 0
    rejected = 0
    for leave in leaves:
        if leave.get("status") == "Pending":
            pending += 1
        elif leave.get("status") == "Approved":
            approved += 1
        elif leave.get("status") == "Rejected":
            rejected += 1
    content = "<h2>Dashboard</h2>"
    content += "<p class='subtitle'>Welcome to the employee leave management system.</p>"
    content += "<table><tr><th>Information</th><th>Total</th></tr>"
    content += "<tr><td>Employees</td><td>" + str(len(employees)) + "</td></tr>"
    content += "<tr><td>Leave requests</td><td>" + str(len(leaves)) + "</td></tr>"
    content += "<tr><td>Pending requests</td><td>" + str(pending) + "</td></tr>"
    content += "<tr><td>Approved requests</td><td>" + str(approved) + "</td></tr>"
    content += "<tr><td>Rejected requests</td><td>" + str(rejected) + "</td></tr></table>"
    return page(content)


@app.route("/employees")
def employees():
    all_employees = read_employees()
    search_text = request.args.get("search", "").strip().lower()
    department = request.args.get("department", "")
    departments = []
    for employee in all_employees:
        if employee["department"] not in departments:
            departments.append(employee["department"])

    shown_employees = []
    for employee in all_employees:
        matches_search = (search_text in employee["employee_id"].lower()
                          or search_text in employee["name"].lower())
        matches_department = department == "" or employee["department"] == department
        if matches_search and matches_department:
            shown_employees.append(employee)

    content = "<h2>Employee Directory</h2>"
    content += "<div class='card'><form method='get'><label>Search by employee ID or name</label>"
    content += "<input name='search' value='" + search_text + "'> "
    content += "<label>Department</label><select name='department'><option value=''>All departments</option>"
    for item in departments:
        selected = " selected" if item == department else ""
        content += "<option" + selected + ">" + item + "</option>"
    content += "</select> <button type='submit'>Search</button></form></div>"
    content += "<table><tr><th>ID</th><th>Name</th><th>Department</th><th>Designation</th><th>Details</th></tr>"
    for employee in shown_employees:
        content += "<tr><td>" + employee["employee_id"] + "</td><td>" + employee["name"] + "</td>"
        content += "<td>" + employee["department"] + "</td><td>" + employee["designation"] + "</td>"
        content += "<td><a class='link' href='" + url_for("employee_detail", employee_id=employee["employee_id"]) + "'>View</a></td></tr>"
    content += "</table>"
    return page(content)


@app.route("/employee/<employee_id>")
def employee_detail(employee_id):
    employees_list = read_employees()
    for employee in employees_list:
        if employee["employee_id"] == employee_id:
            content = "<h2>Employee Details</h2><table>"
            content += "<tr><th>Employee ID</th><td>" + employee["employee_id"] + "</td></tr>"
            content += "<tr><th>Name</th><td>" + employee["name"] + "</td></tr>"
            content += "<tr><th>Department</th><td>" + employee["department"] + "</td></tr>"
            content += "<tr><th>Designation</th><td>" + employee["designation"] + "</td></tr>"
            content += "<tr><th>Casual leave balance</th><td>" + employee["casual_leave"] + "</td></tr>"
            content += "<tr><th>Sick leave balance</th><td>" + employee["sick_leave"] + "</td></tr>"
            content += "<tr><th>Earned leave balance</th><td>" + employee["earned_leave"] + "</td></tr></table>"
            content += "<p><a class='button button-brown' href='" + url_for("employees") + "'>Back to Employees</a></p>"
            return page(content)
    flash("Employee was not found.", "error")
    return redirect(url_for("employees"))


@app.route("/employee/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        designation = request.form.get("designation", "").strip()
        if employee_id == "" or name == "" or department == "" or designation == "":
            flash("Please fill in every employee field.", "error")
        else:
            employees_list = read_employees()
            duplicate = False
            for employee in employees_list:
                if employee["employee_id"].lower() == employee_id.lower():
                    duplicate = True
            if duplicate:
                flash("That employee ID is already in use.", "error")
            else:
                employees_list.append({"employee_id": employee_id, "name": name,
                    "department": department, "designation": designation,
                    "casual_leave": "12", "sick_leave": "10", "earned_leave": "15"})
                write_employees(employees_list)
                flash("Employee added. Starting leave balances are 12, 10 and 15 days.", "success")
                return redirect(url_for("employees"))
    content = "<h2>Add Employee</h2><div class='card'><form method='post'>"
    content += "<label>Employee ID</label><input name='employee_id' required>"
    content += "<label>Name</label><input name='name' required>"
    content += "<label>Department</label><input name='department' required>"
    content += "<label>Designation</label><input name='designation' required>"
    content += "<p><button type='submit'>Add Employee</button></p></form></div>"
    return page(content)


@app.route("/leave/apply", methods=["GET", "POST"])
def apply_leave():
    employees_list = read_employees()
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "")
        leave_type = request.form.get("leave_type", "")
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        reason = request.form.get("reason", "").strip()
        selected_employee = None
        for employee in employees_list:
            if employee["employee_id"] == employee_id:
                selected_employee = employee
        if selected_employee is None:
            flash("Select a valid employee.", "error")
        elif leave_type not in ["Casual", "Sick", "Earned"]:
            flash("Select a valid leave type.", "error")
        else:
            try:
                first_day = datetime.strptime(start_date, "%Y-%m-%d").date()
                last_day = datetime.strptime(end_date, "%Y-%m-%d").date()
                if last_day < first_day:
                    flash("End date must be on or after the start date.", "error")
                else:
                    days = (last_day - first_day).days + 1
                    balance_field = leave_type.lower() + "_leave"
                    if days > int(selected_employee[balance_field]):
                        flash("The employee does not have enough " + leave_type.lower() + " leave.", "error")
                    else:
                        leaves = read_leaves()
                        request_id = "L" + str(len(leaves) + 1).zfill(4)
                        leaves.append({"request_id": request_id, "employee_id": employee_id,
                            "employee_name": selected_employee["name"], "leave_type": leave_type,
                            "start_date": start_date, "end_date": end_date, "days": str(days),
                            "reason": reason, "status": "Pending"})
                        write_leaves(leaves)
                        flash("Leave request submitted for " + str(days) + " day(s).", "success")
                        return redirect(url_for("leave_history"))
            except ValueError:
                flash("Enter valid start and end dates.", "error")

    content = "<h2>Apply for Leave</h2><div class='card'><form method='post'>"
    content += "<label>Employee</label><select name='employee_id' required><option value=''>Choose employee</option>"
    for employee in employees_list:
        content += "<option value='" + employee["employee_id"] + "'>" + employee["employee_id"] + " - " + employee["name"] + "</option>"
    content += "</select><label>Leave type</label><select name='leave_type' required>"
    content += "<option>Casual</option><option>Sick</option><option>Earned</option></select>"
    content += "<label>Start date</label><input type='date' name='start_date' required>"
    content += "<label>End date</label><input type='date' name='end_date' required>"
    content += "<label>Reason</label><input name='reason' required>"
    content += "<p><button type='submit'>Submit Request</button></p></form></div>"
    return page(content)


@app.route("/leaves")
def leave_history():
    leaves = read_leaves()
    content = "<h2>Leave Application History</h2>"
    content += "<table><tr><th>Request</th><th>Employee</th><th>Type</th><th>Dates</th><th>Days</th><th>Reason</th><th>Status</th><th>Action</th></tr>"
    for leave in leaves:
        content += "<tr><td>" + leave["request_id"] + "</td><td>" + leave["employee_id"] + " - " + leave["employee_name"] + "</td>"
        content += "<td>" + leave["leave_type"] + "</td><td>" + leave["start_date"] + " to " + leave["end_date"] + "</td>"
        content += "<td>" + leave["days"] + "</td><td>" + leave["reason"] + "</td><td>" + leave["status"] + "</td><td>"
        if leave["status"] == "Pending":
            content += "<form class='inline-form' method='post' action='" + url_for("approve_leave", request_id=leave["request_id"]) + "'>"
            content += "<button type='submit'>Approve</button></form>"
            content += "<form class='inline-form' method='post' action='" + url_for("reject_leave", request_id=leave["request_id"]) + "'>"
            content += "<button class='button-brown' type='submit'>Reject</button></form>"
        else:
            content += "-"
        content += "</td></tr>"
    content += "</table>"
    return page(content)


@app.route("/leave/approve/<request_id>", methods=["POST"])
def approve_leave(request_id):
    leaves = read_leaves()
    employees_list = read_employees()
    selected_leave = None
    for leave in leaves:
        if leave["request_id"] == request_id:
            selected_leave = leave
    if selected_leave is None or selected_leave["status"] != "Pending":
        flash("Pending request was not found.", "error")
        return redirect(url_for("leave_history"))

    for employee in employees_list:
        if employee["employee_id"] == selected_leave["employee_id"]:
            balance_field = selected_leave["leave_type"].lower() + "_leave"
            if int(employee[balance_field]) >= int(selected_leave["days"]):
                employee[balance_field] = str(int(employee[balance_field]) - int(selected_leave["days"]))
                selected_leave["status"] = "Approved"
                write_employees(employees_list)
                write_leaves(leaves)
                flash("Request approved and leave balance updated.", "success")
            else:
                flash("Request cannot be approved because the leave balance is now too low.", "error")
            return redirect(url_for("leave_history"))
    flash("Employee for this request was not found.", "error")
    return redirect(url_for("leave_history"))


@app.route("/leave/reject/<request_id>", methods=["POST"])
def reject_leave(request_id):
    leaves = read_leaves()
    for leave in leaves:
        if leave["request_id"] == request_id and leave["status"] == "Pending":
            leave["status"] = "Rejected"
            write_leaves(leaves)
            flash("Leave request rejected.", "success")
            return redirect(url_for("leave_history"))
    flash("Pending request was not found.", "error")
    return redirect(url_for("leave_history"))


if __name__ == "__main__":
    app.run(debug=True)
