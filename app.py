from flask import Flask, render_template, flash, redirect, url_for, request 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,LoginManager,current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime
from flask_migrate import Migrate
import sqlite3
import os
from wtforms.widgets import TextArea
from webform import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm,VirtualForm
from flask_ckeditor import CKEditor
import uuid as uuid
import os 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
from passlib.hash import pbkdf2_sha256
from sanitize_filename import sanitize


#####################################################################
#####  SETUP THE INSTANCE OF THE APPLICATION AND DATABASES ##########
#####################################################################   

#Create a flask instance
app= Flask(__name__)
#add ckeditor
ckeditor=CKEditor(app)
#Add database + connexion to it
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/log_users'
#Secret Key
app.config['SECRET_KEY'] ='secret!'
app.config['UPLOAD_FOLDER'] = 'static/files'
#Initialize the database
db=SQLAlchemy(app)


#flask login 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#pass the form to the navbar.html
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#login function loadiong information by id 
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#####################################################################
#####  END OF SETUP             #####################################
#####################################################################   
#####  START OF FUNCTION AND ROUTE     ##############################
#####################################################################


#create admin page
@app.route('/admin',methods=['GET','POST'])
@login_required
def admin():
    id=current_user.id
    our_users=Users.query.order_by(Users.date_added.desc()).all()
    if id ==1:
        return render_template('admin.html',our_users=our_users)
    else: 
        flash('You are not authorized to access this page')
        return redirect(url_for('dashboard'))
    

#create Login page
@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user:
            #check password
            if  pbkdf2_sha256.verify(form.password.data, user.password_hash):
                login_user(user)
                flash('You are now logged in')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password')
        else:
            flash('That username does not exist')
    return render_template('login.html',form=form)

#create logout page
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('You are now logged out')
    return redirect(url_for('login')) 


#create Dashboard page
@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form = UserForm()
    id=current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.profile_pic = request.files['profile_pic']
        #grab image name
        pic_filename = sanitize(name_to_update.profile_pic.filename)
        #generate uuid to make sure it is unique
        pic_name = str(uuid.uuid1()) +"_"+ pic_filename
        name_to_update.profile_pic=pic_name
        try:
            db.session.commit()
            flash("User updated")
            return render_template('dashboard.html',form=form,name_to_update=name_to_update,id=id)
        except:
            flash("User not updated")
            return render_template('dashboard.html',form=form,name_to_update=name_to_update,id=id)
    else:
        return render_template('dashboard.html',form=form, name_to_update=name_to_update,id=id)  



#create the search function

@app.route('/search',methods=["POST"])
def search():
    form=SearchForm()
    posts=Posts.query
    #Get data from submit button
    post.searched = form.searched.data
    #Query the database
    posts=posts.filter(Posts.content.like('%' + post.searched + '%'))
    posts=posts.order_by(Posts.title).all()
    if form.validate_on_submit():
        post.searched= form.searched.data
    return render_template('search.html',form=form,searched=post.searched,posts=posts)

@app.route('/uploaded')
def posts():
    #grab all the posts 
    posts = Posts.query.order_by(Posts.date_posted).all()
    return render_template('posts.html',posts=posts)

@app.route('/uploaded/<int:id>', methods=['GET','POST'])
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html',post=post)

@app.route('/uploaded/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        #update database record
        db.session.add(post)
        db.session.commit() 
        flash("Post updated")
        return redirect(url_for('post',id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.content.data = post.content
        form.slug.data = post.slug
        return render_template('edit_post.html',form=form)
    else:
        flash("You are not allowed to edit this post")
        posts = Posts.query.order_by(Posts.date_posted).all()
        return render_template('posts.html',posts=posts)
    
@app.route('/uploaded/delete/<int:id>', methods=['GET','POST'])
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id=current_user.id
    if id == post_to_delete.poster_id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post deleted")
            posts = Posts.query.order_by(Posts.date_posted).all()
            return render_template('posts.html',posts=posts)
        except:
            flash("Post not deleted")
            posts = Posts.query.order_by(Posts.date_posted).all()
            return render_template('posts.html',posts=posts)
    else:
        flash("You are not allowed to delete this post")
        posts = Posts.query.order_by(Posts.date_posted).all()
        return render_template('posts.html',posts=posts)
    

@app.route('/add-post', methods=['GET','POST'])
@login_required
def add_post():
    form = PostForm()
    flash('Add Post')
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster,slug=form.slug.data,file_path=form.file.data)
        form.title.data = ''
        form.content.data = ''
        file=form.file.data
        db.session.add(post)
        db.session.commit()
        flash("Post added")
    else:
        flash("Post not added")
    return render_template('add_post.html',form=form)


#Update database Record
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User updated")
            return render_template('update.html',form=form,name_to_update=name_to_update,id=id)
        except:
            flash("User not updated")
            return render_template('update.html',form=form,name_to_update=name_to_update,id=id)
    else:
        return render_template('update.html',form=form, name_to_update=name_to_update,id=id)           

#delete a record
@app.route('/delete/<int:id>', methods=['GET','POST'])
def delete(id):
    name=None
    form=UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted")
        our_users=Users.query.order_by(Users.date_added.desc()).all() 
        return render_template('add_user.html',form=form,name=name,our_users=our_users)
    except:
        flash("User not deleted")
        return render_template('add_user.html',form=form,name=name,our_users=our_users)
    



@app.route('/user/add', methods=['GET','POST'])
def add_user():
   name = None
   username = None
   form=UserForm()
   if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #hash the password
            hashed_pw= pbkdf2_sha256.hash(form.password_hash.data)
            user=Users(name=form.name.data,email=form.email.data,password_hash=hashed_pw,username=form.username.data)
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.email.data=''
        form.username.data=''
        form.password_hash.data=''
        submit=""
        flash("User added successfully")
   our_users=Users.query.order_by(Users.date_added.desc()).all()  
   return render_template('add_user.html',form=form,name=name,username=username,our_users=our_users)
    
@app.route('/virtual_lab1', methods=['GET', 'POST'])
def virtual_lab1():
    form=VirtualForm()
    if form.validate_on_submit():
        # INPUT DATA
        Input_RGB_Image = cv2.imread("C:\\Users\\carl1\\OneDrive\\Bureau\\CESI\\stage\\web\\v0.3\\testpy\\6-12mm_Red_Samsung_Perso_12MP.png")[..., ::-1]
        Input_BW_Image = Input_RGB_Image[:, :, 0]
        n_Colors = 2

        colors = [
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 1],
        [0, 1, 0],
        [1, 1, 0],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 1]
        ]

        X, Y, _ = Input_RGB_Image.shape

        # VARIABLES
        Stack = np.zeros((X, Y, 4), dtype=np.float32)
        Surface_Area = np.zeros(n_Colors)
        Cluster_Name = [""] * n_Colors

        # CALCULATIONS
        Edge_BSE_Image = cv2.Canny(Input_BW_Image, 100, 200) / 255.0
        Edge_Smoothed_BSE_Image = cv2.GaussianBlur(Edge_BSE_Image, (0, 0), 1)

        Transformed_RGB_Image = Input_RGB_Image / 255.0

        Stack[:, :, :3] = Transformed_RGB_Image
        Stack[:, :, 3] = Edge_BSE_Image

        pixels = Transformed_RGB_Image.reshape((-1, 3))
        kmeans = KMeans(n_clusters=n_Colors, n_init=3).fit(pixels)
        pixel_labels = kmeans.labels_.reshape(X, Y)

        masks = [pixel_labels == i for i in range(n_Colors)]
        clusters = [Input_RGB_Image * mask[:, :, np.newaxis] for mask in masks]
        areas = [np.mean(mask) for mask in masks]

        for i, area in enumerate(areas):
            Surface_Area[i] = 100 * area
            Cluster_Name[i] = f"Cluster {i+1}"

            Matrix = np.zeros((X, Y, 3, n_Colors))

            for s in range(3):
                for i in range(n_Colors):
                    Matrix[:, :, s, i] = masks[i] * colors[i][s]

                    RGB_Clusters = np.sum(Matrix, axis=3)

        # Create table using pandas
        T = pd.DataFrame({
        'Cluster_Name': Cluster_Name,
        'Surface_Area': Surface_Area
        })

        # FIGURES
        plt.figure(1)
        plt.imshow(Input_RGB_Image)
        plt.title('Input RGB Image')

        plt.figure(2)
        plt.imshow(Input_BW_Image, cmap='gray')
        plt.title('Input BW Image')

        plt.figure(3)
        plt.imshow(RGB_Clusters)
        plt.title('RGB Clusterized image')

        plt.figure(4)
        plt.imshow(Edge_BSE_Image, cmap='gray')
        plt.title('Edge Detection')

        plt.figure(5)
        plt.imshow(Edge_Smoothed_BSE_Image, cmap='gray')
        plt.title('Smoothed Edge Detection')

        # Save the figures to a file
        plt.savefig('static/images/virtualll_lab1.png')

        # Clear the figures to free up memory
        plt.clf()

    return render_template('virtual_lab1.html', form=form, plot_data='data:image/png;base64,{{ plotData }}')    
def get_image():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf8')

@app.route('/virtual_lab2', methods=['GET', 'POST'])
def virtual_lab2():
    # Configurez le chemin d'accès à R
    #{robjects.r('Sys.setenv(R_HOME="C:/Program Files/R/R-4.3.2")')

    # Code R pour générer le diagramme ternaire (à insérer ici)
    #r = robjects.r

# Charger la bibliothèque Ternary
    #r('library("Ternary")')

# Exécuter TernaryPlot()
    #r('TernaryPlot()')
    
    # Enregistrez le diagramme dans un fichier image ou dans un objet BytesIO
    #plt.savefig('C:\\Users\\carl1\\OneDrive\\Bureau\\CESI\\stage\\web\\v0.3\\static\\images\\plot.png')
    
    # Convertissez l'image en base64
    #with open('chemin/vers/diagramme.png', 'rb') as img_file:
                  #img_base64 = base64.b64encode(img_file.read()).decode()

    # Renvoyez la page HTML avec l'image ternaire incorporée
    return render_template('virtual_lab2.html')  

@app.route('/upload', methods=['POST'])
def upload():
    return render_template('upload.html')

@app.route('/')
def index():
    return render_template('index.html')

###############################
# custom error Pages
###############################

#Invalid URL 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Invalid Server Error  
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


##############################################################
####    DATABASE SETUP                ########################
##############################################################

#Create a upload model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text) 
    #author = db.Column(db.String(200))
    file_path = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime,default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #create a foreign key to link users refer to the primary key 
    poster_id=db.Column(db.Integer,db.ForeignKey('users.id'))

#Create a model
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False,unique=True)
    date_added= db.Column(db.DateTime,default=datetime.utcnow)
    profile_pic= db.Column(db.String(200),nullable=True)
    #password + hashing
    password_hash= db.Column(db.String(128))
    #User can have multiple posts
    posts = db.relationship('Posts',backref='poster')
    @property 
    def password(self):
        raise AttributeError('You cannot read the password attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    #create A string
    def __repr__(self):
        return '<User {}>'.format(self.name)

with app.app_context():
    db.create_all()

    
#####################################################################
#####  END OF DATABASES SETUP #######################################
#####################################################################   


if __name__ == '__main__':
    app.run(debug=True)   

