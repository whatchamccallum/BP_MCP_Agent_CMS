"""
Home views for the web interface.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

from api.models import db, User

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/')
def index():
    """Home page."""
    return render_template('index.html')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@home_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    form = LoginForm()
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            user = User.query.filter_by(username=username).first()
            if not user or not user.verify_password(password):
                return jsonify({'error': 'Invalid username or password'}), 401
            access_token = create_access_token(identity=user.id)
            return jsonify({'access_token': access_token})
        elif form.validate_on_submit():
            # Get form data
            username = form.username.data
            password = form.password.data
            
            # Find user
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.verify_password(password):
                flash('Invalid username or password', 'danger')
                return render_template('login.html', form=form)
            
            # Create access token - convert ID to string to avoid JWT decoding issues
            access_token = create_access_token(identity=str(user.id))
            
            # Store token in session
            session.clear()
            session['jwt_token'] = access_token
            print(f"DEBUG: JWT token stored in session: {access_token[:10]}...")
            
            # Create response for redirect
            response = redirect(url_for('dashboard.index'))
            
            # Set JWT as a cookie as well for redundancy
            response.set_cookie(
                'jwt_token',
                access_token,
                httponly=False,  # Allow JavaScript access
                secure=request.is_secure,
                max_age=3600,  # 1 hour
                path='/'
            )
            
            return response
        else:
            # Handle invalid form submission
            if request.is_json:
                return jsonify({'error': 'Invalid form submission'}), 400
            else:
                flash('Invalid form submission', 'danger')
                return render_template('login.html', form=form)
    elif request.is_json:
        return jsonify({'error': 'Invalid request method'}), 405
    
    # CSRF is handled automatically by Flask-WTF
    
    return render_template('login.html', form=form)


@home_blueprint.route('/logout')
def logout():
    """Logout."""
    # Clear session
    session.clear()
    
    # Redirect to home
    return redirect(url_for('home.index'))


@home_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """Register page."""
    # Check if there are any users
    user_count = User.query.count()
    
    # If there are users, registration requires admin access
    if user_count > 0:
        flash('Registration is disabled. Please contact an administrator.', 'warning')
        return redirect(url_for('home.login'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validate form data
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('register.html')
        
        # Create user
        user = User(
            username=username,
            email=email,
            is_admin=True  # First user is admin
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('home.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')
