"""
For later on - Combining all the python files so far into one file - init.py, app.py, auth.py, views.py and models.py
"""
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from passwords import *
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename
import os
import views
from models import Post
from models import User
from models import Image
import requests
from password import *
import base64
#Added to help fix databse for images
from flask_migrate import Migrate
##rom main import db
#from main import Post
#Migrate = Migrate(main,db)

app = Flask(__name__)
app.config['SECRET_KEY'] = Secret_Key_Pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# LOGIN MANAGER SET UP
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Ensure to set up the upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# CREATE A POST 

def upload_image_to_imgbb(image_url,api_key): 
    # Step 1: Download the image from the given URL
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
        return None

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
        return result['data']['url']
    else:
        print(f"Error: {result['error']['message']}")
        return None

# Example usage
    api_key = "3e2ec9448322ec1a97b3ac76b93a5a7f" # Replace with your ImgBB API key
#image_url = 'https://placehold.co/600x400/png'
#new_image_url = upload_image_to_imgbb(image_url, api_key)
#print(f"New Image URL: {new_image_url}")

@app.before_first_request
def create_upload_folder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        image_file = request.files['image']

        if not text and not image_file:
            flash('Post cannot be empty',category='error')
            return redirect(url_for('create_post'))
        post = Post(text=text, author=current_user.id)
        db.session.add(post)
        db.session.commit()

        if image_file and allowed_file(image_file.filename):

            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            image_file.save(image_path)

            new_image_url = upload_image_to_imgbb(image_path,imgBBAPIKey)
            if new_image_url:
                image_instance = Image(
                    data = new_image_url,
                    mimetype = image_file.mimetype,
                    filename = filename,
                    post_id = post.id
                )
                db.session.add(image_instance)
                db.session.commit()
                flash("Image Uploaded sucessfully!", category='success')
            else:
                flash("Failed to upload image to ImgBB.",category='error')
            flash('Post Created!',category='sucess')
            return redirect(url_for('home'))
        return render_template('createpost.html',user=current_user)


# ALL LOGIN / SIGNUP FUNCTIONALITY (AUTHENTICATION)
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!")
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@app.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password1 != password2:
            flash('Passwords do not match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(password1) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('home'))

    return render_template("signup.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/Products")
def products():
    return render_template("Products.html")


@app.route("/")
def Aboutme():
    return render_template("aboutme.html")

@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)


