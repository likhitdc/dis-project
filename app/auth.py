
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

from app.models import User
from app import db

auth = Blueprint('auth', __name__)

def dummy_verification_link(user):
    # Generate a dummy link for verification and store it in the session for display
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    user.token_expiry = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()
    session['verification_link'] = url_for('auth.verify_email', token=token, _external=True)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', 'error')
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password, is_verified=False)

        db.session.add(new_user)
        db.session.commit()

        # Instead of sending an email, insert a dummy link into the flash message
        dummy_verification_link(new_user)
        flash('Account created. Please verify your email. <a href="{}">Click here to verify</a>.'.format(session.get('verification_link')), 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        flash('Invalid or expired verification link', 'error')
        return redirect(url_for('auth.login'))

    if user.token_expiry and user.token_expiry < datetime.utcnow():
        flash('Verification link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.resend_verification'))

    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None
    db.session.commit()

    flash('Your email has been verified successfully! You can now login.', 'success')
    return render_template('verify_email.html', success=True)

@auth.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with that email', 'error')
            return redirect(url_for('auth.resend_verification'))

        if user.is_verified:
            flash('Your email is already verified. You can login.', 'info')
            return redirect(url_for('auth.login'))

        # Dummy link in flash, not email
        dummy_verification_link(user)
        flash('Verification link: <a href="{}">Click here to verify</a>.'.format(session.get('verification_link')), 'success')
        return redirect(url_for('auth.login'))

    return render_template('resend_verification.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with that email', 'error')
            return redirect(url_for('auth.login'))

        if not user.is_verified and not user.is_admin:
            flash('Please verify your email before logging in', 'warning')
            return redirect(url_for('auth.login'))

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))

@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            token = secrets.token_urlsafe(32)
            user.verification_token = token
            user.token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            # Instead of email, flash link for demo/dev
            flash('Reset link: <a href="{}">Click here to reset your password</a>.'.format(reset_url), 'info')
        else:
            flash('If an account exists with that email, we have sent password reset instructions', 'info')
        return redirect(url_for('auth.login'))

    return render_template('reset_password_request.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user or (user.token_expiry and user.token_expiry < datetime.utcnow()):
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('auth.reset_password_request'))

    if request.method == 'POST':
        password = request.form.get('password')
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        user.verification_token = None
        user.token_expiry = None
        db.session.commit()

        flash('Your password has been updated. You can now login with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')

# ACCOUNT MANAGEMENT

@auth.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        field = request.form.get('field')
        value = request.form.get('value')
        if field == 'name':
            current_user.name = value
            db.session.commit()
            flash('Name updated successfully!', 'success')
        elif field == 'email':
            # Check if email taken
            other = User.query.filter_by(email=value).first()
            if other and other.id != current_user.id:
                flash('Email already used by another account.', 'error')
            else:
                current_user.email = value
                db.session.commit()
                flash('Email updated successfully!', 'success')
        elif field == 'password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            if not check_password_hash(current_user.password, current_password):
                flash('Current password incorrect.', 'error')
            else:
                current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
                flash('Password updated successfully!', 'success')
        return redirect(url_for('auth.account'))

    return render_template('account.html', user=current_user)

