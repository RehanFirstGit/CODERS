from flask import Flask, render_template,request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os
import math


with open('config.json') as c :
    params = json.load(c)["params"]

local_server =True
app=Flask(__name__)
app.secret_key = "super-secret-key"
app.config['UPLOAD_FOLDER']=params['upload_location']

if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno         = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(80), nullable=False)
    email       = db.Column(db.String(20), nullable=False)
    phone_num   = db.Column(db.String(12), nullable=False)
    msg         = db.Column(db.String(120), nullable=False)
    date        = db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    sno         = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(80), nullable=False)
    slug        = db.Column(db.String(25), nullable=False)
    content     = db.Column(db.String(120), nullable=False)
    tagline     = db.Column(db.String(50), nullable=False)
    date        = db.Column(db.String(12), nullable=True)
    img_file    = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    #[0:params['no_of_posts']] # this slicing will done in another format later

    page = request.args.get('page')             # form.get for html page to here, args.get to fetch var value.
    if(not(str(page).isdigit())):
        page = 1

    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts'])   :  (page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]

    if (page == 1):
        prev = "#"
        next = "/?page="+ str(page+1)

    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"

    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)



    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)  # home page for all posts

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)       # post page for one post


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/dashboard", methods =['GET','POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all() # filter_by().
        return render_template('dashboard.html', params=params,posts=posts)

    elif (request.method == 'POST'):
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_pass']):
            session['user']=params['admin_user']
            posts = Posts.query.all() #.filter_by().
            return render_template('dashboard.html', params=params,posts=posts)
        else:
            return render_template('login.html', params=params)

    else:
        return render_template('login.html', params=params)


@app.route("/edit/<string:sno>", methods =['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method =='POST'):
            ed_title = request.form.get('title')
            ed_tline = request.form.get('tline')
            ed_slug = request.form.get('slug')
            ed_content = request.form.get('content')
            ed_img_file= request.form.get('img_file')
            ed_date = datetime.now()

            if sno =='0':
                post = Posts(title=ed_title,slug=ed_slug,tagline=ed_tline,content=ed_content,img_file=ed_img_file,date=ed_date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = ed_title            # post.database_title = python var title(jar modhe html er title store ache)
                post.tagline =ed_tline
                post.slug = ed_slug
                post.content =ed_content
                post.img_File = ed_img_file
                post.date = ed_date
                db.session.commit()
                return redirect('/edit/'+sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno=sno) # sno=sno ->eta thakle add post thik hoche


@app.route("/contact",methods = ['GET','POST'])
def contact():
    if(request.method=='POST'):
        name    = request.form.get('name')
        email   = request.form.get('email')
        phone   = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, phone_num=phone, msg=message, email=email,date=datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html', params=params)

@app.route("/uploader",methods = ['GET','POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method =='POST'):
            f = request.files['filename']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "File Uploaded Successfully .."

@app.route("/logout")
def logout():
    session.pop('user')  # pop means push pop remove purpose
    return redirect('/dashboard')


@app.route("/delete/<string:sno>",methods = ['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

if __name__ == "__main__":
     app.run(debug=False,host='0.0.0.0')























