from flask import Flask, render_template, redirect, url_for, session, request, flash
from flaskblog.models import User, Post
from flaskblog.forms import LoginForm, RegistrationForm, EditAccount, NewPost
from flaskblog import app, db

def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user

def load_post(id):
    post = Post.query.filter_by(id=id).first()
    return post

#Routes/urls
@app.route("/home")
@app.route("/", methods=["GET", "POST"])
def index():
    if "logged_in" in session:
        posts = Post.query.all()
        user = load_user(session["user_id"])
        lg = session["logged_in"]

        authors = []

        for post in posts:
            pa = post.author_id
            author = User.query.filter_by(id=pa).first()
            post_author = author.username
            authors.append(post_author)


        return render_template("index.html", user=user, lg=lg, posts=posts, authors=authors)
    return render_template("index.html", spm="Login to view posts!")

@app.route("/login", methods=["GET", "POST"])
def login():

    if "logged_in" not in session:

        form = LoginForm()
        if form.validate_on_submit():

            if form.email.data == "admin@admin.com" and form.password.data == "123":
                session["admin"] = "True"
                flash(f"Logged in as Admin", "success")
                return redirect("home")
            else:

                check_user = User.query.filter_by(email=form.email.data).first()

                if check_user:

                    if form.password.data == check_user.password:
                        session["logged_in"] = "True"
                        session["user_id"] = check_user.id
                        flash(f"Logged in as {check_user.username}", "success")
                        return redirect("home")
                    else:
                        flash("Invalid username of password. please try again", "danger")
                        return redirect(url_for("login"))

                else:
                    flash("Invalid username of password. please try again", "danger")
                    return redirect(url_for("login"))                   

    else:
        return redirect("home")

    return render_template("login.html", form=form) 
    
@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()

    if "logged_in" not in session:


        if form.validate_on_submit():
            new_user = User(username=form.username.data, password=form.password.data, email=form.email.data)
            db.session.add(new_user)
            db.session.commit()
            flash(f"Added {form.username.data}! Please login!", "success")
            return redirect(url_for("login"))


    else:
        lg = session["logged_in"]
        return render_template("register.html", lg=lg, form=form)
        
    return render_template("register.html", form=form) 

@app.route('/account', methods=["GET", "POST"])
def account():
    if "logged_in" in session:

        lg = session["logged_in"]

        form=EditAccount()
        user = load_user(session["user_id"])

        if form.validate_on_submit():

            if form.username.data == "":
                user.email = form.email.data
                db.session.commit()
            elif form.email.data == "":
                user.username = form.username.data
                db.session.commit()
            else:
                user.email = form.email.data
                user.username = form.username.data
                db.session.commit()

            flash("Updated account", "success")
            return redirect(url_for('index'))

        return render_template("account.html", user=user, form=form, lg=lg)
    else:
        flash("You need  to login to access this page!", "info")
        return redirect(url_for("login"))

@app.route('/admin', methods=["GET", "POST"])
def gotoadmin():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == "admin@admin.com" and password == "123":
            session["admin"] = "True"
            session["logged_in"] = "True"
            return redirect(url_for('admin'))

        else:
            flash("Incorrect admin credentials", "danger")
            return redirect(url_for("gotoadmin"))

    return render_template("gotoadmin.html")

@app.route('/inside_admin', methods=["GET", "POST"])
def admin():

    if "admin" in session:

        if request.method == "POST":
            uname = request.form["search"]
            users = User.query.filter(User.username.like("%"+uname+"%")).all()
            return render_template("admin.html", users=users)


        users = User.query.all()
        return render_template("admin.html", users=users)

    else:
        flash("Login to access this page", "warning")
        return redirect(url_for('gotoadmin'))


@app.route('/addPost', methods=["GET", "POST"])
def addPost():
    if "logged_in" in session:
        lg= session["logged_in"]
        form = NewPost()
        post_author = load_user(session["user_id"])

        if form.validate_on_submit():
            new_post = Post(title=form.title.data, content=form.content.data, author_id = post_author.id)
            db.session.add(new_post)
            db.session.commit()
            flash("Added post!", "success")
            return redirect(url_for('index'))

        return render_template('add_post.html', form=form, lg=lg)

    else:
        flash("You need to log in to add a post", "info")
        return redirect(url_for('login'))

@app.route("/editPost/<post_id>", methods=["GET", "POST"])
def editPost(post_id):
    post = load_post(post_id)
    user = load_user(session["user_id"])
    if post.author_id == user.id:
        lg=session["logged_in"]
        form = NewPost()

        if form.validate_on_submit():
            if form.title.data == "":
                post.content = form.content.data
                db.session.commit()
                flash("Post edited!", "info")                
                return redirect(url_for('index'))
            elif form.content.data == "":
                post.title = form.title.data
                db.session.commit()
                flash("Post edited!", "info")
                return redirect(url_for('index'))
            else:
                post.title = form.title.data
                post.content = form.content.data
                db.session.commit()
                flash("Post edited!", "info")
                return redirect(url_for('index'))
                
        return render_template('edit_post.html', form=form, lg=lg)

    else:
        flash("Do not have access to this page", "danger")
        return redirect(url_for('login'))

@app.route('/user/<uname>')
def user(uname):
    user = User.query.filter_by(username=uname).first()

    if "logged_in" in session:

        if user:
            mp = Post.query.filter_by(author_id=user.id).all()
            lg = session["logged_in"]
            return render_template("user.html", posts=mp, user=user, lg=lg)
        else:
            flash("User not found", "info")
            return redirect(url_for('index'))
    
    else:
        flash("Login to view this page!", "info")
        return redirect(url_for('login'))


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.pop("logged_in", None)
    session.pop("user_id", None)
    flash("Logged out!", "danger")
    return redirect(url_for('login'))

@app.route('/view/<post_id>')
def view(post_id):

    if "logged_in" in session:

        lg = session["logged_in"]
        post = load_post(post_id)
        return render_template("view_post.html", post=post, lg=lg)

    else:
        post = load_post(post_id)   
        return render_template("view_post.html", post=post)    