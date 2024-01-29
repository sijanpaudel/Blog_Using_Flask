from flask import Flask, render_template, request, session, redirect,flash
import db
from flask_mail import Mail, Message
import os
from werkzeug.utils import secure_filename 
import math

app = Flask(__name__)

app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = db.params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = db.params['gmail-user'],
    MAIL_PASSWORD = db.params['gmail-password']
)
mail = Mail(app)

@app.route("/")
def home():
    postinit = db.Posts()
    posts = postinit.getAllPost() #.limit(db.params["no_of_posts"])
    last = math.ceil(int(db.collectionp.count_documents({}))/int(db.params["no_of_posts"]))

    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1

    page = int(page)
    posts = posts[(page-1)*db.params["no_of_posts"]:(page-1)*db.params["no_of_posts"] +db.params["no_of_posts"]]
    if(page==1):
        prev = "#"
        nextt = "/?page="+ str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page-1)
        nextt = "#"
    else:
        prev = "/?page=" + str(page-1)
        nextt = "/?page="+ str(page+1)


    return render_template("index.html", params=db.params, posts = posts, prev=prev, nextt=nextt)

@app.route("/post/<string:post_slug>", methods = ["GET"])
def post_route(post_slug):
    postinit = db.Posts()
    post = postinit.getPost(post_slug)

    return render_template("post.html", params=db.params, post=post)
    
@app.route("/about")
def about():
    return render_template("about.html", params=db.params)

@app.route("/login", methods=['GET','POST'])
def login():

    if ('user' in session and session['user']==db.params['admin_user']):
        postinit = db.Posts()
        posts = postinit.getAllPost()
        return render_template('dashboard.html', params=db.params, posts=posts)

    if request.method == 'POST':
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if (username == db.params['admin_user'] and userpass == db.params['admin_password']):
            session['user'] = username
            postinit = db.Posts()
            posts = postinit.getAllPost()
            return render_template('dashboard.html', params=db.params, posts=posts)
        else:
            flash("Invalid username or password")
        
    return render_template("login.html", params=db.params)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user']==db.params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')

            if sno == '0':
                postinit = db.Posts()
                postinit.insertDocument(title=box_title, slug=slug, content=content,tagline=tline, img_file=img_file)
            else:
                postinit = db.Posts()
                postinit.updatePostById(sno=sno, title=box_title, tagline=tline, slug=slug, content=content, img_file=img_file)
                return redirect('/edit/'+sno)
            

    post_init = db.Posts()
    post = post_init.getPostById(id=sno)
    return render_template('edit.html', params=db.params, post = post)

@app.route('/delete/<string:sno>')
def delete(sno):
    if ('user' in session and session['user']==db.params['admin_user']):
        post = db.Posts()
        post.deletePost(sno)

    return redirect('/login')
    

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user']==db.params['admin_user']):
        if request.method == 'POST':
            f = request.files['myfile']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded sucessfully"
        
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method == "POST"):
        contact = db.Contacts()

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        contact.insertDocument(name=name, email=email, number=phone, mes=message)
        msg = Message(name,
                  sender=email,
                  recipients=[db.params['gmail-user']])
        
        msg2 = Message("Thank you! "+name,
                       sender=db.params['gmail-user'],
                       recipients=[email])
        
        msg2.body = f"{name}, you have done the right choice by connecting with us. You have send us the message as : {message}"
        
        msg.body = message
        
        mail.send(msg)
        mail.send(msg2)

    return render_template("contact.html", params=db.params)

app.run(debug=True)