# ALMS - Advanced Library Management System

A smart, analytics-driven library management system with role-based access, QR codes, book recommendations, fine tracking, and an admin analytics dashboard. Built with Flask and Bootstrap 5.

## Features

- **Role-based Login** — Admin and Student dashboards
- **Book Management** — Add, edit, delete books with search and filters
- **Student Management** — Add, view, edit students with full history
- **Issue & Return** — Issue books to students with due dates and return tracking
- **Smart Recommendations** — Suggests books based on reading history
- **QR Code per Book** — Auto-generated QR codes linking to book details
- **Fine Calculation** — Automatic late fee computation (Rs. 5/day)
- **Email Notifications** — Issue, return, and due date reminders (optional SMTP)
- **Analytics Dashboard** — Charts for most issued books, category distribution, monthly trends, active users

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5, Chart.js
- **Database:** SQLite
- **Libraries:** qrcode, smtplib, pandas

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database (creates tables, admin user, sample data)

```bash
python3 seed.py
```

### 3. Run the application

```bash
python3 app.py
```

The app will start at **http://localhost:5001**

## Login Credentials

| Role    | Email              | Password   |
|---------|--------------------|------------|
| Admin   | admin@lms.com      | admin123   |
| Student | student1@lms.com   | student123 |
| Student | student2@lms.com   | student123 |
| Student | student3@lms.com   | student123 |

## Project Structure

```
lms/
├── app.py                  # Flask app factory
├── config.py               # Configuration
├── extensions.py           # DB, login manager, CSRF
├── seed.py                 # Database seeder
├── requirements.txt
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── book.py
│   ├── issued_book.py
│   └── recommendation.py
├── routes/                 # Flask blueprints
│   ├── auth.py             # Login, register, logout
│   ├── admin.py            # Admin dashboard, CRUD, analytics
│   ├── student.py          # Student dashboard, my books
│   └── books.py            # Book catalog, detail
├── utils/                  # Helper modules
│   ├── decorators.py       # @admin_required, @student_required
│   ├── fine_calculator.py
│   ├── qr_service.py
│   ├── recommendation_engine.py
│   ├── email_service.py
│   └── helpers.py
├── templates/              # Jinja2 templates
│   ├── base.html
│   ├── components/         # Sidebar, navbar
│   ├── auth/               # Login, register
│   ├── admin/              # Dashboard, books, students, analytics
│   ├── student/            # Dashboard, my books, recommendations
│   └── books/              # Catalog, detail
└── static/
    ├── css/style.css
    ├── js/main.js
    └── qrcodes/            # Generated QR images
```

## Email Setup (Optional)

Create a `.env` file in the project root:

```
MAIL_ENABLED=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

The app works without email configured — notifications are logged instead.
