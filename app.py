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

# import database's model
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
                "name": venue.name,
                "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.today(), venue.shows)))
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
        "name": venue.name,
        "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.today(), venue.shows)))
        })
     
  response = {
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

  past_shows = []
  upcoming_shows = []

  past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))
  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), venue.shows))

  tmp = []
  for show in past_shows:
    tmp.append({
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat()
    })
  past_shows = tmp

  tmp = []
  for show in upcoming_shows:
    tmp.append({
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat()
    })
  upcoming_shows = tmp

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = upcoming_shows_count

  # Get genres
  if (venue.genres is not None):
     data['genres'] = venue.genres.split(',')
  else:
     data['genres'] = ""
  print(data)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    venue = Venue()
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.add(venue)
    db.session.commit()
    flash('Venue: {0} created successfully!'.format(venue.name))
  except Exception as err:
    db.session.rollback()
    flash('An error occurred creating the Venue: {0}. Error: {1}'.format(venue.name, err))
    print(sys.exc_info())
  finally:
    db.session.close()
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
      "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.today(), artist.shows)))
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

  past_shows = []
  upcoming_shows = []
  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time >= datetime.now()).all()

  tmp = []
  for show in past_shows:
    tmp.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.isoformat()
    })
  past_shows = tmp

  tmp = []
  for show in upcoming_shows:
    tmp.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.isoformat()
    })
  upcoming_shows = tmp

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)
  data["past_shows"] = past_shows
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = past_shows_count
  data["upcoming_shows_count"] = upcoming_shows_count

  # Get genres
  if (artist.genres is not None):
     data['genres'] = artist.genres.split(',')
  else:
     data['genres'] = ""

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  genres = artist.genres.split(',')
  artist = artist.to_dict()
  artist['website_link'] = artist['website']
  artist['genres'] = genres
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
    artist.genres = ','.join(form.genres.data)
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
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  genres = venue.genres.split(',')
  venue = venue.to_dict()
  venue['website_link'] = venue['website']
  venue['genres'] = genres
  form = VenueForm(formdata=None, data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  try:
    venue.name = form.name.data
    venue.genres = ','.join(form.genres.data)
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Venue: {0} updated successfully'.format(venue.name))
  except Exception as err:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred updating the Venue: {0}. Error: {1}'.format(venue.name, err))
  finally:
    db.session.close()
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
    artist.genres = ','.join(tmp_genres)
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
