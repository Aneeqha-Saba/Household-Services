# Household Services

A web application for managing household service bookings, built as part of the **MAD-1** course. The platform connects **customers** who need home services with **professionals** who provide them, while an **admin** manages services, approvals, and users.

## Features

### Customer
- Register and log in
- Browse available services and approved professionals
- Book a service request with a chosen professional
- View and track service history (Requested, Accepted, Rejected, Closed)
- Rate and close completed services
- Search by service name, professional name, or profile
- View a summary chart of request statuses

### Professional
- Register with service details and a PDF resume/CV upload
- Log in after admin approval
- View incoming service requests
- Accept or reject requests (only one active request at a time)
- Search past requests by date, location, or pincode
- View a summary chart of request statuses
- Update profile details

### Admin
- Log in with admin credentials
- Create, edit, and delete services
- Approve or reject professional registrations
- View uploaded professional documents (PDF)
- Search customers and professionals
- Block and unblock users
- View platform-wide summary charts

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Backend      | Python, Flask                       |
| Database     | SQLite (via Flask-SQLAlchemy)       |
| REST API     | Flask-RESTful                       |
| Frontend     | HTML, CSS, Bootstrap 5              |
| Charts       | Matplotlib                          |

## Project Structure

```
Code/
├── app.py                  # Application entry point
├── backend/
│   ├── models.py           # Database models (Admin, Customer, Professional, Service, ServiceRequest)
│   ├── controllers.py      # Web routes and page logic
│   └── api_controllers.py  # REST API endpoints for services
├── templates/              # HTML templates for all pages
├── static/
│   └── style.css           # Custom styles
└── uploads/                # Professional PDF uploads (created at runtime)
```

## Prerequisites

- Python 3.8 or higher
- pip

## Installation

1. **Clone or download the project** and navigate to the project directory:

   ```bash
   cd Code
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:

   Open a Python shell in the project directory and run:

   ```python
   from app import app, db
   from backend.models import Admin

   with app.app_context():
       db.create_all()
       admin = Admin(email="admin@example.com", password="admin123")
       db.session.add(admin)
       db.session.commit()
       print("Database initialized.")
   ```

   Adjust the admin email and password as needed.

5. **Create the chart output directory** (required for summary pages):

   ```bash
   mkdir -p static/img/summaries
   ```

   On Windows (PowerShell):

   ```powershell
   New-Item -ItemType Directory -Force -Path static\img\summaries
   ```

## Running the Application

```bash
python app.py
```

The app runs at **http://127.0.0.1:5000** by default.

### Getting Started

1. Open **http://127.0.0.1:5000** in your browser.
2. Log in as **admin** and create one or more services.
3. Register as a **professional**, then approve the account from the admin dashboard.
4. Register as a **customer**, browse services, and book a request.
5. As the **professional**, accept the request; as the **customer**, rate and close it when done.

## REST API

Services can also be managed via a REST API:

| Method | Endpoint                      | Description          |
|--------|-------------------------------|----------------------|
| GET    | `/api/service`                | List all services    |
| POST   | `/api/service`                | Create a service     |
| PUT    | `/api/service/<service_id>`   | Update a service     |
| DELETE | `/api/service/<service_id>`   | Delete a service     |

**POST / PUT body (JSON or form):**

```json
{
  "name": "Plumbing",
  "description": "Fix leaks and install fixtures",
  "price": 500.0,
  "time_required": "2 hours"
}
```

## Database Models

| Model           | Description                                              |
|-----------------|----------------------------------------------------------|
| `Admin`         | Platform administrator                                   |
| `Customer`      | Users who book household services                        |
| `Professional`  | Service providers (require admin approval)               |
| `Service`       | Service catalog (name, description, price, duration)     |
| `ServiceRequest`| Booking records linking customer, professional, and service |

### Service Request Statuses

- **Requested** — Customer has submitted a booking
- **Accepted** — Professional accepted the request
- **Rejected** — Professional declined the request
- **Closed** — Customer completed and rated the service

## Notes

- The SQLite database file (`houseservices.db`) is created automatically on first run after initialization.
- Professional document uploads are stored in the `uploads/` folder (PDF only).
- Summary pages generate chart images saved under `static/img/summaries/`.

## License

This project was developed for academic purposes as part of the MAD-1 course.
