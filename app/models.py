
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genres = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # in minutes
    showtimes = db.relationship('Showtime', backref='movie', lazy=True, cascade="all, delete-orphan")

class Theatre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    showtimes = db.relationship('Showtime', backref='theatre', lazy=True, cascade="all, delete-orphan")

class Showtime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    economy_price = db.Column(db.Float, default=190.00)
    standard_price = db.Column(db.Float, default=250.00)
    premium_price = db.Column(db.Float, default=320.00)
    seats = db.relationship('Seat', backref='showtime', lazy=True, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='showtime', lazy=True, cascade="all, delete-orphan")

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    showtime_id = db.Column(db.Integer, db.ForeignKey('showtime.id', ondelete='CASCADE'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_class = db.Column(db.String(20), nullable=False)  # economy, standard, premium
    occupied = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    showtime_id = db.Column(db.Integer, db.ForeignKey('showtime.id', ondelete='CASCADE'), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    seats = db.relationship('BookedSeat', backref='booking', lazy=True, cascade="all, delete-orphan")

class BookedSeat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id', ondelete='CASCADE'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)
    seat = db.relationship('Seat')
