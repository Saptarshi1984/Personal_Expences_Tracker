# Personal Expense Tracker

A Flask-based personal finance dashboard that helps you capture expenses, set budgets, and visualize spending trends by category.

## Features
- Secure signup/signin with hashed passwords and CSRF-protected forms
- Add, edit, and delete expenses by category with dates and descriptions
- Monthly budget tracking with remaining balance highlights
- Category-wise summaries and recent expenses on the dashboard
- Responsive UI styled with Bootstrap and custom CSS

## Tech Stack
- Backend: Flask, SQLAlchemy, WTForms
- Programming language: Python
- Database: SQLite (via SQLAlchemy ORM)
- Templates: Jinja2
- Frontend: Bootstrap 5, custom CSS, Material Symbols
- Auth: Werkzeug password hashing, Flask session + flash messages

## Project Scope
- Individual financial tracking (no team/multi-tenant budgeting)
- Focus on expense logging, budget setting, and summary visualization
- Local SQLite storage by default; can be swapped for another SQL backend
- No payment processing or bank integrations included

## Getting Started
1. Create and activate a virtual environment.  
   - Windows: `python -m venv venv && venv\\Scripts\\activate`  
   - macOS/Linux: `python -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables (optional):  
   - `SECRET_KEY` (defaults to `dev-secret-key`)
4. Initialize the database and run:  
   - `flask run`  
   - or `python app.py` (uses `app.run(debug=True)`)

## Project Structure
- `app.py` – Flask app, routes, and forms
- `models/` – SQLAlchemy models and DB setup
- `templates/` – Jinja2 templates (pages and partials)
- `static/` – CSS and assets
- `instance/site.db` – SQLite database (created at runtime)

## Usage Notes
- Signup requires matching password and confirm-password fields.
- Flash alerts display validation and authentication feedback.
- Dashboard and expense routes are protected; signin required.
