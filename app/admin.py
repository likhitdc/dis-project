
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

from app.models import Movie, Theatre, Showtime, Seat, Booking
from app import db
from app.utils import send_booking_deletion_notification

admin = Blueprint('admin', __name__)

# Decorator to check if user is admin
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Unauthorized access', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return login_required(decorated_function)

@admin.route('/')
@admin_required
def dashboard():
    movies_count = Movie.query.count()
    theatres_count = Theatre.query.count()
    showtimes_count = Showtime.query.count()
    bookings_count = Booking.query.count()
    
    return render_template(
        'admin/dashboard.html', 
        movies_count=movies_count, 
        theatres_count=theatres_count,
        showtimes_count=showtimes_count,
        bookings_count=bookings_count
    )

# Admin Bookings Management
@admin.route('/bookings')
@admin_required
def bookings():
    bookings = Booking.query.order_by(Booking.booking_time.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

# Admin Movie Management
@admin.route('/movies')
@admin_required
def movies():
    movies = Movie.query.all()
    return render_template('admin/movies.html', movies=movies)

@admin.route('/movies/add', methods=['GET', 'POST'])
@admin_required
def add_movie():
    if request.method == 'POST':
        title = request.form.get('title')
        genres = request.form.get('genres')
        language = request.form.get('language')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        duration = request.form.get('duration')
        
        new_movie = Movie(
            title=title, 
            genres=genres, 
            language=language,
            description=description,
            image_url=image_url,
            duration=duration
        )
        
        db.session.add(new_movie)
        db.session.commit()
        
        flash('Movie added successfully', 'success')
        return redirect(url_for('admin.movies'))
    
    return render_template('admin/add_movie.html')

@admin.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
@admin_required
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    if request.method == 'POST':
        movie.title = request.form.get('title')
        movie.genres = request.form.get('genres')
        movie.language = request.form.get('language')
        movie.description = request.form.get('description')
        movie.image_url = request.form.get('image_url')
        movie.duration = request.form.get('duration')
        
        db.session.commit()
        
        flash('Movie updated successfully', 'success')
        return redirect(url_for('admin.movies'))
    
    return render_template('admin/edit_movie.html', movie=movie)

@admin.route('/movies/delete/<int:movie_id>', methods=['POST'])
@admin_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    # Get all bookings that will be affected by movie deletion
    affected_bookings = []
    showtimes = Showtime.query.filter_by(movie_id=movie_id).all()
    for showtime in showtimes:
        bookings = Booking.query.filter_by(showtime_id=showtime.id).all()
        for booking in bookings:
            affected_bookings.append(booking)
            send_booking_deletion_notification(booking)
    
    # Delete movie (cascading delete will remove showtimes and related bookings)
    db.session.delete(movie)
    db.session.commit()
    
    flash(f'Movie deleted successfully. {len(affected_bookings)} bookings were affected and customers have been notified.', 'info')
    return redirect(url_for('admin.movies'))

# Admin Theatre Management
@admin.route('/theatres')
@admin_required
def theatres():
    theatres = Theatre.query.all()
    return render_template('admin/theatres.html', theatres=theatres)

@admin.route('/theatres/edit/<int:theatre_id>', methods=['GET', 'POST'])
@admin_required
def edit_theatre(theatre_id):
    theatre = Theatre.query.get_or_404(theatre_id)
    
    if request.method == 'POST':
        theatre.name = request.form.get('name')
        theatre.location = request.form.get('location')
        theatre.total_seats = request.form.get('total_seats', 110)
        
        db.session.commit()
        flash('Theatre updated successfully', 'success')
        return redirect(url_for('admin.theatres'))
    
    return render_template('admin/edit_theatre.html', theatre=theatre)

@admin.route('/theatres/delete/<int:theatre_id>', methods=['POST'])
@admin_required
def delete_theatre(theatre_id):
    theatre = Theatre.query.get_or_404(theatre_id)
    
    # Get all bookings that will be affected by theatre deletion
    affected_bookings = []
    showtimes = Showtime.query.filter_by(theatre_id=theatre_id).all()
    for showtime in showtimes:
        bookings = Booking.query.filter_by(showtime_id=showtime.id).all()
        for booking in bookings:
            affected_bookings.append(booking)
            send_booking_deletion_notification(booking)
    
    # Delete theatre (cascading delete will remove showtimes and related bookings)
    db.session.delete(theatre)
    db.session.commit()
    
    flash(f'Theatre deleted successfully. {len(affected_bookings)} bookings were affected and customers have been notified.', 'info')
    return redirect(url_for('admin.theatres'))

@admin.route('/theatres/add', methods=['GET', 'POST'])
@admin_required
def add_theatre():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        total_seats = request.form.get('total_seats', 110)  # Set default to 110
        
        new_theatre = Theatre(name=name, location=location, total_seats=total_seats)
        db.session.add(new_theatre)
        db.session.commit()
        
        flash('Theatre added successfully', 'success')
        return redirect(url_for('admin.theatres'))
    
    return render_template('admin/add_theatre.html')

# Admin Showtime Management
@admin.route('/showtimes')
@admin_required
def showtimes():
    showtimes = Showtime.query.all()
    return render_template('admin/showtimes.html', showtimes=showtimes)

@admin.route('/showtimes/add', methods=['GET', 'POST'])
@admin_required
def add_showtime():
    if request.method == 'POST':
        movie_id = request.form.get('movie_id')
        theatre_id = request.form.get('theatre_id')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        time = datetime.strptime(request.form.get('time'), '%H:%M').time()
        
        # Get pricing information
        economy_price = request.form.get('economy_price', 190.00)
        standard_price = request.form.get('standard_price', 250.00)
        premium_price = request.form.get('premium_price', 320.00)
        
        # Create showtime
        new_showtime = Showtime(
            movie_id=movie_id, 
            theatre_id=theatre_id, 
            date=date, 
            time=time,
            economy_price=economy_price,
            standard_price=standard_price,
            premium_price=premium_price
        )
        db.session.add(new_showtime)
        db.session.flush()  # To get the showtime ID
        
        # Create seats for this showtime
        theatre = Theatre.query.get(theatre_id)
        
        # For a theater layout more similar to the image with ~16 seats per row
        # with 3 sections (aisle after seat 3 and 13)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        seats_per_row = 16  # Fixed number of seats per row
        
        for row in rows:
            for num in range(1, seats_per_row + 1):
                seat_number = f"{row}{num}"
                
                # Determine seat class and price based on position
                if row in ['A', 'B']:
                    seat_class = 'premium'
                    price = float(premium_price)
                elif row in ['C', 'D', 'E']:
                    seat_class = 'standard'
                    price = float(standard_price)
                else:
                    seat_class = 'economy'
                    price = float(economy_price)
                
                seat = Seat(
                    showtime_id=new_showtime.id,
                    seat_number=seat_number,
                    seat_class=seat_class,
                    occupied=False,
                    price=price
                )
                db.session.add(seat)
        
        db.session.commit()
        flash('Showtime and seats added successfully', 'success')
        return redirect(url_for('admin.showtimes'))
    
    movies = Movie.query.all()
    theatres = Theatre.query.all()
    return render_template('admin/add_showtime.html', movies=movies, theatres=theatres)

@admin.route('/showtimes/edit/<int:showtime_id>', methods=['GET', 'POST'])
@admin_required
def edit_showtime(showtime_id):
    showtime = Showtime.query.get_or_404(showtime_id)
    
    if request.method == 'POST':
        # Update prices
        showtime.economy_price = float(request.form.get('economy_price', 190.00))
        showtime.standard_price = float(request.form.get('standard_price', 250.00))
        showtime.premium_price = float(request.form.get('premium_price', 320.00))
        
        # Update seat prices based on their class
        seats = Seat.query.filter_by(showtime_id=showtime_id).all()
        for seat in seats:
            if seat.seat_class == 'economy':
                seat.price = showtime.economy_price
            elif seat.seat_class == 'standard':
                seat.price = showtime.standard_price
            elif seat.seat_class == 'premium':
                seat.price = showtime.premium_price
        
        db.session.commit()
        flash('Showtime prices updated successfully', 'success')
        return redirect(url_for('admin.showtimes'))
    
    return render_template('admin/edit_showtime.html', showtime=showtime)

@admin.route('/showtimes/delete/<int:showtime_id>', methods=['POST'])
@admin_required
def delete_showtime(showtime_id):
    showtime = Showtime.query.get_or_404(showtime_id)
    
    # Get all bookings that will be affected by showtime deletion
    bookings = Booking.query.filter_by(showtime_id=showtime_id).all()
    for booking in bookings:
        send_booking_deletion_notification(booking)
    
    # Delete showtime and related records
    db.session.delete(showtime)
    db.session.commit()
    
    flash(f'Showtime deleted successfully. {len(bookings)} bookings were affected and customers have been notified.', 'info')
    return redirect(url_for('admin.showtimes'))
