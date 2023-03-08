#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
import collections.abc
collections.Callable = collections.abc.Callable
import sys
from operator import itemgetter # for sorting lists of tuples

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

  def __repr__(self):
    return f'<Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Data to save all venues
  data = []
  # Set of all the {cities, states) combinations uniquely
  location_list = set()

  venues = Venue.query.all()
  for venue in venues:
    # Add turple of (city, state) to the set
    location_list.add((venue.city, venue.state))
  
  # Turn the set into an ordered list
  location_list = list(location_list)
  # Sorts on second column first (state), then by city.
  location_list.sort(key=itemgetter(1,0))

  for location in location_list:
    venue_list = []
    for venue in venues:
        if (venue.city == location[0]) and (venue.state == location[1]):
            venue_list.append({
                "id": venue.id,
                "name": venue.name
            })

    # Append the data dictionary
    data.append({
        "city": location[0],
        "state": location[1],
        "venues": venue_list
    })

  print(data)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '').strip()
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  venue_list = []
  for venue in results:
     venue_list.append({
        "id": venue.id,
        "name": venue.name
        })
     
  response={
    "count": len(results),
    "data": venue_list
  }
  print(response)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# shows the venue page with the given venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  data = venue.to_dict()

  #TODO: get genres
#  if (venue['genres'] is not None):
#     data['genres'] = venue['genres'].split(',')
#  else:
#     data['genres'] = ""
  #TODO: get past_shows_count, upcoming_shows_count then append to the data
  #TODO: get lists: past_shows[],  upcoming_shows[] then append to the data
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
      venue = Venue()
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      tmp_genres = request.form.getlist('genres')
      venue.genres = ','.join(tmp_genres)
      venue.facebook_link = request.form['facebook_link']
      db.session.add(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
    # on unsuccessful db insert, flash an error.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  print('/venues/<venue_id>/delete')
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash(f'An error occurred deleting venue {venue_name}.')
    abort(500)
  else:
    flash(f'Successfully removed venue {venue_name}.')
    return jsonify({'success': True})

  # TODO: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '').strip()
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  artist_list = []
  for artist in results:
    artist_list.append({
      "id": artist.id,
      "name": artist.name,
      #TODO: "num_upcoming_shows": 
    })

  response = {
    "count": len(artist_list),
    "data": artist_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  data = artist.to_dict()

  #TODO: get genres
#  if (venue['genres'] is not None):
#     data['genres'] = venue['genres'].split(',')
#  else:
#     data['genres'] = ""
  #TODO: get past_shows_count, upcoming_shows_count then append to the data
  #TODO: get lists: past_shows[],  upcoming_shows[] then append to the data

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id).to_dict()
  artist['website_link'] = artist['website']
  form = ArtistForm(formdata=None, data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  error = False
  is_seeking_venue = False

  try:
    artist.name = request.form['name'].strip()
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    #TODO: process genres combobox
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website_link']
    if (request.form['seeking_venue'] == 'y'):
      is_seeking_venue = True
    else:
       is_seeking_venue = False
    artist.seeking_venue = is_seeking_venue
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db update, flash an error.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
    # on successful db update, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id).to_dict()
  venue['website_link'] = venue['website']
  #TODO: get genres list and push to venue
  form = VenueForm(formdata=None, data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  error = False
  is_seeking_talent = False

  try:
    venue.name = request.form['name'].strip()
    #TODO: process genres combobox
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    if (form.seeking_talent.data):
      is_seeking_talent = True
    else:
       is_seeking_talent = False
    venue.seeking_talent = is_seeking_talent
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db update, flash an error.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  else:
    # on successful db update, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  is_seeking_venue = False
  try:
    artist = Artist()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    artist.genres = ', '.join(tmp_genres)
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website_link']
    if (request.form['seeking_venue'] == 'y'):
      is_seeking_venue = True
    else:
      is_seeking_venue = False
    artist.seeking_venue = is_seeking_venue
    artist.seeking_description = request.form['seeking_description']

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash an error.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  list = db.session.query(Show, Venue, Artist).join(Venue).join(Artist).filter(Show.start_time > datetime.now()).order_by('start_time').all()
  data = []

  for item in list:
    data.append({
      'venue_id': item.Venue.id,
      'venue_name': item.Venue.name,
      'artist_id': item.Artist.id,
      'artist_name': item.Artist.name,
      'artist_image_link': item.Artist.image_link,
      'start_time': item.Show.start_time.strftime('%Y-%m-%d %H:%I')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False

  try:
      show = Show()
      show.venue_id = request.form['venue_id']
      show.artist_id = request.form['artist_id']
      show.start_time = request.form['start_time']
      db.session.add(show)
      db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show could not be listed.')
  else:
      flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
