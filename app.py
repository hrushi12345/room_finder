import json
import uuid
import urllib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from dataset_model_training.model_training import recommend_hotels
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
pymysql.install_as_MySQLdb()
from models import db

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

# Importing models
from models import UserAccount, UserProfile, Room

# Load dataset from CSV
df = pd.read_csv('dataset_model_training/hotel_reviews.csv')

### 🔹 Default Page → Login
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('index'))  # If logged in, go to search
    return redirect(url_for('login'))  # Default page is login

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
    hotel_list = df['hotel_name'].unique().tolist()
    return render_template('index.html', hotel_list=hotel_list)

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate hotel recommendations based on user input and store search in DB."""

    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in
        
    user_id = session['user_id']
    user = UserProfile.query.filter_by(userId=user_id).first()

    first_name = user.firstName if user else "Guest"
    last_name = user.lastName if user else ""
    
    selected_hotel = request.form.get('hotel_name')
    accommodation_type = request.form.get("accommodation_type")
    max_cost = request.form.get("max_cost")

    # Get selected hotel's region
    selected_row = df[df['hotel_name'] == selected_hotel]
    if selected_row.empty:
        print("No hotel found with that name.")
        recommendations = []
    else:
        selected_row = selected_row.iloc[0]
        region = selected_row['region']

        # Step 1: Filter hotels in the same region (excluding the selected hotel)
        filtered_df = df[(df["region"] == region) & (df["hotel_name"] != selected_hotel)]        
                
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

if __name__ == '__main__':
    app.run(debug=True)
