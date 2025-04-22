
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

from app.models import Movie, Theatre, Showtime, Seat, Booking, BookedSeat
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@main.route('/movies')
def movies():
    movies = Movie.query.all()
    return render_template('movies.html', movies=movies)

@main.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    # Get unique dates for this movie's showtimes
    showtimes = Showtime.query.filter_by(movie_id=movie_id).all()
    dates = sorted(set(showtime.date for showtime in showtimes))
    
    return render_template('movie_details.html', movie=movie, dates=dates)

@main.route('/showtimes/<int:movie_id>/<date>')
def showtimes(movie_id, date):
    movie = Movie.query.get_or_404(movie_id)
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get theatres and showtimes for this movie and date
    showtimes = Showtime.query.filter_by(movie_id=movie_id, date=date_obj).all()
    theatres_with_showtimes = {}
    
    for showtime in showtimes:
        if showtime.theatre.id not in theatres_with_showtimes:
            theatres_with_showtimes[showtime.theatre.id] = {
                'theatre': showtime.theatre,
                'showtimes': []
            }
        theatres_with_showtimes[showtime.theatre.id]['showtimes'].append(showtime)
    
    return render_template('showtimes.html', movie=movie, date=date, theatres_with_showtimes=theatres_with_showtimes)

@main.route('/seats/<int:showtime_id>')
@login_required
def seat_selection(showtime_id):
    showtime = Showtime.query.get_or_404(showtime_id)
    seats = Seat.query.filter_by(showtime_id=showtime_id).all()
    
    # Organize seats by class
    seat_classes = {}
    for seat in seats:
        if seat.seat_class not in seat_classes:
            seat_classes[seat.seat_class] = []
        seat_classes[seat.seat_class].append(seat)
    
    return render_template('seat_selection.html', showtime=showtime, seat_classes=seat_classes)

@main.route('/book', methods=['POST'])
@login_required
def book_seats():
    showtime_id = request.form.get('showtime_id')
    seat_ids = request.form.getlist('seat_ids')
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')
    
    if not seat_ids:
        flash('No seats selected', 'error')
        return redirect(url_for('main.seat_selection', showtime_id=showtime_id))
    
    showtime = Showtime.query.get_or_404(showtime_id)
    seats = Seat.query.filter(Seat.id.in_(seat_ids)).all()
    
    # Check if seats are still available
    unavailable_seats = []
    for seat in seats:
        if seat.occupied:
            unavailable_seats.append(seat.seat_number)
    
    if unavailable_seats:
        flash(f'These seats are no longer available: {", ".join(unavailable_seats)}', 'error')
        return redirect(url_for('main.seat_selection', showtime_id=showtime_id))
    
    # Calculate total amount
    total_amount = sum(seat.price for seat in seats)
    
    # Verify Razorpay payment (in production, you would verify the payment here)
    # For simplicity, we'll assume the payment is valid
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        showtime_id=showtime_id,
        total_amount=total_amount
    )
    db.session.add(booking)
    
    # Mark seats as occupied and create booked_seat records
    for seat in seats:
        seat.occupied = True
        booked_seat = BookedSeat(booking=booking, seat=seat)
        db.session.add(booked_seat)
    
    db.session.commit()
    
    flash('Booking successful!', 'success')
    return redirect(url_for('main.booking_confirmation', booking_id=booking.id))

@main.route('/booking/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure user can only see their own bookings
    if booking.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('booking_confirmation.html', booking=booking)

@main.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_time.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)
