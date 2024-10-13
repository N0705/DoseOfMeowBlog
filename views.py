from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask_login import login_required, current_user
from models import Post, Comment, Like
from init import db
import requests
import base64
from password import *
from models import User
from auth import is_user_verified
from werkzeug.utils import secure_filename
import os 
views = Blueprint("views", __name__)


# image upload
def upload_image_to_imgbb(image_data, api_key):
    # Step 2: Convert the image data to a base64 encoded string
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    # Step 3: Upload the image to ImgBB
    upload_url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': api_key,
        'image': encoded_image,
    }

    try:
        upload_response = requests.post(upload_url, data=payload)
        upload_response.raise_for_status()
        result = upload_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading the image to ImgBB: {e}")
        return None

    # Step 4: Return the new URL of the uploaded image
    if result['status'] == 200:
        #print(result)
        return result['data']['url']
    else:
        print(f"Error: {result['error']['message']}")
        return None

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


# for creating a post 
@views.route("/create-post", methods = ['GET', 'POST'])
@login_required
@is_user_verified  # Apply the verification check
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        imageFile = request.files.get('image')

        imageData = imageFile.read()

        #print(imageData)

        print("This is the text: ", text)

        # Step 1: Upload the image to ImgBB (function)
        imageLink = upload_image_to_imgbb(imageData, imgDbKey)

        print(imageLink)

        post = Post(text=text, author=current_user.id, images=imageLink)
        db.session.add(post)
        db.session.commit()

        # convert back to 
        
        #post = Post(text=text, author=current_user.id)
        #db.session.add(post)
        #db.session.commit()


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