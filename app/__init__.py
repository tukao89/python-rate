from flask import Flask, render_template, make_response,request, flash,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib
from flask_mail import Mail, Message

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
    
        def __init__(self, name, username, age, jobTitle, email, phone):
            self.name = name
            self.username = username
            self.age = age
            self.jobTitle = jobTitle
            self.email = email
            self.phone = phone
        
    class questions(db.Model):
        id = db.Column('id', db.Integer)
        question = db.Column(db.String(1000))        
        type = db.Column(db.String(20))        
    
        def __init__(self, id, question, type):
            self.id = id
            self.question = question
            self.type = type
    
    class answers(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        questionId = db.Column(db.Interger)        
        answer = db.Column(db.String(1000))
    
        def __init__(self, question, type):
            self.question = question
            self.type = type
    
    class userAnswers(db.Model):
        id = db.Column('id', db.Integer, primary_key = True)
        userId = db.Column(db.Interger)        
        questionId = db.Column(db.Interger)        
        answerId = db.Column(db.Interger)
    
        def __init__(self,userId, questionId, answerId):
            self.userId = userId
            self.questionId = questionId
            self.answerId = answerId
   
    db.create_all()
    
    if questions.query(questions.id).one() is None:
        db.session.add(questions(1, "Theo bạn thiết kế của sản phẩm năm nay thế nào?",'radio'))
        db.session.add(answers(1, "Tuyệt đẹp"))
        db.session.add(answers(1, "Bình thường"))
        db.session.add(answers(1, "Xấu"))            
        
        db.session.add(questions(2, "Theo bạn cần thêm tính năng nào?",'checkbox'))
        db.session.add(answers(2, "Đề nổ từ xa"))
        db.session.add(answers(2, "Phanh tay điện tử"))
        db.session.add(answers(2, "Auto hold"))
        db.session.add(answers(2, "Gạt mưa tự động"))
        
        db.session.add(questions(3, "Bạn thấy giá bán hợp lý không?",'radio'))
        db.session.add(answers(3, "Đắt"))
        db.session.add(answers(3, "Hợp lý"))
        db.session.add(answers(3, "Rẻ"))
        
        db.session.commit()
    
    app.config['MAIL_SERVER']='mx.vitan.dev'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'no-reply@mail.vitan.dev'
    app.config['MAIL_PASSWORD'] = '17252101'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    
    @app.route("/test-mail")
    def testMail():
        msg = Message('Hello', sender = 'no-reply@mail.vitan.dev', recipients = ['tu.phunganh@gmail.com'])
        msg.body = "Hello Flask message sent from Flask-Mail"
        mail.send(msg)
        return "Sent"
    
    @app.route("/")
    def index():
        listQuestions = questions.all()
        listAnswers = answers.all()
        
        return render_template("index.html", questions=questions, answers=answers)
    
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