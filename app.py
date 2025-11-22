import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

app = Flask(__name__)

# Secret key for forms (CSRF protection)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# SQLite database (stored locally as site.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#---Database model---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def __ref__(self):
        return f"<User {self.email}>"
    
class SignupForm(FlaskForm):
    
    full_name = StringField(         
        'Full Name',
        validators=[DataRequired(), Length(min=2, max=100)]
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
    return render_template("index.html")

@app.route('/SignIn')
def signin():
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
        new_user = User(email=form.email.data, password=hashed_password)

    
        # 4. Save to database
        db.session.add(new_user)
        db.session.commit()
    
    # 5. Show success message and redirect
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('signin'))

    # If GET request or form not valid, just render the template again
    return render_template('signup.html', form=form)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)