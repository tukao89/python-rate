from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
    
class users(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(1000))
    username = db.Column(db.String(1000))
    age = db.Column(db.Integer)
    jobTitle = db.Column(db.String(1000))
    email = db.Column(db.String(1000))
    phone = db.Column(db.String(1000))
    
    def __init__(self, name, username, age, jobTitle, email, phone):
        self.name = name
        self.username = username
        self.age = age
        self.jobTitle = jobTitle
        self.email = email
        self.phone = phone