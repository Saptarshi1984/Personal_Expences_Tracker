import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Category, Expence
from dotenv import load_dotenv

app = Flask(__name__)

# Secret key for forms (CSRF protection)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# SQLite database (stored locally as site.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
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
            Length(min=6, message="Password must be at least 6 characters.")
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
    
    if form.validate_on_submit():
        # 1. Check if email is already registered
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("This email is already registered. Try logging in.")
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

    # If GET request or form not valid, just render the template again
    return render_template('signup.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    return render_template('dashboard.html')

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