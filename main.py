from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json, math


app = Flask(__name__)
app.secret_key = 'the random string'


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

if params["local_server"]:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail-user'],
#     MAIL_PASSWORD=params['gmail-password']
# )
# mail = Mail(app)


class Contact(db.Model):
    """
    s_no, name, email, phone_no, message, date
    """
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.VARCHAR(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=True)


class Posts(db.Model):
    """
    s_no, name, email, phone_no, message, date
    """
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    heading = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.String(100), nullable=True)
    bg_image = db.Column(db.String(100), nullable=True)


@app.route("/")
def hello_world():
    post = Posts.query.filter_by().all()
    last = math.ceil(len(post)/int(params['no_of_posts']))

    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page = int(page)
    post = post[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]

    if(page==1):
        prev = "#"
        next = "/?page=" + str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page-1)
        next = "#"
    else:
        prev = "/?page=" + str(page-1)
        next = "/?page=" + str(page+1)
    return render_template('index.html', params=params, posts=post, prev=prev, next=next)


# @app.route("/index")
# def index():
#     post = Posts.query.filter_by().all()[0:params['no_of_posts']]
#     return render_template('index.html', params=params, posts=post)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/admin", methods=['GET', 'POST'])
def admin():

    if 'user' in session and session['user']==params['admin_user']:
        post = Posts.query.all()
        return render_template('admin.html', params=params, posts=post)

    if(request.method=='POST'):
        username = request.form.get('uname')
        userpass = request.form.get('upass')
        if(username==params['admin_user'] and userpass == params['admin_pass']):
            session['user'] = username 
            post = Posts.query.all()
            return render_template('admin.html', params=params, posts = post)
    
    return render_template('login.html', params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user']==params['admin_user']:
        if(request.method=='POST'):
            title = request.form.get('title')
            heading =  request.form.get('heading')
            slug =  request.form.get('slug')
            content =  request.form.get('content')
            bg_image =  request.form.get('img_file')
            date = datetime.now()

            if(sno=='0'):
                post = Posts(sno=sno, title=title, heading=heading, slug=slug, name="Jugal", content=content, bg_image=bg_image, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.heading = heading
                post.slug = slug
                post.content = content
                post.bg_image = bg_image
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, posts=post, sno=sno)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/admin")


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user']==params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/admin")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(name=name, phone_no=phone, date=datetime.now(), email=email, message=message)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


app.run(debug=True)