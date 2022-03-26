from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
    
class users(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(1000))
    username = db.Column(db.String(1000))
    password = db.Column(db.String(1000))
    
    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password
    
class snippets(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    title = db.Column(db.String(1000))
    content = db.Column(db.String(100000))

    def __init__(self, title, content):
        self.title = title
        self.content = content