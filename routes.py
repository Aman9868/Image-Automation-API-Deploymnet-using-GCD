from app import app, db,bcrypt,mail
from flask import render_template,request,redirect,url_for, flash,jsonify
import torch
from numba import cuda
from GPUtil import showUtilization as gpu_usage
from functions import extract_contact_info,extract_airport_codes,first_to_third_person,translate_text
from forms import RegisterForm,LoginForm
from models import User
from flask_login import login_user,logout_user,current_user, login_required

#### -----------------------CUDA Description--------------------##############################3
if torch.cuda.is_available():
    device_count = torch.cuda.device_count()
    for i in range(device_count):
        device_name = torch.cuda.get_device_name(i)
        print(f"Device {i}: {device_name}")
else:
    print("CUDA is not available")
#################-----------------Gpu Memory Releaser----------------------------####################
def free_gpu_cache():
    print("Initial GPU Usage")
    gpu_usage()  
    torch.cuda.empty_cache()
    cuda.select_device(0)
    cuda.close()
    cuda.select_device(0)
    print("GPU Usage after emptying the cache")
    gpu_usage()
free_gpu_cache()        


##-------------------------Homepage--------------------------------------------#####
@app.route("/")
@app.route("/home")
def home_page():
    return render_template('index.html')

@app.route("/projects")
def project_page():
    return render_template('projects.html')
@app.route("/about")
def about_page():
    return render_template('about.html')
@app.route('/base')
def base_page():
    return render_template('base.html')
#####---------------------------Register------------------------------------------#####
@app.route('/register',methods=['GET','POST'])
def register_page():
    form=RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('register_page'))
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('register_page'))
        #password_hash = generate_password_hash(form.password.data).decode('utf-8')
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_create = User(username=form.username.data, email=form.email.data, password=hashed_password,mobile_number=form.mobile_number.data)
        db.session.add(user_create)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login_page'))
    if form.errors !={}:
        for err in form.errors.values():
            flash(f'There was an error with creating a user: {err}', category='danger')
    return render_template('register.html',form=form)

#####-----------------------Login Page-----------------------------------#######
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home_page'))
       else:
            flash('Email and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)
app.run(debug=True)