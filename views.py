from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Post
from init import db
from models import User

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

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.",category='error')
    elif current_user.id != post.id:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted',category='success')
    return redirect(url_for('views.home'))
    
@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.',category='error')
        return redirect(url_for('views.home'))
    post = Post.query.filter_by(author=user.id).all()

    return render_template("posts.html",user=current_user,posts=posts, username=username)
