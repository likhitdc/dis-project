from datetime import datetime, timedelta
import secrets

# Email functions
def send_email(to, subject, template):
    # In production, this would connect to an actual SMTP server
    # For now, we'll just print the email to the console
    print(f"====== EMAIL TO: {to} ======")
    print(f"SUBJECT: {subject}")
    print(f"BODY: {template}")
    print("====== END EMAIL ======")
    return True

def send_verification_email(user):
    # No-op for dummy verification
    pass

def send_booking_deletion_notification(booking):
    from app.models import User
    
    user = User.query.get(booking.user_id)
    movie = booking.showtime.movie
    theatre = booking.showtime.theatre
    showtime_date = booking.showtime.date.strftime('%d %b, %Y')
    showtime_time = booking.showtime.time.strftime('%I:%M %p')
    
    template = f"""
    Hello {user.name},
    
    We regret to inform you that your booking #{booking.id} has been cancelled.
    
    Booking Details:
    Movie: {movie.title}
    Theatre: {theatre.name}
    Date: {showtime_date}
    Time: {showtime_time}
    
    Your payment of ₹{booking.total_amount} will be refunded within 5-7 business days.
    
    We apologize for any inconvenience this may have caused.
    
    Thank you for your understanding,
    Flick Ticket Palace Team
    """
    
    send_email(user.email, "Booking Cancellation - Flick Ticket Palace", template)
