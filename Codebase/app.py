import os
import csv
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash

# ==============================================================================
# EMPLOYEE LEAVE MANAGEMENT SYSTEM
# ------------------------------------------------------------------------------
# First Year Engineering Mini Project (Semester 1)
# Language: Python 3
# Framework: Flask
# Storage: CSV (Comma-Separated Values) Files
# ==============================================================================

app = Flask(__name__)
# Secret key needed for session flash messages
app.secret_key = "college-mini-project-secret-key"

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMPLOYEE_FILE = os.path.join(BASE_DIR, "company_employee_data.csv")
LEAVE_FILE = os.path.join(BASE_DIR, "leave_requests.csv")

# Standard CSV column headers
EMPLOYEE_FIELDS = ["employee_id", "name", "department", "designation", "casual_leave", "sick_leave", "earned_leave"]
REQUEST_FIELDS = ["request_id", "employee_id", "employee_name", "leave_type", "start_date", "end_date", "days", "reason", "status", "submitted_on"]

# Mapping user-friendly leave names to CSV column names
LEAVE_TYPE_MAP = {
    "Casual Leave": "casual_leave",
    "Sick Leave": "sick_leave",
    "Earned Leave": "earned_leave",
    "Casual": "casual_leave",
    "Sick": "sick_leave",
    "Earned": "earned_leave",
}


# ==============================================================================
# CSV FILE OPERATIONS (READ & WRITE)
# ==============================================================================

def read_employees():
    """
    Reads all employee records from company_employee_data.csv.
    Returns a list of employee dictionaries.
    """
    employees = []
    if not os.path.exists(EMPLOYEE_FILE):
        return employees

    with open(EMPLOYEE_FILE, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert leave balances to integers for arithmetic operations
            row["casual_leave"] = int(row["casual_leave"])
            row["sick_leave"] = int(row["sick_leave"])
            row["earned_leave"] = int(row["earned_leave"])
            employees.append(row)
    return employees


def write_employees(employees):
    """
    Writes the list of employee dictionaries back to company_employee_data.csv.
    """
    with open(EMPLOYEE_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=EMPLOYEE_FIELDS)
        writer.writeheader()
        for emp in employees:
            writer.writerow(emp)


def read_leave_requests():
    """
    Reads all leave requests from leave_requests.csv.
    If the file does not exist, it creates it with standard headers.
    """
    requests = []
    if not os.path.exists(LEAVE_FILE):
        with open(LEAVE_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=REQUEST_FIELDS)
            writer.writeheader()
        return requests

    with open(LEAVE_FILE, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            requests.append(row)
    return requests


def write_leave_requests(requests):
    """
    Writes the list of leave request dictionaries back to leave_requests.csv.
    """
    with open(LEAVE_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=REQUEST_FIELDS)
        writer.writeheader()
        for req in requests:
            writer.writerow(req)


def calculate_leave_days(start_str, end_str):
    """
    Calculates the number of days between two dates inclusive (both start and end dates included).
    Returns (days, error_message).
    """
    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        if end_date < start_date:
            return None, "End date cannot be earlier than start date."
        # +1 day for inclusive calculation
        total_days = (end_date - start_date).days + 1
        return total_days, None
    except ValueError:
        return None, "Invalid date format. Please use YYYY-MM-DD."


# ==============================================================================
# HTML TEMPLATES (EMBEDDED WITH BASIC CSS)
# ==============================================================================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }} - Employee Leave Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            color: #333333;
            margin: 0;
            padding: 0;
        }
        /* Simple blue header */
        .header {
            background-color: #1a5276;
            color: #ffffff;
            padding: 16px 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 22px;
        }
        .header p {
            margin: 5px 0 0 0;
            font-size: 13px;
            color: #d4e6f1;
        }
        /* Navigation bar */
        .nav-bar {
            background-color: #2471a3;
            padding: 10px 20px;
            border-bottom: 2px solid #154360;
        }
        .nav-bar a {
            color: #ffffff;
            text-decoration: none;
            margin-right: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .nav-bar a:hover {
            text-decoration: underline;
        }
        /* Container for page contents */
        .container {
            max-width: 1000px;
            margin: 20px auto;
            padding: 0 15px;
        }
        h2 {
            color: #1a5276;
            border-bottom: 2px solid #d5dbdb;
            padding-bottom: 6px;
            margin-top: 10px;
            font-size: 18px;
        }
        h3 {
            color: #2471a3;
            font-size: 16px;
            margin-top: 20px;
        }
        /* Flash message boxes */
        .alert {
            padding: 10px 14px;
            margin-bottom: 15px;
            border: 1px solid transparent;
            font-size: 14px;
        }
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            border-color: #c3e6cb;
        }
        .alert-error {
            background-color: #f8d7da;
            color: #721c24;
            border-color: #f5c6cb;
        }
        /* Normal HTML tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            margin-bottom: 20px;
            font-size: 13px;
        }
        table, th, td {
            border: 1px solid #cccccc;
        }
        th {
            background-color: #eaf2f8;
            color: #1a5276;
            padding: 8px;
            text-align: left;
        }
        td {
            padding: 8px;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        /* Forms */
        .form-box {
            border: 1px solid #cccccc;
            background-color: #fdfdfd;
            padding: 20px;
            max-width: 550px;
            margin-top: 15px;
        }
        .form-group {
            margin-bottom: 12px;
        }
        .form-group label {
            display: block;
            font-weight: bold;
            margin-bottom: 4px;
            font-size: 13px;
        }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 6px 8px;
            border: 1px solid #cccccc;
            box-sizing: border-box;
            font-size: 13px;
            font-family: Arial, sans-serif;
        }
        .form-group textarea {
            height: 60px;
            resize: vertical;
        }
        /* Simple rectangular buttons */
        .btn {
            background-color: #1a5276;
            color: #ffffff;
            border: 1px solid #154360;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 13px;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background-color: #154360;
        }
        .btn-green {
            background-color: #27ae60;
            border-color: #1e8449;
        }
        .btn-green:hover {
            background-color: #219d55;
        }
        .btn-red {
            background-color: #c0392b;
            border-color: #962d22;
        }
        .btn-red:hover {
            background-color: #a93226;
        }
        .btn-small {
            padding: 3px 8px;
            font-size: 12px;
        }
        /* Summary statistics boxes */
        .stats-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        .stat-card {
            flex: 1;
            min-width: 120px;
            border: 1px solid #cccccc;
            background-color: #f8f9f9;
            padding: 10px;
            text-align: center;
        }
        .stat-card .num {
            font-size: 20px;
            font-weight: bold;
            color: #1a5276;
            margin-top: 4px;
        }
        .stat-card .desc {
            font-size: 12px;
            color: #555555;
        }
        /* Search and filter form */
        .filter-section {
            background-color: #f4f6f7;
            border: 1px solid #cccccc;
            padding: 12px;
            margin-bottom: 15px;
        }
        .filter-section form {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        .filter-section input, .filter-section select {
            padding: 5px 8px;
            font-size: 13px;
            border: 1px solid #cccccc;
        }
        /* Status styles */
        .status-Pending {
            color: #d35400;
            font-weight: bold;
        }
        .status-Approved {
            color: #27ae60;
            font-weight: bold;
        }
        .status-Rejected {
            color: #c0392b;
            font-weight: bold;
        }
        /* Pagination */
        .pagination {
            margin: 15px 0;
            font-size: 13px;
        }
        .pagination a, .pagination span {
            padding: 4px 8px;
            border: 1px solid #cccccc;
            color: #1a5276;
            text-decoration: none;
            margin-right: 4px;
        }
        .pagination .current-page {
            background-color: #1a5276;
            color: #ffffff;
            border-color: #1a5276;
        }
        .footer {
            margin-top: 40px;
            border-top: 1px solid #dddddd;
            padding-top: 15px;
            padding-bottom: 20px;
            font-size: 12px;
            color: #666666;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Employee Leave Management System</h1>
        <p>Department of Computer Science &amp; Engineering | First Year Mini Project</p>
    </div>
    <div class="nav-bar">
        <a href="{{ url_for('dashboard') }}">Dashboard</a>
        <a href="{{ url_for('employee_list') }}">Employee Directory</a>
        <a href="{{ url_for('add_employee') }}">Add Employee</a>
        <a href="{{ url_for('apply_leave') }}">Apply Leave</a>
        <a href="{{ url_for('leave_requests_page') }}">Leave Requests</a>
    </div>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {{ content | safe }}

        <div class="footer">
            <p>Employee Leave Management System &copy; College Mini Project | Python Flask &amp; CSV</p>
        </div>
    </div>
</body>
</html>
"""

def render_page(template_body, title="Home", **context):
    """
    Helper function to render a page using the embedded base template.
    Avoids separate HTML files and keeps everything inside Python.
    """
    rendered_content = render_template_string(template_body, **context)
    return render_template_string(BASE_TEMPLATE, title=title, content=rendered_content)


# ==============================================================================
# PAGE TEMPLATES (HTML STRINGS)
# ==============================================================================

DASHBOARD_TEMPLATE = """
<h2>Dashboard Overview</h2>
<p>Welcome to the Employee Leave Management System. Below is the summary of employees and leave requests.</p>

<div class="stats-container">
    <div class="stat-card">
        <div class="desc">Total Employees</div>
        <div class="num">{{ total_employees }}</div>
    </div>
    <div class="stat-card">
        <div class="desc">Total Leave Requests</div>
        <div class="num">{{ total_requests }}</div>
    </div>
    <div class="stat-card">
        <div class="desc">Pending Requests</div>
        <div class="num" style="color: #d35400;">{{ pending_count }}</div>
    </div>
    <div class="stat-card">
        <div class="desc">Approved Requests</div>
        <div class="num" style="color: #27ae60;">{{ approved_count }}</div>
    </div>
    <div class="stat-card">
        <div class="desc">Rejected Requests</div>
        <div class="num" style="color: #c0392b;">{{ rejected_count }}</div>
    </div>
</div>

<h3>Company Leave Balance Summary</h3>
<div class="stats-container">
    <div class="stat-card">
        <div class="desc">Total Casual Leave Days</div>
        <div class="num">{{ total_casual }}</div>
    </div>
    <div class="stat-card">
        <div class="desc">Total Sick Leave Days</div>
        <div class="num">{{ total_sick }}</div>
    </div>
    <div class="stat-card">
        <div class="desc">Total Earned Leave Days</div>
        <div class="num">{{ total_earned }}</div>
    </div>
</div>

<h3>Quick Actions</h3>
<p>
    <a href="{{ url_for('apply_leave') }}" class="btn">Apply for Leave</a> &nbsp;
    <a href="{{ url_for('add_employee') }}" class="btn">Add New Employee</a> &nbsp;
    <a href="{{ url_for('leave_requests_page') }}" class="btn">View All Leave Requests</a>
</p>

<h3>Recent Leave Applications</h3>
{% if recent_requests %}
<table>
    <tr>
        <th>Request ID</th>
        <th>Employee ID</th>
        <th>Employee Name</th>
        <th>Leave Type</th>
        <th>From Date</th>
        <th>To Date</th>
        <th>Days</th>
        <th>Reason</th>
        <th>Status</th>
    </tr>
    {% for req in recent_requests %}
    <tr>
        <td>#{{ req.request_id }}</td>
        <td><a href="{{ url_for('employee_detail', emp_id=req.employee_id) }}">{{ req.employee_id }}</a></td>
        <td>{{ req.employee_name }}</td>
        <td>{{ req.leave_type }}</td>
        <td>{{ req.start_date }}</td>
        <td>{{ req.end_date }}</td>
        <td>{{ req.days }}</td>
        <td>{{ req.reason }}</td>
        <td><span class="status-{{ req.status }}">{{ req.status }}</span></td>
    </tr>
    {% endfor %}
</table>
{% else %}
<p>No leave requests found in the system.</p>
{% endif %}

<h3>Department-Wise Employee Count</h3>
<table>
    <tr>
        <th>Department</th>
        <th>Total Employees</th>
    </tr>
    {% for dept, count in department_counts.items() %}
    <tr>
        <td>{{ dept }}</td>
        <td>{{ count }}</td>
    </tr>
    {% endfor %}
</table>
"""

EMPLOYEES_TEMPLATE = """
<h2>Employee Directory</h2>
<p>Search and browse all registered employees in the organization.</p>

<div class="filter-section">
    <form method="GET" action="{{ url_for('employee_list') }}">
        <label>Search:</label>
        <input type="text" name="search" placeholder="Search by ID or Name..." value="{{ search_query }}">
        
        <label>Department:</label>
        <select name="department">
            <option value="">-- All Departments --</option>
            {% for dept in all_departments %}
            <option value="{{ dept }}" {% if dept == selected_department %}selected{% endif %}>{{ dept }}</option>
            {% endfor %}
        </select>
        
        <button type="submit" class="btn">Search</button>
        <a href="{{ url_for('employee_list') }}" class="btn">Reset</a>
    </form>
</div>

<p><strong>Total Employees Found:</strong> {{ total_found }}</p>

{% if employees %}
<table>
    <tr>
        <th>Employee ID</th>
        <th>Name</th>
        <th>Department</th>
        <th>Designation</th>
        <th>Casual Leave</th>
        <th>Sick Leave</th>
        <th>Earned Leave</th>
        <th>Actions</th>
    </tr>
    {% for emp in employees %}
    <tr>
        <td><strong>{{ emp.employee_id }}</strong></td>
        <td>{{ emp.name }}</td>
        <td>{{ emp.department }}</td>
        <td>{{ emp.designation }}</td>
        <td>{{ emp.casual_leave }}</td>
        <td>{{ emp.sick_leave }}</td>
        <td>{{ emp.earned_leave }}</td>
        <td>
            <a href="{{ url_for('employee_detail', emp_id=emp.employee_id) }}" class="btn btn-small">Details</a>
            <a href="{{ url_for('apply_leave', emp_id=emp.employee_id) }}" class="btn btn-small">Apply Leave</a>
        </td>
    </tr>
    {% endfor %}
</table>

<!-- Pagination -->
{% if total_pages > 1 %}
<div class="pagination">
    <span>Page {{ current_page }} of {{ total_pages }}:</span>
    {% if current_page > 1 %}
        <a href="{{ url_for('employee_list', page=current_page-1, search=search_query, department=selected_department) }}">&laquo; Previous</a>
    {% endif %}
    
    <span class="current-page">{{ current_page }}</span>
    
    {% if current_page < total_pages %}
        <a href="{{ url_for('employee_list', page=current_page+1, search=search_query, department=selected_department) }}">Next &raquo;</a>
    {% endif %}
</div>
{% endif %}

{% else %}
<p>No employees found matching the search criteria.</p>
{% endif %}
"""

EMPLOYEE_DETAIL_TEMPLATE = """
<h2>Employee Details: {{ employee.name }}</h2>

<table>
    <tr>
        <th style="width: 220px;">Employee ID</th>
        <td><strong>{{ employee.employee_id }}</strong></td>
    </tr>
    <tr>
        <th>Full Name</th>
        <td>{{ employee.name }}</td>
    </tr>
    <tr>
        <th>Department</th>
        <td>{{ employee.department }}</td>
    </tr>
    <tr>
        <th>Designation</th>
        <td>{{ employee.designation }}</td>
    </tr>
    <tr>
        <th>Casual Leave Balance</th>
        <td><strong>{{ employee.casual_leave }}</strong> day(s)</td>
    </tr>
    <tr>
        <th>Sick Leave Balance</th>
        <td><strong>{{ employee.sick_leave }}</strong> day(s)</td>
    </tr>
    <tr>
        <th>Earned Leave Balance</th>
        <td><strong>{{ employee.earned_leave }}</strong> day(s)</td>
    </tr>
</table>

<p>
    <a href="{{ url_for('apply_leave', emp_id=employee.employee_id) }}" class="btn">Apply Leave for this Employee</a> &nbsp;
    <a href="{{ url_for('employee_list') }}" class="btn">Back to Employee Directory</a>
</p>

<h3>Leave Application History</h3>
{% if employee_requests %}
<table>
    <tr>
        <th>Request ID</th>
        <th>Leave Type</th>
        <th>Start Date</th>
        <th>End Date</th>
        <th>Days</th>
        <th>Reason</th>
        <th>Status</th>
        <th>Submitted On</th>
    </tr>
    {% for req in employee_requests %}
    <tr>
        <td>#{{ req.request_id }}</td>
        <td>{{ req.leave_type }}</td>
        <td>{{ req.start_date }}</td>
        <td>{{ req.end_date }}</td>
        <td>{{ req.days }}</td>
        <td>{{ req.reason }}</td>
        <td><span class="status-{{ req.status }}">{{ req.status }}</span></td>
        <td>{{ req.submitted_on }}</td>
    </tr>
    {% endfor %}
</table>
{% else %}
<p>No leave requests found for this employee.</p>
{% endif %}
"""

ADD_EMPLOYEE_TEMPLATE = """
<h2>Add New Employee</h2>
<p>Enter the details below to register a new employee into the CSV database.</p>

<div class="form-box">
    <form method="POST" action="{{ url_for('add_employee') }}">
        <div class="form-group">
            <label>Employee ID:</label>
            <input type="text" name="employee_id" placeholder="e.g. E851" required>
        </div>
        
        <div class="form-group">
            <label>Full Name:</label>
            <input type="text" name="name" placeholder="e.g. Rajesh Kumar" required>
        </div>
        
        <div class="form-group">
            <label>Department:</label>
            <input type="text" name="department" placeholder="e.g. Engineering" required list="dept-list">
            <datalist id="dept-list">
                {% for dept in departments %}
                <option value="{{ dept }}">
                {% endfor %}
            </datalist>
        </div>
        
        <div class="form-group">
            <label>Designation:</label>
            <input type="text" name="designation" placeholder="e.g. Software Engineer" required>
        </div>
        
        <div class="form-group">
            <label>Casual Leave Balance (Days):</label>
            <input type="number" name="casual_leave" value="12" min="0" max="365" required>
        </div>
        
        <div class="form-group">
            <label>Sick Leave Balance (Days):</label>
            <input type="number" name="sick_leave" value="10" min="0" max="365" required>
        </div>
        
        <div class="form-group">
            <label>Earned Leave Balance (Days):</label>
            <input type="number" name="earned_leave" value="15" min="0" max="365" required>
        </div>
        
        <button type="submit" class="btn">Save Employee</button>
        <a href="{{ url_for('employee_list') }}" class="btn">Cancel</a>
    </form>
</div>
"""

APPLY_LEAVE_TEMPLATE = """
<h2>Apply for Leave</h2>
<p>Fill in the application details. The system will automatically calculate the total days and verify the leave balance.</p>

<div class="form-box">
    <form method="POST" action="{{ url_for('apply_leave') }}">
        <div class="form-group">
            <label>Select Employee:</label>
            <select name="employee_id" required>
                <option value="">-- Choose Employee --</option>
                {% for emp in employees %}
                <option value="{{ emp.employee_id }}" {% if emp.employee_id == selected_emp_id %}selected{% endif %}>
                    {{ emp.employee_id }} - {{ emp.name }} ({{ emp.department }})
                </option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label>Leave Type:</label>
            <select name="leave_type" required>
                <option value="Casual Leave">Casual Leave</option>
                <option value="Sick Leave">Sick Leave</option>
                <option value="Earned Leave">Earned Leave</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>Start Date:</label>
            <input type="date" name="start_date" required>
        </div>
        
        <div class="form-group">
            <label>End Date:</label>
            <input type="date" name="end_date" required>
        </div>
        
        <div class="form-group">
            <label>Reason for Leave:</label>
            <textarea name="reason" placeholder="Enter the reason for taking leave..." required></textarea>
        </div>
        
        <button type="submit" class="btn">Submit Leave Application</button>
        <a href="{{ url_for('dashboard') }}" class="btn">Cancel</a>
    </form>
</div>
"""

LEAVE_REQUESTS_TEMPLATE = """
<h2>Leave Applications &amp; Approval</h2>
<p>View all leave applications. You can approve or reject pending requests below.</p>

<div class="filter-section">
    <form method="GET" action="{{ url_for('leave_requests_page') }}">
        <label>Filter by Status:</label>
        <select name="status">
            <option value="">All Statuses</option>
            <option value="Pending" {% if status_filter == 'Pending' %}selected{% endif %}>Pending</option>
            <option value="Approved" {% if status_filter == 'Approved' %}selected{% endif %}>Approved</option>
            <option value="Rejected" {% if status_filter == 'Rejected' %}selected{% endif %}>Rejected</option>
        </select>
        <button type="submit" class="btn">Filter</button>
        <a href="{{ url_for('leave_requests_page') }}" class="btn">Show All</a>
    </form>
</div>

<p><strong>Total Requests:</strong> {{ total_requests }}</p>

{% if requests %}
<table>
    <tr>
        <th>ID</th>
        <th>Employee ID</th>
        <th>Employee Name</th>
        <th>Leave Type</th>
        <th>Start Date</th>
        <th>End Date</th>
        <th>Days</th>
        <th>Reason</th>
        <th>Status</th>
        <th>Submitted On</th>
        <th>Action</th>
    </tr>
    {% for req in requests %}
    <tr>
        <td><strong>#{{ req.request_id }}</strong></td>
        <td><a href="{{ url_for('employee_detail', emp_id=req.employee_id) }}">{{ req.employee_id }}</a></td>
        <td>{{ req.employee_name }}</td>
        <td>{{ req.leave_type }}</td>
        <td>{{ req.start_date }}</td>
        <td>{{ req.end_date }}</td>
        <td>{{ req.days }}</td>
        <td>{{ req.reason }}</td>
        <td><span class="status-{{ req.status }}">{{ req.status }}</span></td>
        <td>{{ req.submitted_on }}</td>
        <td>
            {% if req.status == 'Pending' %}
            <div style="display: flex; gap: 5px;">
                <form method="POST" action="{{ url_for('approve_leave', request_id=req.request_id) }}" style="display:inline;">
                    <button type="submit" class="btn btn-green btn-small">Approve</button>
                </form>
                <form method="POST" action="{{ url_for('reject_leave', request_id=req.request_id) }}" style="display:inline;">
                    <button type="submit" class="btn btn-red btn-small">Reject</button>
                </form>
            </div>
            {% else %}
            <span>Reviewed</span>
            {% endif %}
        </td>
    </tr>
    {% endfor %}
</table>
{% else %}
<p>No leave requests found.</p>
{% endif %}
"""


# ==============================================================================
# FLASK APPLICATION ROUTES
# ==============================================================================

@app.route("/")
def dashboard():
    """
    Dashboard route showing summary statistics, leave balances,
    department counts, and recent leave requests.
    """
    employees = read_employees()
    requests = read_leave_requests()

    total_employees = len(employees)
    total_requests = len(requests)

    # Count requests by status using simple loops
    pending_count = 0
    approved_count = 0
    rejected_count = 0
    for req in requests:
        if req["status"] == "Pending":
            pending_count += 1
        elif req["status"] == "Approved":
            approved_count += 1
        elif req["status"] == "Rejected":
            rejected_count += 1

    # Total company leave balances
    total_casual = 0
    total_sick = 0
    total_earned = 0
    department_counts = {}

    for emp in employees:
        total_casual += emp["casual_leave"]
        total_sick += emp["sick_leave"]
        total_earned += emp["earned_leave"]

        dept = emp["department"]
        if dept in department_counts:
            department_counts[dept] += 1
        else:
            department_counts[dept] = 1

    # Sort department names alphabetically
    sorted_departments = dict(sorted(department_counts.items()))

    # Get the last 5 recent requests in reverse chronological order
    recent_requests = list(reversed(requests))[:5]

    return render_page(
        DASHBOARD_TEMPLATE,
        title="Dashboard",
        total_employees=total_employees,
        total_requests=total_requests,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        total_casual=total_casual,
        total_sick=total_sick,
        total_earned=total_earned,
        department_counts=sorted_departments,
        recent_requests=recent_requests
    )


@app.route("/employees")
def employee_list():
    """
    Employee directory route supporting search by ID or name,
    department filtering, and clean pagination.
    """
    employees = read_employees()
    search_query = request.args.get("search", "").strip()
    selected_department = request.args.get("department", "").strip()

    # Collect all unique department names for dropdown
    departments_set = set()
    for emp in employees:
        departments_set.add(emp["department"])
    all_departments = sorted(list(departments_set))

    # Filter employees based on search and department
    filtered_employees = []
    for emp in employees:
        # Check department filter
        if selected_department and emp["department"] != selected_department:
            continue

        # Check search query (matches ID or Name)
        if search_query:
            query_lower = search_query.lower()
            id_match = query_lower in emp["employee_id"].lower()
            name_match = query_lower in emp["name"].lower()
            if not (id_match or name_match):
                continue

        filtered_employees.append(emp)

    total_found = len(filtered_employees)

    # Simple pagination: 25 employees per page
    page_size = 25
    total_pages = (total_found + page_size - 1) // page_size
    if total_pages == 0:
        total_pages = 1

    try:
        current_page = int(request.args.get("page", 1))
    except ValueError:
        current_page = 1

    if current_page < 1:
        current_page = 1
    if current_page > total_pages:
        current_page = total_pages

    start_index = (current_page - 1) * page_size
    end_index = start_index + page_size
    page_employees = filtered_employees[start_index:end_index]

    return render_page(
        EMPLOYEES_TEMPLATE,
        title="Employee Directory",
        employees=page_employees,
        total_found=total_found,
        current_page=current_page,
        total_pages=total_pages,
        search_query=search_query,
        selected_department=selected_department,
        all_departments=all_departments
    )


@app.route("/employee/<emp_id>")
def employee_detail(emp_id):
    """
    Shows full details for an individual employee and their complete leave history.
    """
    employees = read_employees()
    target_employee = None
    for emp in employees:
        if emp["employee_id"].upper() == emp_id.strip().upper():
            target_employee = emp
            break

    if target_employee is None:
        flash("Error: Employee not found.", "error")
        return redirect(url_for("employee_list"))

    # Fetch leave requests submitted by this employee
    all_requests = read_leave_requests()
    employee_requests = []
    for req in all_requests:
        if req["employee_id"].upper() == target_employee["employee_id"].upper():
            employee_requests.append(req)

    # Show newest requests first
    employee_requests.reverse()

    return render_page(
        EMPLOYEE_DETAIL_TEMPLATE,
        title=f"Employee Details - {target_employee['name']}",
        employee=target_employee,
        employee_requests=employee_requests
    )


@app.route("/add_employee", methods=["GET", "POST"])
@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    """
    Form to add a new employee record and save it to the CSV file.
    """
    employees = read_employees()

    # Collect existing departments for the suggestion list
    departments_set = set()
    for emp in employees:
        departments_set.add(emp["department"])
    departments = sorted(list(departments_set))

    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip().upper()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        designation = request.form.get("designation", "").strip()
        casual_leave_str = request.form.get("casual_leave", "").strip()
        sick_leave_str = request.form.get("sick_leave", "").strip()
        earned_leave_str = request.form.get("earned_leave", "").strip()

        # Validation: check required fields
        if not employee_id or not name or not department or not designation:
            flash("Error: All fields are required.", "error")
            return redirect(url_for("add_employee"))

        # Validation: check if employee ID already exists
        for emp in employees:
            if emp["employee_id"].upper() == employee_id:
                flash("Error: That Employee ID already exists. Please choose a unique ID.", "error")
                return redirect(url_for("add_employee"))

        # Validation: check integer leave balances
        try:
            casual_leave = int(casual_leave_str)
            sick_leave = int(sick_leave_str)
            earned_leave = int(earned_leave_str)
            if casual_leave < 0 or sick_leave < 0 or earned_leave < 0:
                flash("Error: Leave balances cannot be negative.", "error")
                return redirect(url_for("add_employee"))
        except ValueError:
            flash("Error: Leave balances must be valid numbers.", "error")
            return redirect(url_for("add_employee"))

        # Add new employee to the list and save
        new_emp = {
            "employee_id": employee_id,
            "name": name,
            "department": department,
            "designation": designation,
            "casual_leave": casual_leave,
            "sick_leave": sick_leave,
            "earned_leave": earned_leave
        }
        employees.append(new_emp)
        write_employees(employees)

        flash(f"Success: Employee {name} ({employee_id}) has been added successfully.", "success")
        return redirect(url_for("employee_detail", emp_id=employee_id))

    return render_page(
        ADD_EMPLOYEE_TEMPLATE,
        title="Add New Employee",
        departments=departments
    )


@app.route("/apply_leave", methods=["GET", "POST"])
@app.route("/requests/new", methods=["GET", "POST"])
def apply_leave():
    """
    Form to apply for leave. Validates employee ID, dates, inclusive days,
    and checks if the employee has sufficient balance.
    """
    employees = read_employees()
    selected_emp_id = request.args.get("emp_id", "").strip().upper()

    if request.method == "POST":
        employee_id = request.form.get("employee_id", "").strip().upper()
        leave_type = request.form.get("leave_type", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        reason = request.form.get("reason", "").strip()

        # Find employee
        employee = None
        for emp in employees:
            if emp["employee_id"].upper() == employee_id:
                employee = emp
                break

        if employee is None:
            flash("Error: Selected employee does not exist.", "error")
            return redirect(url_for("apply_leave"))

        # Check leave type
        leave_column = LEAVE_TYPE_MAP.get(leave_type)
        if not leave_column:
            flash("Error: Please select a valid leave type.", "error")
            return redirect(url_for("apply_leave"))

        # Calculate leave days
        days, error_msg = calculate_leave_days(start_date, end_date)
        if error_msg:
            flash(f"Error: {error_msg}", "error")
            return redirect(url_for("apply_leave"))

        if not reason:
            flash("Error: Reason for leave is required.", "error")
            return redirect(url_for("apply_leave"))

        # Check leave balance
        available_balance = employee[leave_column]
        if days > available_balance:
            flash(
                f"Error: Insufficient leave balance! You requested {days} day(s), but employee only has {available_balance} day(s) of {leave_type} remaining.",
                "error"
            )
            return redirect(url_for("apply_leave"))

        # Generate unique request ID
        requests = read_leave_requests()
        max_id = 0
        for req in requests:
            try:
                current_id = int(req["request_id"])
                if current_id > max_id:
                    max_id = current_id
            except ValueError:
                pass
        new_request_id = str(max_id + 1)

        # Record submission timestamp
        submitted_on = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Create new request dictionary
        new_request = {
            "request_id": new_request_id,
            "employee_id": employee["employee_id"],
            "employee_name": employee["name"],
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "days": str(days),
            "reason": reason,
            "status": "Pending",
            "submitted_on": submitted_on
        }

        requests.append(new_request)
        write_leave_requests(requests)

        flash(f"Success: Leave request submitted for {days} day(s). Status is Pending approval.", "success")
        return redirect(url_for("leave_requests_page"))

    return render_page(
        APPLY_LEAVE_TEMPLATE,
        title="Apply for Leave",
        employees=employees,
        selected_emp_id=selected_emp_id
    )


@app.route("/leave_requests")
@app.route("/requests")
def leave_requests_page():
    """
    Displays leave requests history and allows filtering by status.
    """
    all_requests = read_leave_requests()
    status_filter = request.args.get("status", "").strip()

    filtered_requests = []
    for req in all_requests:
        if status_filter and req["status"] != status_filter:
            continue
        filtered_requests.append(req)

    # Show recent requests first
    filtered_requests.reverse()

    return render_page(
        LEAVE_REQUESTS_TEMPLATE,
        title="Leave Requests",
        requests=filtered_requests,
        total_requests=len(filtered_requests),
        status_filter=status_filter
    )


@app.route("/approve_leave/<request_id>", methods=["POST"])
def approve_leave(request_id):
    """
    Approves a pending leave request, checks remaining balance,
    and automatically deducts leave days from company_employee_data.csv.
    """
    requests = read_leave_requests()
    target_request = None
    for req in requests:
        if req["request_id"] == str(request_id):
            target_request = req
            break

    if target_request is None:
        flash("Error: Leave request could not be found.", "error")
        return redirect(url_for("leave_requests_page"))

    if target_request["status"] != "Pending":
        flash("Warning: This leave request has already been reviewed.", "error")
        return redirect(url_for("leave_requests_page"))

    # Load employee to deduct balance
    employees = read_employees()
    employee = None
    for emp in employees:
        if emp["employee_id"].upper() == target_request["employee_id"].upper():
            employee = emp
            break

    if employee is None:
        flash("Error: Employee record was not found.", "error")
        return redirect(url_for("leave_requests_page"))

    leave_col = LEAVE_TYPE_MAP.get(target_request["leave_type"])
    if not leave_col:
        flash("Error: Invalid leave type.", "error")
        return redirect(url_for("leave_requests_page"))

    days_needed = int(target_request["days"])
    if employee[leave_col] < days_needed:
        flash(f"Error: Employee only has {employee[leave_col]} day(s) left. Cannot approve request.", "error")
        return redirect(url_for("leave_requests_page"))

    # Deduct days from employee balance
    employee[leave_col] -= days_needed
    write_employees(employees)

    # Mark request as Approved
    target_request["status"] = "Approved"
    write_leave_requests(requests)

    flash(f"Success: Leave request #{request_id} has been Approved and {days_needed} day(s) deducted from balance.", "success")
    return redirect(url_for("leave_requests_page"))


@app.route("/reject_leave/<request_id>", methods=["POST"])
def reject_leave(request_id):
    """
    Rejects a pending leave request. The leave balance remains unchanged.
    """
    requests = read_leave_requests()
    target_request = None
    for req in requests:
        if req["request_id"] == str(request_id):
            target_request = req
            break

    if target_request is None:
        flash("Error: Leave request could not be found.", "error")
        return redirect(url_for("leave_requests_page"))

    if target_request["status"] != "Pending":
        flash("Warning: This leave request has already been reviewed.", "error")
        return redirect(url_for("leave_requests_page"))

    # Update status to Rejected
    target_request["status"] = "Rejected"
    write_leave_requests(requests)

    flash(f"Notice: Leave request #{request_id} has been Rejected.", "success")
    return redirect(url_for("leave_requests_page"))


@app.route("/requests/<request_id>/decision", methods=["POST"])
def decide_request(request_id):
    """
    Backwards compatibility route for decision submission.
    """
    decision = request.form.get("decision", "").strip()
    if decision == "Approved":
        return approve_leave(request_id)
    elif decision == "Rejected":
        return reject_leave(request_id)
    else:
        flash("Error: Please select either Approved or Rejected.", "error")
        return redirect(url_for("leave_requests_page"))


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Ensure leave requests CSV exists on startup
    read_leave_requests()
    print("Employee Leave Management System is starting...")
    print("Open http://127.0.0.1:5000 in your web browser.")
    app.run(debug=True)
