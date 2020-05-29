#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate

import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Implement Venue, Show and Artist models, and complete all model relationships and properties, as a database migration.

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('venue', lazy=True))

    def __repr__(self):
        return f'<Venue {self.id} name: {self.name}>'

    @property
    def city_state(self):
        return {'city': self.city, 'state': self.state}


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} name: {self.name}>'


class Show(db.Model):

    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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
    # num_shows should be aggregated based on number of upcoming shows per venue.

    data = [v.city_state for v in Venue.query.distinct(
        Venue.city, Venue.state).all()]

    for a in data:
        a['venues'] = [{'id': v.id, 'name': v.name, 'num_upcoming_shows': v.shows}
                       for v in Venue.query.filter_by(city=a['city']).all()]

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    resp = {
        "count": len(data),
        "data": [{
            "id": d.id,
            "name": d.name,
            "num_upcoming_shows": len(d.shows),
        } for d in data]
    }

    return render_template('pages/search_venues.html', results=resp, search_term=request.form.get('search_term', ''))


def venue_past_shows(venue_id):
    return Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue_id).all()


def venue_upcoming_shows(venue_id):
    return Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == venue_id).all()


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    # Get venue
    venue = Venue.query.filter_by(id=venue_id).first()
    # Get all upcoming shows
    upcoming_shows = venue_upcoming_shows(venue_id)
    # Get all past shows
    past_shows = venue_past_shows(venue_id)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [{
            'artist_id': p.artist.id,
            'artist_name': p.artist.name,
            'artist_image_link': p.artist.image_link,
            'start_time': format_datetime(str(p.start_time))
        } for p in past_shows],
        "upcoming_shows": [{
            'artist_id': u.artist.id,
            'artist_name': u.artist.name,
            'artist_image_link': u.artist.image_link,
            'start_time': format_datetime(str(u.start_time))
        } for u in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    try:
        new_venue = Venue(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            address=request.form.get('address'),
            genres=request.form.getlist('genres'),
            phone=request.form.get('phone'),
            facebook_link=request.form.get('facebook_link'),
            image_link=request.form.get('image_link'),
            website=request.form.get('website'),
            seeking_talent=request.form.get('seeking_talent') == 'True',
            seeking_description=request.form.get('seeking_description')
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' +
              new_venue.name + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Delete venue
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    try:
        venue = Venue.query.get(venue_id)
        venue_name = venue.name

        db.session.delete(venue)
        db.session.commit()

        flash('Venue ' + venue_name + ' was deleted')
    except:
        flash('an error occured and Venue ' + venue_name + ' was not deleted')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

    data = []
    artists = Artist.query.all()
    for a in artists:
        data.append({
            "id": a.id,
            "name": a.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')

    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

    response = {
        "count": artists.count(),
        "data": artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id

    artist = Artist.query.filter_by(id=artist_id).first()
    past_shows = Show.query.filter(
        Show.start_time < datetime.now(), Show.artist_id == artist_id).all()

    upcoming_shows = Show.query.filter(
        Show.start_time > datetime.now(), Show.artist_id == artist_id).all()

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows": [{
            'artist_id': p.artist.id,
            'artist_name': p.artist.name,
            'artist_image_link': p.artist.image_link,
            'start_time': format_datetime(str(p.start_time))
        } for p in past_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows": [{
            'artist_id': u.artist.id,
            'artist_name': u.artist.name,
            'artist_image_link': u.artist.image_link,
            'start_time': format_datetime(str(u.start_time))
        } for u in upcoming_shows],
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # populate form with fields from artist with ID <artist_id>
    artist = Artist.query.filter_by(id=artist_id).all()[0]

    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        genres=artist.genres,
        phone=artist.phone,
        facebook_link=artist.facebook_link,
        website=artist.website,
        image_link=artist.image_link,
        # seeking_venue=artist.seeking_venue,
        # seeking_description=artist.seeking_description
    )

    return render_template('forms/edit_artist.html', form=form, artist=artist)

# Edit Artist


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.filter_by(id=artist_id).all()[0]

        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form.get('facebook_link')
        artist.website = request.form.get('website')
        artist.image_link = request.form.get('image_link')
        # artist.seeking_venue = request.form.get('seeking_venue')
        # artist.seeking_description = request.form.get('seeking_description')

        db.session.commit()
        flash('The Artist ' +
              request.form['name'] + ' has been successfully updated!')
    except:
        db.session.rollback()
        flash('An Error has occured and the update unsuccessful')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # populate form with values from venue with ID <venue_id>
    venue = Venue.query.filter_by(id=venue_id).all()[0]

    form = VenueForm(
        name=venue.name,
        city=venue.city,
        state=venue.state,
        address=venue.address,
        phone=venue.phone,
        facebook_link=venue.facebook_link,
        genres=venue.genres,
        website=venue.website,
        image_link=venue.image_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description
    )

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.filter_by(id=venue_id).all()[0]

        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form.get('facebook_link')
        venue.website = request.form.get('website')
        venue.image_link = request.form.get('image_link')
        venue.seeking_talent = request.form.get('seeking_talent') == 'True'
        venue.seeking_description = request.form.get('seeking_description')

        db.session.commit()
        flash('Venue ' + venue.name + ' has been updated')
    except:
        db.session.rollback()
        flash('An error occured while trying to update Venue')
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
    # called upon submitting the new artist listing form
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    try:
        new_artist = Artist(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            genres=request.form.getlist('genres'),
            facebook_link=request.form.get('facebook_link'),
            image_link=request.form.get('image_link'),
            website=request.form.get('website'),

        )
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:

        flash('An error occurred. Artist ' +
              new_artist.name + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.all()
    data = []
    for s in shows:
        data.append({
            "venue_id": s.venue_id,
            "venue_name": s.venue.name,
            "artist_id": s.artist_id,
            "artist_name": s.artist.name,
            "artist_image_link": s.artist.image_link,
            "start_time": format_datetime(str(s.start_time))
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    try:
        show = Show(
            start_time=request.form.get('start_time'),
            venue_id=request.form.get('venue_id'),
            artist_id=request.form.get('artist_id')
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    # on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
