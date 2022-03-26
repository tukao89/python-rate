from flask import Flask, render_template, make_response,request, flash,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib

def create_app():
    
    app = Flask(__name__)
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.instance_path}/snippets.sqlite3'

    db = SQLAlchemy(app)
    
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
   
    db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")
    
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
        if(request.method=="POST"):
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