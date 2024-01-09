from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Post
from init import db

views = Blueprint("views", __name__)


#insta page, shop, navbar 

@views.route("/")
def aboutme():
    return render_template("aboutme.html", user=current_user) 

@views.route("/home")
def home():
    posts = Post.query.all()
    return render_template("home.html",user=current_user,posts=posts)


@views.route("/create-post", methods = ['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('createpost.html',user=current_user)

