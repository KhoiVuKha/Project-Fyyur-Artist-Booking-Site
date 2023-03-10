from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  genres = db.Column(db.String(120))
  address = db.Column(db.String(120))
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  website = db.Column(db.String(200))
  facebook_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  shows = db.relationship('Show', backref='venue', lazy=True)

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'address': self.address,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'website': self.website,
      'facebook_link': self.facebook_link,
      'seeking_talent': self.seeking_talent,
      'seeking_description': self.seeking_description,
      'image_link': self.image_link
    }

  def __repr__(self):
    return f'<<Venue {self.id} {self.name}>'

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  genres = db.Column(db.String(120))
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  website = db.Column(db.String(200))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  shows = db.relationship('Show', backref='artist', lazy=True)

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'website': self.website,
      'facebook_link': self.facebook_link,
      'seeking_venue': self.seeking_venue,
      'seeking_description': self.seeking_description,
      'image_link': self.image_link
    }
      
  def __repr__(self):
    return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

  def __repr__(self):
    return f'<Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'
