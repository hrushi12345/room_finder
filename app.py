import json
import uuid
import urllib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
from dataset_model_training.model_training import recommend_hotels
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
pymysql.install_as_MySQLdb()
from models import db, UserAccount, UserProfile, Room, BookingDetails

app = Flask(__name__)
# 🔹 Set a secret key for sessions and security
app.secret_key = "!@#$%QWER^&*()POIYTREWQ"  # Change this to a secure, random key

# Open and read the config file
with open('config.json', 'r') as file:
    data = json.load(file)
dbUserName = urllib.parse.quote_plus(data['username'])
dbPassword = urllib.parse.quote_plus(data['password'])
dbHost = data['host']
dbName = data['database']
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{dbUserName}:{dbPassword}@{dbHost}/{dbName}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Load dataset from CSV
df = pd.read_csv('dataset_model_training/hotel_reviews.csv')

@app.route('/')
def home():
    return render_template('home.html')


### 🔹 Default Page → Login
# @app.route('/index')
# def index():
#     if 'user_id' in session:
#         return redirect(url_for('index'))  # If logged in, go to search
#     return redirect(url_for('login'))  # Default page is login

### 🔹 User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')        
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        # Check if user already exists
        existing_user = UserAccount.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for('register'))

        # Create user account
        user_id = str(uuid.uuid4())
        user = UserAccount(userId=user_id, email=email, passwordHash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        profile = UserProfile(
            profileId=str(uuid.uuid4()),
            userId=user_id,
            firstName=first_name,
            lastName=last_name,
            phoneNumber=phone_number,
            updatedAt=datetime.utcnow()
        )
        db.session.add(profile)
        db.session.commit()

        flash("Account created! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

### 🔹 User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = UserAccount.query.filter_by(email=email).first()
        if user and check_password_hash(user.passwordHash, password):
            session['user_id'] = user.userId
            session['email'] = user.email
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials!", "danger")

    return render_template('login.html')

### 🔹 Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

@app.route('/index')
def index():
    """Render the homepage with a searchable hotel dropdown from dataset."""
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in
    region_list = df['region'].unique().tolist()
    return render_template('index.html', region_list=region_list)

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate hotel recommendations based on user input and store search in DB."""

    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in
        
    user_id = session['user_id']
    user = UserProfile.query.filter_by(userId=user_id).first()

    first_name = user.firstName if user else "Guest"
    last_name = user.lastName if user else ""
    
    selected_region = request.form.get('region_name')
    accommodation_type = request.form.get("accommodation_type")
    max_cost = request.form.get("max_cost")

    # Get selected hotel's region
    selected_row = df[df['region'] == selected_region]
    if selected_row.empty:
        print("No region found with that name.")
        recommendations = []
    else:
        selected_row = selected_row.iloc[0]
        region = selected_row['region']
        # Step 1: Filter hotels in the same region (excluding the selected hotel)
        filtered_df = df[df["region"] == region]
                
        if accommodation_type:
            filtered_df = filtered_df[filtered_df["accommodation_type"] == accommodation_type]

        if max_cost:
            try:
                max_cost = float(max_cost)
                filtered_df = filtered_df[filtered_df["cost"] <= max_cost]
            except ValueError:
                print("Invalid cost entered, ignoring max_cost filter.")

        # Recommend similar hotels in the same region
        recommendations = filtered_df.head(5).to_dict(orient="records")

        # Store recommended rooms in the database
        for hotel in recommendations:
            existing_room = Room.query.filter_by(hotel_name=hotel['hotel_name']).first()
            if not existing_room:
                new_room = Room(
                    roomId=str(uuid.uuid4()),
                    ownerId=user_id,
                    hotel_name=hotel['hotel_name'],
                    region=hotel['region'],
                    cost=hotel['cost'],
                    accommodation_type=hotel['accommodation_type'],
                    latitude=hotel['latitude'],
                    longitude=hotel['longitude']
                )
                db.session.add(new_room)
                db.session.commit()

    return render_template('result.html', first_name=first_name, last_name=last_name, recommended_hotels=recommendations, user_email=session['email'])


@app.route('/book_hotel', methods=['POST'])
def book_hotel():
    try:
        hotel_data = request.get_json()  # Get hotel details from frontend
        session['selected_hotel'] = hotel_data  # Store data in session

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/booking_page')
def booking_page():
    if 'selected_hotel' not in session:
        return redirect(url_for('index'))  # Redirect if no hotel selected
    cost = session['selected_hotel']['cost']
    hotel_name = session['selected_hotel']['hotel_name']
    return render_template('booking.html', hotel_name=hotel_name, cost=cost)


@app.route('/book_hotel_database', methods=['POST'])
def book_hotel_database():
    userAccountObj = UserAccount.query.filter_by(email=session['email']).first()
    roomObj = Room.query.filter_by(hotel_name=request.form.get('hotel_name')).first()
    bookingObj = BookingDetails(
        bookingId = str(uuid.uuid4()),
        ownerId = userAccountObj.userId,
        roomId = roomObj.roomId,
        check_in = request.form.get('check_in'),
        check_out = request.form.get('check_out'),
        total_cost = request.form.get('total_cost')
    )
    db.session.add(bookingObj)
    db.session.commit()
    flash("Room booked successfully!", "success")
    return redirect(url_for('booking_details'))

@app.route('/booking_details', methods=['GET'])
def booking_details():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect if no hotel selected
    bookingObj = BookingDetails.query.filter_by(ownerId=session['user_id']).first()
    if bookingObj:
        userProfileObj = UserProfile.query.filter_by(userId=bookingObj.ownerId).first()
        roomObj = Room.query.filter_by(roomId=bookingObj.roomId).first()
        firstName = userProfileObj.firstName
        lastName = userProfileObj.lastName
        hotel_name = roomObj.hotel_name
        check_in = bookingObj.check_in
        check_out = bookingObj.check_out
        total_cost = bookingObj.total_cost
        return render_template('bookingDetails.html', name=firstName+lastName, hotel_name=hotel_name, check_in=check_in, check_out=check_out, total_cost=total_cost)
    else:
        return render_template('bookingDetails.html', name="")

@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect if no hotel selected
    BookingDetails.query.filter_by(ownerId=session['user_id']).delete()
    db.session.commit()  # Commit the changes
    flash("Room booking cancelled successfully!", "success")
    return render_template('bookingDetails.html', name="")

if __name__ == '__main__':
    app.run(debug=True)
