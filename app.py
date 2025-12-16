import os
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
from sqlalchemy import func as sa_func
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Category, Expence, Budget
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Secret key for forms (CSRF protection)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Database configuration (prefers DATABASE_URL, falls back to local SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
    
class SignupForm(FlaskForm):
    
    name = StringField(         
        'Name',
        validators=[
            DataRequired(), 
            Length(min=2, max=100)]
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address!")
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters.")
        ]
    )
    
    confirm_password = PasswordField(
        'confirm_password',
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters."),
            EqualTo('password', message="Passwords must match.")
        ]
    )
    submit = SubmitField('Sign Up')
    
#---Routes---    
@app.route('/')
def home():
    if 'user_id' in session:
        
        return redirect(url_for('dashboard'))
    
    return render_template("index.html")

@app.route('/SignIn', methods=['GET', 'POST'])
def signin():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
    
        user = User.query.filter_by(email=email).first()
    
        if user and check_password_hash(user.password, password):
        
            session['user_id'] = user.id
            session['name'] = user.name
            session['email'] = user.email
        
            flash("SignIn Sucessful!")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', "danger")        
    
    return render_template("signin.html")



@app.route('/SignUp', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    is_valid = form.validate_on_submit()
    # Extra safeguard in case validators are bypassed
    if request.method == 'POST' and form.password.data != form.confirm_password.data:
        is_valid = False
        flash("Passwords must match.", "danger")
    if is_valid:
        # 1. Check if email is already registered
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("This email is already registered. Try logging in.")
            return redirect(url_for('signup'))
        
        if form.password.data != form.confirm_password.data:
            flash("Passwords do not match. Please try again.")
            return redirect(url_for('signup'))

        # 2. Hash the password
        hashed_password = generate_password_hash(form.password.data)
        
        # 3. Create new user object
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)

    
        # 4. Save to database
        db.session.add(new_user)
        db.session.commit()
    
    # 5. Show success message and redirect
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('signin'))

    # If GET request or form not valid, show errors (if any) and render the template again
    if request.method == 'POST' and not is_valid:
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, "danger")
    return render_template('signup.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    user_id = session.get('user_id')
    today_date = date.today()
    current_month_start = today_date.replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    def sum_expenses(start_date=None, end_date=None):
        query = db.session.query(sa_func.coalesce(sa_func.sum(Expence.amount), 0)).filter(Expence.user_id == user_id)
        if start_date:
            query = query.filter(Expence.date >= start_date)
        if end_date:
            query = query.filter(Expence.date < end_date)
        value = query.scalar()
        return Decimal(value or 0)

    def sum_budgets(start_date=None, end_date=None):
        query = db.session.query(sa_func.coalesce(sa_func.sum(Budget.amount), 0)).filter(Budget.user_id == user_id)
        if start_date:
            query = query.filter(Budget.date >= start_date)
        if end_date:
            query = query.filter(Budget.date < end_date)
        value = query.scalar()
        return Decimal(value or 0)

    def percent_change(current, previous):
        if previous is None or previous == 0:
            return None
        try:
            return float((current - previous) / previous * 100)
        except (InvalidOperation, ZeroDivisionError):
            return None

    categories = Category.query.order_by(Category.name.asc()).all()
    spending_current = sum_expenses(start_date=current_month_start)
    spending_prev = sum_expenses(start_date=previous_month_start, end_date=current_month_start)
    total_spending = spending_current

    budget_current = sum_budgets(start_date=current_month_start)
    budget_prev = sum_budgets(start_date=previous_month_start, end_date=current_month_start)
    total_budget = budget_current

    budget_remaining_current = budget_current - spending_current
    budget_remaining_prev = budget_prev - spending_prev
    budget_remaining = budget_remaining_current if budget_remaining_current > 0 else Decimal(0)

    spending_change = percent_change(spending_current, spending_prev)
    budget_change = percent_change(budget_remaining_current, budget_remaining_prev)

    recent_expenses = (
        Expence.query.filter_by(user_id=user_id)
        .order_by(Expence.date.desc(), Expence.id.desc())
        .limit(4)
        .all()
    )

    current_category_totals = (
        db.session.query(
            Category.name,
            sa_func.coalesce(sa_func.sum(Expence.amount), 0).label("total"),
        )
        .join(Expence, (Category.id == Expence.category_id))
        .filter(Expence.user_id == user_id, Expence.date >= current_month_start)
        .group_by(Category.id)
        .order_by(Category.name.asc())
        .all()
    )
    current_category_map = {row[0]: Decimal(row[1] or 0) for row in current_category_totals}

    prev_category_totals = (
        db.session.query(
            Category.name,
            sa_func.coalesce(sa_func.sum(Expence.amount), 0).label("total"),
        )
        .join(Expence, (Category.id == Expence.category_id))
        .filter(
            Expence.user_id == user_id,
            Expence.date >= previous_month_start,
            Expence.date < current_month_start,
        )
        .group_by(Category.id)
        .order_by(Category.name.asc())
        .all()
    )
    prev_category_map = {row[0]: Decimal(row[1] or 0) for row in prev_category_totals}

    top_category_name = "N/A"
    top_category_amount = Decimal(0)
    if current_category_map:
        top_category_name, top_category_amount = max(
            current_category_map.items(), key=lambda item: item[1]
        )
    top_category_prev_amount = prev_category_map.get(top_category_name, Decimal(0))
    top_category_change = percent_change(top_category_amount, top_category_prev_amount)

    chart_labels = list(current_category_map.keys())
    chart_values = [float(val) for val in current_category_map.values()]

    return render_template(
        'dashboard.html',
        categories=categories,
        today=date.today().isoformat(),
        recent_expenses=recent_expenses,
        total_spending=total_spending,
        total_budget=total_budget,
        budget_remaining=budget_remaining,
        spending_change=spending_change,
        budget_change=budget_change,
        top_category_name=top_category_name,
        top_category_amount=top_category_amount,
        top_category_change=top_category_change,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )



@app.route('/myexpence')
def myexpence():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user_id = session.get('user_id')
    selected_category_id = request.args.get('category_id', type=int)
    categories = Category.query.order_by(Category.name.asc()).all()
    expenses_query = Expence.query.filter_by(user_id=user_id)
    if selected_category_id:
        expenses_query = expenses_query.filter(Expence.category_id == selected_category_id)

    expenses = expenses_query.order_by(Expence.date.desc(), Expence.id.desc()).all()

    total_spending_query = db.session.query(sa_func.coalesce(sa_func.sum(Expence.amount), 0)).filter(
        Expence.user_id == user_id
    )
    if selected_category_id:
        total_spending_query = total_spending_query.filter(Expence.category_id == selected_category_id)

    total_spending = total_spending_query.scalar()
    if not isinstance(total_spending, Decimal):
        total_spending = Decimal(total_spending)

    return render_template(
        'myexpence.html',
        categories=categories,
        expenses=expenses,
        today=date.today().isoformat(),
        total_spending=total_spending,
        selected_category_id=selected_category_id,
    )


@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user = User.query.get(session.get('user_id'))
    if not user:
        flash("User not found. Please sign in again.", "warning")
        return redirect(url_for('logout'))

    return render_template('settings.html', user=user)


@app.route('/budget', methods=['GET', 'POST'])
def budget():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        amount_raw = request.form.get('amount')
        budget_date_raw = request.form.get('date')

        if not amount_raw or not budget_date_raw:
            flash("Please provide both amount and date.", "danger")
            return redirect(url_for('budget'))

        try:
            amount = Decimal(amount_raw)
        except (InvalidOperation, TypeError):
            flash("Please enter a valid amount.", "danger")
            return redirect(url_for('budget'))

        try:
            budget_date = datetime.strptime(budget_date_raw, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            flash("Please enter a valid date.", "danger")
            return redirect(url_for('budget'))

        new_budget = Budget(user_id=session['user_id'], amount=amount, date=budget_date)
        db.session.add(new_budget)
        db.session.commit()
        flash("Budget added successfully.", "success")
        return redirect(url_for('budget'))

    budgets = (
        Budget.query.filter_by(user_id=session['user_id'])
        .order_by(Budget.date.desc(), Budget.id.desc())
        .all()
    )
    return render_template('budget.html', budgets=budgets, today=date.today().isoformat())



@app.route('/expense/<int:expense_id>/edit', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        flash("Please sign in to edit expenses.", "warning")
        return redirect(url_for('signin'))

    user_id = session.get('user_id')
    expense = Expence.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        flash("Expense not found or access denied.", "warning")
        return redirect(url_for('myexpence'))

    if request.method == 'POST':
        amount_raw = request.form.get('amount')
        expense_date_raw = request.form.get('date')
        category_name = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        if not amount_raw or not expense_date_raw or not category_name or not description:
            flash("All required fields must be filled.", "danger")
            return redirect(url_for('edit_expense', expense_id=expense_id, next=request.args.get('next')))

        try:
            amount = Decimal(amount_raw)
        except (InvalidOperation, TypeError):
            flash("Please enter a valid amount.", "danger")
            return redirect(url_for('edit_expense', expense_id=expense_id, next=request.args.get('next')))

        try:
            expense_date = datetime.strptime(expense_date_raw, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            flash("Please enter a valid date.", "danger")
            return redirect(url_for('edit_expense', expense_id=expense_id, next=request.args.get('next')))

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()

        expense.category_id = category.id
        expense.amount = amount
        expense.description = description
        expense.date = expense_date

        db.session.commit()
        flash("Expense updated successfully.", "success")

        next_url = request.args.get('next') or request.form.get('next')
        if not next_url or not next_url.startswith('/'):
            next_url = url_for('myexpence')
        return redirect(next_url)

    next_url = request.args.get('next')
    if not next_url or not next_url.startswith('/'):
        next_url = url_for('myexpence')
    return redirect(next_url)

@app.route('/expense/<int:expense_id>/delete', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        flash("Please sign in to delete expenses.", "warning")
        return redirect(url_for('signin'))

    user_id = session.get('user_id')
    expense = Expence.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        flash("Expense not found or access denied.", "warning")
        return redirect(url_for('myexpence'))

    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted. This action cannot be undone.", "warning")

    next_url = request.form.get('next') or request.args.get('next')
    if not next_url or not next_url.startswith('/'):
        next_url = url_for('myexpence')
    return redirect(next_url)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        flash("Please sign in to add expenses.", "warning")
        return redirect(url_for('signin'))

    amount_raw = request.form.get('amount')
    expense_date_raw = request.form.get('date')
    category_name = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()

    if not amount_raw or not expense_date_raw or not category_name or not description:
        flash("All required fields must be filled.", "danger")
        return redirect(url_for('dashboard'))

    try:
        amount = Decimal(amount_raw)
    except (InvalidOperation, TypeError):
        flash("Please enter a valid amount.", "danger")
        return redirect(url_for('dashboard'))

    try:
        expense_date = datetime.strptime(expense_date_raw, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        flash("Please enter a valid date.", "danger")
        return redirect(url_for('dashboard'))

    # Map the submitted category name to a Category record (create if missing)
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        category = Category(name=category_name)
        db.session.add(category)
        db.session.flush()  # ensure category.id is available for the expense

    new_expense = Expence(
        user_id=session['user_id'],
        category_id=category.id,
        amount=amount,
        description=description,
        date=expense_date,
    )

    db.session.add(new_expense)
    db.session.commit()

    flash("Expense added successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('name', None)
    flash("You have logged out successfully.",  "info")
    return redirect(url_for('home'))

if __name__ == "__main__":
   
   #Run for the first time
   with app.app_context():
    db.create_all()
   
    app.run(debug=True)
