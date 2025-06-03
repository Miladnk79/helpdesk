import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import jdatetime

db = SQLAlchemy()
def calculateTime():
    today = datetime.datetime.now()
    todaystr = str(today)
    data = datetime.datetime(int(todaystr[:4]), int(todaystr[5:7]), int(todaystr[8:10]),int(todaystr[11:13]), int(todaystr[14:16]), int(todaystr[17:19]))
    return str(jdatetime.datetime.fromgregorian(date=data))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'client' or 'operator'
    requests = db.relationship('Request', backref='user', lazy=True)  # Relationship to Request


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # New status field
    priority = db.Column(db.String(20), default='Normal')  # New priority field with default Normal
    date_created = db.Column(db.String(50), default=calculateTime())  # Changed to string to store jdatetime string




