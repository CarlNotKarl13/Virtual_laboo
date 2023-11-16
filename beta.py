from flask import Flask, render_template, flash, redirect, url_for, request 
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,LoginManager,current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime
from flask_migrate import Migrate
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 
from wtforms.widgets import TextArea

#Create a flask instance
app= Flask(__name__)
#Add database + connexion to it
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/db_user'
#Secret Key
app.config['SECRET_KEY'] ='secret!'
app.config['UPLOAD_FOLDER'] = 'static/files'
#Initialize the database
db=SQLAlchemy(app)

#flask login 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#create the login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')

#create Login page
@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user:
            #check password
            if check_password_hash(user.password_hash,form.password.data):
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
    return render_template('dashboard.html')

#Create a upload model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text) 
    author = db.Column(db.String(200))
    file_path = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime,default=datetime.utcnow)
    slug = db.Column(db.String(255))
#Create a post form

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    file= FileField('File', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Create a model
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False,unique=True)
    date_added= db.Column(db.DateTime,default=datetime.utcnow)
    #password + hashing
    password_hash= db.Column(db.String(128))
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
    

#create a form class
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password_hash=PasswordField('Password', validators=[DataRequired(),EqualTo('password_hash2',message= 'Passwords must match')])
    password_hash2=PasswordField('Comfirm Password ', validators=[DataRequired()])
    submit = SubmitField('Submit')

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
        post.author = form.author.data
        post.slug = form.slug.data
        #update database record
        db.session.add(post)
        db.session.commit()
        flash("Post updated")
        return redirect(url_for('post',id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    form.author.data = post.author
    form.slug.data = post.slug
    return render_template('edit_post.html',form=form)

@app.route('/uploaded/delete/<int:id>', methods=['GET','POST'])
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
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


@app.route('/add-post', methods=['GET','POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data,slug=form.slug.data,file_path=form.file.data)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        file=form.file.data
        db.session.add(post)
        db.session.commit()
        flash("Post added")
    return render_template('add_post.html',form=form)


#Update database Record
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
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
    

#create a form class
class NamerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

#create a form class
class PasswordForm(FlaskForm):
    email = StringField('eamil', validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



@app.route('/user/add', methods=['GET','POST'])
def add_user():
   name = None
   username = None
   form=UserForm()
   if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #hash the password
            hashed_pw= generate_password_hash(form.password_hash.data, method="pbkdf2:sha256")
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
    
    


@app.route('/test_pwd', methods=['GET','POST'])
def test_pw():
    email=None
    password=None
    pw_to_check=None
    passed= None
    form=PasswordForm()    

    #Validate the form data
    if form.validate_on_submit():
        email=form.email.data
        password=form.password_hash.data
        form.email.data=''
        form.password_hash.data=''
        pw_to_check = Users.query.filter_by(email=email).first()
        submit="" 
        #lookup users in the database
        passed=check_password_hash(pw_to_check.password_hash,password)
        flash("You logged in successfully")
    return render_template('test_pwd.html',email=email,password=password,pw_to_check=pw_to_check,passed=passed, form=form)


@app.route('/name', methods=['GET','POST'])
def name():
    name=None
    password=None
    form=NamerForm()    
    #Validate the form data
    if form.validate_on_submit():
        name=form.name.data
        form.name.data=''
        password=form.password.data
        submit="" 
        flash("You logged in successfully")
    return render_template('name.html',name=name, form=form)

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


if __name__ == '__main__':
    app.run(debug=True)   

