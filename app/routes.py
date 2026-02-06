
from flask import render_template, redirect, url_for, flash, request, session, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User
from app.forms import RegistrationForm, LoginForm
from datetime import datetime, date

main = Blueprint('main', __name__)

@main.route('/dbtest')
def dbtest():
    try:
        db.session.execute('SELECT 1')
        return 'Database connection successful!'
    except Exception as e:
        return f'Database connection failed: {e}'

@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            user.visit_count = (user.visit_count or 0) + 1
            user.last_login_date = date.today()
            user.last_login_time = datetime.now().time()
            db.session.commit()
            session['visit_count'] = user.visit_count
            session['last_login_date'] = user.last_login_date.strftime('%Y-%m-%d')
            session['last_login_time'] = user.last_login_time.strftime('%H:%M:%S')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route("/")
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)
