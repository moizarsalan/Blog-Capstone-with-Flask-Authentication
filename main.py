from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import login_user, login_required, current_user, logout_user
from flask_gravatar import Gravatar
# My Files (Classes)
from classes.forms import CreatePostForm
from classes.blogPost import BlogPost, Blog_db
from classes.user_class import User, User_db
# My Files (Functions)
from Functions.user_load_func import login_Manager, load_user

# Init Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # DB to store blog posts
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # DB to store registered users
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init the Flask App with SQL DBs
Blog_db.init_app(app) # Blog DB
User_db.init_app(app) # User DB

# Init the Flask App with Login Manager
login_Manager.init_app(app)

# Home Route
@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


# Register Route
@app.route('/register')
def register():
    return render_template("register.html")


# Login Route
@app.route('/login')
def login():
    return render_template("login.html")


# Logout Route
@app.route('/logout')
def logout():
    return redirect(url_for('get_all_posts'))


# About Route
@app.route("/about")
def about():
    return render_template("about.html")


# Contact Route
@app.route("/contact")
def contact():
    return render_template("contact.html")


# Show Post Route
@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


# New Post Route
@app.route("/new-post")
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        Blog_db.session.add(new_post)
        Blog_db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# Edit Post Route
@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    # Displaying the info in form
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    # Validating the form
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        # Commiting in DB
        Blog_db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


# Delete Post Route
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    Blog_db.session.delete(post_to_delete)
    Blog_db.session.commit()
    return redirect(url_for('get_all_posts'))


# Executing as Script
if __name__ == "__main__":
    # Creating a database with app context
    with app.app_context():
        Blog_db.create_all()
        User_db.create_all()
    app.run(host='127.0.0.1', port=5000)
