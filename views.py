from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask_login import login_required, current_user
from models import Post, Comment, Like
from init import db
from models import User
from auth import is_user_verified
from werkzeug.utils import secure_filename
import os 
views = Blueprint("views", __name__)


#insta page, shop, navbar 

@views.route("/")
def aboutme():
    return render_template("aboutme.html", user=current_user) 

@views.route("/Products")
def Products():
    return render_template("Products.html",user=current_user)

@views.route("/home")
def home():
    posts = Post.query.all()
    return render_template("home.html",user=current_user,posts=posts)

ALLOWED_EXTENSIONS = {'txt','pdf','png','jpg','jpeg','gif'}

def allowed_file(filename):
    return ',' in filename and \
    filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/create-post", methods = ['GET', 'POST'])
@login_required
@is_user_verified  # Apply the verification check
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        file = request.files.get('file')

        if not text and not file:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()

            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))


            flash('Post created!', category='success')
            return redirect(url_for('views.home'))
             


    return render_template('createpost.html',user=current_user)

@views.route("/delete-post/<id>") 
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.",category='error')
 #   elif current_user.id != post.id:
  #      flash('You do not have permission to delete this post.', category='error')
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
    
    posts = user.posts
    return render_template("posts.html",user=current_user,posts=posts, username=username)



@views.route("/create-comment/<post_id>",methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.',category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text,author=current_user.id,post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment was added!',category='success')        
        else:
            flash('Post does not exist.',category='error') 
    

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        flash("Comment not found",category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash("You do not have permission to delete this comment.",category='error')
    else:
        db.session.delete(comment)
        db.session.commit() 
    
    
    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>",methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first() 
    like = Like.query.filter_by(author=current_user.id,post_id=post_id).first()

    if not post:
        flash("Post does not exist",category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit() 
    
    return redirect(url_for('views.home'))


#@views.route("/create-post", methods = ['GET', 'POST'])
#@login_required
#@is_user_verified  # Apply the verification check
#   if request.method == 'POST':
 #       if 'file' not in request.files:
  #          flash("file not supported")
   #         return redirect(request.url)
    #    file = redirect.files['file']
     #   if file.filename == '':
      #      flash("No selected file")
       #     return redirect(request.url)
        #### return redirect(url_for('views.home'))