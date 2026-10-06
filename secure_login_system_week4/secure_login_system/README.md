# Secure Login System

A secure login web application built with **Python Flask** and **SQLite**.

## Features

- User registration
- Password hashing with bcrypt
- Login authentication
- Input validation
- Parameterized SQL queries to reduce SQL injection risk
- Secure session management
- Logout
- Protected dashboard
- Duplicate username/email prevention
- Password length validation
- Basic security headers
- Environment-based secret key
- Optional 2FA extension point

## Project Structure

```text
secure_login_system/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   └── dashboard.html
└── static/
    └── style.css
```

## Installation

Create a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace the secret key with a long random value.

Run:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Security Implementation

### Password hashing
Passwords are never stored as plain text. They are hashed with bcrypt before being saved to the database.

### SQL injection protection
Database queries use SQLite parameter placeholders instead of string concatenation.

### Input validation
Username, email, and password values are validated on the server.

### Session management
Flask sessions are used to identify authenticated users. The session is cleared during logout.

### Protected routes
The dashboard requires an authenticated session.

### Security headers
The application sets basic headers such as:

- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy

## Optional 2FA

Two-factor authentication can be added with a TOTP library such as `pyotp`. It is not enabled by default in this educational version so the core login flow remains easy to understand.

## Important

This project is intended for an internship/educational demonstration. For production deployment, also use HTTPS, CSRF protection, rate limiting, secure cookie settings, account lockout/abuse controls, centralized logging, and a production WSGI server.
