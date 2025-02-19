from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class UserAccount(db.Model):
    userId = db.Column(db.String(36), primary_key=True, unique=True, nullable=False, default=str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    profileId = db.Column(db.String(36), primary_key=True, unique=True, nullable=False, default=str(uuid.uuid4()))
    userId = db.Column(db.String(36), db.ForeignKey('user_account.userId'), nullable=False)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.String(20), unique=True)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Room(db.Model):
    roomId = db.Column(db.String(36), primary_key=True, unique=True, nullable=False, default=str(uuid.uuid4()))
    ownerId = db.Column(db.String(36), db.ForeignKey('user_account.userId'), nullable=False)
    hotel_name = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    accommodation_type = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
