from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#---Database model---
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    expenses = db.relationship('Expence', backref='user', lazy=True)
    
    def __repr__(self):
        return f"<User {self.email}>"
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    expences = db.relationship('Expence', backref='category', lazy=True)
    
    def __repr__(self):
        return f"<Category {self.name}>"
    
class Expence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f"<Expense {self.amount} by user {self.user_id}>"
    
    
    
    
