
from flask import Blueprint, request, jsonify
import uuid
from flask_login import login_required
from app.models import Seat
from app import db, razorpay_client

api = Blueprint('api', __name__)

@api.route('/create_order', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    amount = data.get('amount')
    showtime_id = data.get('showtime_id')
    seat_ids = data.get('seat_ids')
    
    # Check if seats are still available before creating order
    seats = Seat.query.filter(Seat.id.in_(seat_ids)).all()
    occupied_seats = [seat.id for seat in seats if seat.occupied]
    
    if occupied_seats:
        return jsonify({
            'status': 'error',
            'message': 'Some seats are no longer available',
            'occupied_seats': occupied_seats
        }), 400
    
    # Create Razorpay Order
    order_amount = int(float(amount))
    order_currency = 'INR'
    order_receipt = f'order_{uuid.uuid4().hex}'
    
    # Create razorpay order
    razorpay_order = razorpay_client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'receipt': order_receipt
    })
    
    return jsonify({
        'status': 'success',
        'order_id': razorpay_order['id']
    })

@api.route('/check_seats', methods=['POST'])
def check_seats():
    data = request.get_json()
    seat_ids = data.get('seat_ids', [])
    
    seats = Seat.query.filter(Seat.id.in_(seat_ids)).all()
    occupied_seats = [seat.id for seat in seats if seat.occupied]
    
    return jsonify({
        'status': 'success',
        'occupied_seats': occupied_seats
    })
