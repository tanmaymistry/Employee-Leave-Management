# Employee Leave Management System

A lightweight web application built with **Python** and **Flask** for managing employee records, tracking leave balances, and processing leave applications using local CSV storage.

## Features

- **Dashboard Overview:** Displays totals for registered employees, submitted leave requests, pending approvals, approved leaves, and rejected requests.
- **Employee Directory & Search:** Lists employees with search by Employee ID or name and filtering by department.
- **Employee Balance Details:** Shows employee profiles with remaining Casual Leave, Sick Leave, and Earned Leave balances.
- **Add New Employee:** Registers employees with duplicate ID checks and starting leave balances of 12 Casual, 10 Sick, and 15 Earned leave days.
- **Apply for Leave:** Validates dates, calculates requested leave days, checks the available balance, and creates a pending request.
- **Approve or Reject Requests:** Allows pending applications to be reviewed. Approved leave days are deducted from the employee's balance.

## Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | Python 3, Flask |
| Frontend | HTML5, CSS3, Jinja2 templates |
| Design | Cream, olive green and dark brown theme |
| Data Storage | CSV files |

## Project Files

| File Name | Description |
|---|---|
| `app.py` | Main Flask application containing routes, CSV read/write functions and page templates |
| `company_employee_data.csv` | Employee dataset containing IDs, names, departments, designations and leave balances |
| `leave_requests.csv` | Leave application records containing request IDs, dates, reasons and approval status |
| `requirements.txt` | Python package dependencies required to run the project |
| `README.md` | Project documentation and setup instructions |

## CSV Data Structure

### 1. `company_employee_data.csv`

| Column | Description |
|---|---|
| `employee_id` | Unique identifier for each employee |
| `name` | Full name of the employee |
| `department` | Department name |
| `designation` | Job title or role |
| `casual_leave` | Remaining casual leave days (new employees start with 12) |
| `sick_leave` | Remaining sick leave days (new employees start with 10) |
| `earned_leave` | Remaining earned leave days (new employees start with 15) |

### 2. `leave_requests.csv`

| Column | Description |
|---|---|
| `request_id` | Auto-generated request ID (for example, `L0001`) |
| `employee_id` | ID of the employee applying for leave |
| `employee_name` | Name of the employee |
| `leave_type` | Selected leave category: Casual, Sick or Earned |
| `start_date` | Leave start date (`YYYY-MM-DD`) |
| `end_date` | Leave end date (`YYYY-MM-DD`) |
| `days` | Total calculated leave days |
| `reason` | Reason provided for the leave request |
| `status` | Request status: Pending, Approved or Rejected |

## Application Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Main dashboard showing summary counts |
| `/employees` | GET | Employee directory with search and department filter |
| `/employee/<employee_id>` | GET | Detailed profile and leave balances for one employee |
| `/employee/add` | GET, POST | Form to add a new employee record |
| `/leave/apply` | GET, POST | Form to submit a new leave request |
| `/leaves` | GET | Leave application history and status table |
| `/leave/approve/<request_id>` | POST | Approves a pending leave request and deducts leave balance |
| `/leave/reject/<request_id>` | POST | Marks a pending leave request as rejected |

## How to Run Locally

### 1. Clone the repository

Replace `YOUR-USERNAME` with your GitHub username:

```bash
git clone https://github.com/YOUR-USERNAME/Employee-Leave-Management-System.git
cd Employee-Leave-Management-System
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Flask application

```bash
python app.py
```

### 4. Open the website

Open this address in your browser:

```text
http://127.0.0.1:5000/
```

## GitHub Repository Setup

### `requirements.txt`

Make sure the file contains:

```text
Flask>=3.0.0
```

### `.gitignore`

Create a file named `.gitignore` in the project folder and add:

```text
__pycache__/
*.py[cod]
.venv/
venv/
.env
.DS_Store
```

### Upload using Git

Open the VS Code terminal inside your project folder and run:

```bash
git init
git add .
git commit -m "Initial commit: Employee Leave Management System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Employee-Leave-Management-System.git
git push -u origin main
```

## Note

- This project is made for learning and college demonstration purposes.
- It runs locally on your computer. It is not configured as a publicly hosted website.
- Employee and leave information is stored in CSV files instead of a database.
- If the repository is public, use sample data only. Do not publish real or private employee information.

## Author

**Tanmay Mistry**
