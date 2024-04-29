### This example for performing many to many relationship on the same class(table)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Association table for the follower-followee relationship
follower_followee = db.Table('follower_followee',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('followee_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    
    # Define the follower-followee relationship
    followers = db.relationship('Users',
                                secondary=follower_followee,
                                primaryjoin=(follower_followee.c.followee_id == id),
                                secondaryjoin=(follower_followee.c.follower_id == id),
                                backref=db.backref('following', lazy='dynamic'),
                                lazy='dynamic')

# Example usage
user1 = Users(username='user1')
user2 = Users(username='user2')
user3 = Users(username='user3')

# user1 follows user2 and user3
user1.following.append(user2)
user1.following.append(user3)

# user2 follows user3
user2.following.append(user3)

# Commit changes to the database
db.session.add_all([user1, user2, user3])
db.session.commit()



########################### To reach the followers

# Assuming user3 is already created and exists in the database
user3 = User.query.filter_by(username='user3').first()

# Get followers of user3
followers_of_user3 = user3.followers.all()

# Print the usernames of followers
for follower in followers_of_user3:
    print(follower.username)
