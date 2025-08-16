from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(1), default='A')  # A-Available, O-Occupied
    
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)
    status = db.Column(db.String(10), default='active')  # active, completed

# Helper Functions
def create_admin_user():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@parking.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

def create_parking_spots(lot_id, max_spots):
    for i in range(1, max_spots + 1):
        spot = ParkingSpot(
            lot_id=lot_id,
            spot_number=f"S{i:03d}",
            status='A'
        )
        db.session.add(spot)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    parking_lots = ParkingLot.query.all()
    total_spots = db.session.query(ParkingSpot).count()
    occupied_spots = db.session.query(ParkingSpot).filter_by(status='O').count()
    available_spots = total_spots - occupied_spots
    total_users = User.query.filter_by(is_admin=False).count()
    
    stats = {
        'total_lots': len(parking_lots),
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'available_spots': available_spots,
        'total_users': total_users
    }
    
    return render_template('admin_dashboard.html', parking_lots=parking_lots, stats=stats)

@app.route('/admin/create_lot', methods=['GET', 'POST'])
def create_lot():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lot = ParkingLot(
            prime_location_name=request.form['location_name'],
            address=request.form['address'],
            pin_code=request.form['pin_code'],
            price_per_hour=float(request.form['price_per_hour']),
            maximum_number_of_spots=int(request.form['max_spots'])
        )
        
        db.session.add(lot)
        db.session.commit()
        
        # Create parking spots
        create_parking_spots(lot.id, lot.maximum_number_of_spots)
        db.session.commit()
        
        flash('Parking lot created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_lot.html')

@app.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.prime_location_name = request.form['location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_hour = float(request.form['price_per_hour'])
        
        new_max_spots = int(request.form['max_spots'])
        current_spots = len(lot.parking_spots)
        
        if new_max_spots > current_spots:
            # Add new spots
            for i in range(current_spots + 1, new_max_spots + 1):
                spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=f"S{i:03d}",
                    status='A'
                )
                db.session.add(spot)
        elif new_max_spots < current_spots:
            # Remove spots (only if they're available)
            spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').offset(new_max_spots).all()
            for spot in spots_to_remove:
                db.session.delete(spot)
        
        lot.maximum_number_of_spots = new_max_spots
        db.session.commit()
        
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_lot.html', lot=lot)

@app.route('/admin/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if all spots are available
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    if occupied_spots > 0:
        flash('Cannot delete parking lot with occupied spots!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.session.delete(lot)
    db.session.commit()
    
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/view_spots/<int:lot_id>')
def view_spots(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    # Get reservation details for occupied spots
    spot_details = []
    for spot in spots:
        detail = {'spot': spot}
        if spot.status == 'O':
            reservation = Reservation.query.filter_by(spot_id=spot.id, status='active').first()
            if reservation:
                detail['reservation'] = reservation
                # Calculate duration
                if reservation.parking_timestamp:
                    duration_hours = (datetime.utcnow() - reservation.parking_timestamp).total_seconds() / 3600
                    detail['duration_hours'] = duration_hours
        spot_details.append(detail)
    
    return render_template('view_spots.html', lot=lot, spot_details=spot_details)

@app.route('/admin/users')
def view_users():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    users = User.query.filter_by(is_admin=False).all()
    return render_template('view_users.html', users=users)

@app.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # Fixed: Use 'status' instead of 'is_active'
    active_reservations = Reservation.query.filter_by(user_id=user_id, status='active').all()
    completed_reservations = Reservation.query.filter_by(user_id=user_id, status='completed').order_by(Reservation.parking_timestamp.desc()).all()
    
    # Calculate current costs and durations for active reservations
    for reservation in active_reservations:
        if reservation.parking_timestamp:
            duration_hours = (datetime.utcnow() - reservation.parking_timestamp).total_seconds() / 3600
            reservation.current_duration = duration_hours
            reservation.current_cost = duration_hours * reservation.parking_spot.parking_lot.price_per_hour
    
    # Calculate durations for completed reservations
    for reservation in completed_reservations:
        if reservation.parking_timestamp and reservation.leaving_timestamp:
            duration_hours = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
            reservation.duration_hours = duration_hours
    
    return render_template('user_dashboard.html', 
                         active_reservations=active_reservations,
                         completed_reservations=completed_reservations)

@app.route('/user/book_parking')
def book_parking():
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('login'))
    
    parking_lots = ParkingLot.query.all()
    lot_availability = []
    
    for lot in parking_lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        lot_availability.append({
            'lot': lot,
            'available_spots': available_spots
        })
    
    return render_template('book_parking.html', lot_availability=lot_availability)

@app.route('/user/confirm_booking/<int:lot_id>', methods=['GET', 'POST'])
def confirm_booking(lot_id):
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']
        
        # Check if user already has an active reservation
        existing_reservation = Reservation.query.filter_by(user_id=session['user_id'], status='active').first()
        if existing_reservation:
            flash('You already have an active parking reservation! Please release it first.', 'error')
            return redirect(url_for('user_dashboard'))
        
        # Find first available spot
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        
        if not available_spot:
            flash('No available spots in this parking lot!', 'error')
            return redirect(url_for('book_parking'))
        
        # Create reservation
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=session['user_id'],
            vehicle_number=vehicle_number,
            status='active'
        )
        
        # Update spot status
        available_spot.status = 'O'
        
        db.session.add(reservation)
        db.session.commit()
        
        flash(f'Parking spot {available_spot.spot_number} booked successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('confirm_booking.html', lot=lot)

@app.route('/user/release_parking/<int:reservation_id>')
def release_parking(reservation_id):
    if not session.get('user_id') or session.get('is_admin'):
        return redirect(url_for('login'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != session['user_id']:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('user_dashboard'))
    
    if reservation.status != 'active':
        flash('This reservation is already completed!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Calculate parking cost
    if reservation.parking_timestamp:
        duration_hours = (datetime.utcnow() - reservation.parking_timestamp).total_seconds() / 3600
        lot = reservation.parking_spot.parking_lot
        # Minimum 1 hour charge
        cost = max(duration_hours * lot.price_per_hour, lot.price_per_hour)
        
        reservation.leaving_timestamp = datetime.utcnow()
        reservation.parking_cost = round(cost, 2)
        reservation.status = 'completed'
        
        # Update spot status
        reservation.parking_spot.status = 'A'
        
        db.session.commit()
        
        flash(f'Parking released successfully! Duration: {duration_hours:.1f} hours, Total cost: ₹{cost:.2f}', 'success')
    else:
        flash('Error calculating parking cost!', 'error')
    
    return redirect(url_for('user_dashboard'))

# API Routes
@app.route('/api/parking_lots')
def api_parking_lots():
    lots = ParkingLot.query.all()
    return jsonify([{
        'id': lot.id,
        'name': lot.prime_location_name,
        'address': lot.address,
        'price_per_hour': lot.price_per_hour,
        'total_spots': lot.maximum_number_of_spots,
        'available_spots': ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
    } for lot in lots])

@app.route('/api/parking_spots/<int:lot_id>')
def api_parking_spots(lot_id):
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return jsonify([{
        'id': spot.id,
        'spot_number': spot.spot_number,
        'status': spot.status
    } for spot in spots])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    app.run(debug=True)
