from flask import Flask, render_template, make_response,request, flash,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib
from flask_mail import Mail, Message
from wtforms import Form, BooleanField, StringField, PasswordField, validators

def create_app():
    
    app = Flask(__name__)
    app.secret_key = '1234567890'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.instance_path}/rate.sqlite3'

    db = SQLAlchemy(app)
    
    class users(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        name = db.Column(db.String(1000))        
        age = db.Column(db.Integer)
        jobTitle = db.Column(db.String(1000))
        email = db.Column(db.String(1000))
        phone = db.Column(db.String(1000))
    
    def __init__(self, name, age, jobTitle, email, phone):
        self.name = name
        self.age = age
        self.jobTitle = jobTitle
        self.email = email
        self.phone = phone
   
    db.create_all()

    
    app.config['MAIL_SERVER']='mx.vitan.dev'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'no-reply@mail.vitan.dev'
    app.config['MAIL_PASSWORD'] = '17252101'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    class RegistrationForm(Form):
        name = StringField('Name', [validators.DataRequired()])
        age = StringField('Age', [validators.DataRequired()])
        jobTitle = StringField('Job Title', [validators.DataRequired()])
        email = StringField('Email Address', [validators.Length(min=6, max=35)])
        phone = PasswordField('Phone')
    
    @app.route("/test-mail")
    def testMail():
        msg = Message('Hello', sender = 'no-reply@mail.vitan.dev', recipients = ['tu.phunganh@gmail.com'])
        msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
        return "Sent"
    
    @app.route("/")
    def index():
        form = RegistrationForm(request.form)
        if(request.method=="POST") and form.validate():
            name = request.form.get("name")
            username = request.form.get("username")
            password = request.form.get("password")
            if username!='' and password!='' and name !='':
                password = hashlib.md5(password.encode('utf-8')).hexdigest()
                db.session.add(users(name,username,password))
                db.session.commit()
                flash('Tạo tài khoản thành công!', 'success')
            else:
                flash('Lỗi tung toét, nhập lại đi!', 'error')
        return render_template("index.html", form = form)
    
    @app.route("/auth/login", methods=["GET","POST"])
    def login():
        loggedInId = request.cookies.get('loggedIn')
        if loggedInId and int(loggedInId)>0:
            return redirect(url_for('snippet_list'))
        if(request.method=="POST"):
            username = request.form.get("username")
            password = request.form.get("password")
            password = hashlib.md5(password.encode('utf-8')).hexdigest()
            try:
                user =  users.query.filter_by(username=username, password=password).one()
                resp = make_response(redirect(url_for('snippet_list')))
                resp.set_cookie('loggedIn', str(user.id))
                return resp
            except:
                flash('Tên đăng nhập hoặc mật khẩu không chính xác!', 'error')
        return render_template("auth/login.html")
        
    @app.route("/auth/register", methods=["GET","POST"])
    def register():
        form = RegistrationForm(request.form)
        if(request.method=="POST") and form.validate():
            name = request.form.get("name")
            username = request.form.get("username")
            password = request.form.get("password")
            if username!='' and password!='' and name !='':
                password = hashlib.md5(password.encode('utf-8')).hexdigest()
                db.session.add(users(name,username,password))
                db.session.commit()
                flash('Tạo tài khoản thành công!', 'success')
            else:
                flash('Lỗi tung toét, nhập lại đi!', 'error')
        return render_template("auth/register.html")
    
    @app.route("/s")
    def snippet_list():
        snippets = []
        for i in range(100):
            snippets.append({
                "id":i,
                "title":"snippet - " + str(i+1)
            })
        return render_template("snippet/list.html",snippets=snippets)
    
    @app.route("/s/<int:id>")
    def snippet_detail(id):
        return render_template("snippet/detail.html",id=id)
    
    @app.route("/create")
    def snippet_create():
        return render_template("snippet/create.html")
    

    return app