from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(164), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    items = db.relationship('Item', backref='owner', lazy='dynamic')
    about_me = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}?f=y'.format(digest,size)




class Item(db.Model):
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    manufacturer = db.Column(db.String(64))
    purchase_date = db.Column(db.String(20))
    purchase_price = db.Column(db.String(12))
    warranty = db.Column(db.String(20))
    insured = db.Column(db.String(20))
    current_value = db.Column(db.String(12))
    serial = db.Column(db.String(30))
    date_added = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Item {}, from {}>'.format(self.name, self.user_id)

      

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
