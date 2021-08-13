from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash, session, send_file
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request
import json
import PIL.Image
from PIL import ImageFont
from PIL import ImageDraw
from urllib.request import urlopen
from io import BytesIO
import requests
import os
from boto.s3.connection import S3Connection
from forms import *

s3 = S3Connection(os.environ['SPOTIPY_CLIENT_ID'], os.environ['SPOTIPY_CLIENT_SECRET'])

app = Flask(__name__)
Bootstrap(app)
# app.config['SECRET_KEY'] = 'uZY3nyUwMr'
app.secret_key = 'uZY3nyUwMr'

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)


@app.route("/", methods=['POST', 'GET'])
def home():
    form = BeginQuiz()
    if form.validate_on_submit():
        session["tracklist"] = []
        session["urls_tracklist"] = []
        session["indices_tracks"] = []
        session["fave_tracks"] = []
        session["fave_genres"] = []
        session["fave_artists"] = []
        session["artist_names"] = []
        session["tracks"] = ""
        session["danceability_score"] = 50
        session["energy_score"] = 50

        return redirect(url_for('question1'))

    return render_template('home.html',form=form)


@app.route("/quiz/1", methods=['POST', 'GET'])
def question1():
    question1 = Question1()
    genres = sp.recommendation_genre_seeds()
    question1.genre1.choices = genres['genres']

    if request.method == 'GET':

        # Set default values
        if (session.get('fave_genres')):
            question1.genre1.data = session['fave_genres'][0]

        return render_template('question1.html', form=question1)

    if request.method == 'POST' and question1.validate_on_submit():
        session['fave_genres'].clear()
        session['fave_genres'].insert(0, question1.genre1.data)
        session.modified = True

        return redirect(url_for('question2'))
    
    return render_template('question1.html', form=question1)


@app.route("/quiz/2", methods=['POST', 'GET'])
def question2():
    question2 = Question2()

    if request.method == 'POST' and question2.validate_on_submit():
        session["tracklist"].clear()
        session["urls_tracklist"].clear()
        session["artist_names"].clear()
        session["fave_artists"].clear()

        session["artist_names"].append(question2.artist1.data)
        session["artist_names"].append(question2.artist2.data)
        session.modified = True

        if question2.next2.data:

            results1 = sp.search(q=question2.artist1.data, limit=4)
            results2 = sp.search(q=question2.artist2.data, limit=4)

            session["fave_artists"].append(results1['tracks']['items'][0]['album']['artists'][0]['external_urls']['spotify'])
            session["fave_artists"].append(results2['tracks']['items'][0]['album']['artists'][0]['external_urls']['spotify'])

            tracks1 = results1['tracks']['items']
            tracks2 = results2['tracks']['items']

            index = 1
            for track in tracks1:
                session["urls_tracklist"] .append(track['uri'])
                session["tracklist"].append((index, track['name'] + " - " + track['artists'][0]['name']))
                index += 1

            for track in tracks2:
                session["urls_tracklist"] .append(track['uri'])
                session["tracklist"].append((index, track['name'] + " - " + track['artists'][0]['name']))
                index += 1

            session.modified = True
            return redirect(url_for('question3',tracklist=session["tracklist"]))

        if question2.back2.data:

            if (session["artist_names"]):
                question2.artist1.data = session["artist_names"][0]
                question2.artist2.data = session["artist_names"][1]

            return redirect(url_for('question1', tracklist=session["tracklist"]))

    else:
        if (session["artist_names"]):
            question2.artist1.data = session["artist_names"][0]
            question2.artist2.data = session["artist_names"][1]

        return render_template('question2.html',form=question2)

@app.route("/quiz/3", methods=['POST', 'GET'])
def question3():
    question3 = Question3()
    question3.track_options.choices = session["tracklist"]

    if request.method == 'POST' and question3.validate_on_submit():

            if question3.next3.data:
                session["indices_tracks"].clear()
                session["fave_tracks"].clear()
                for x in question3.track_options.data:
                    session["indices_tracks"].append(x-1)
                    session["fave_tracks"].append(session["urls_tracklist"][x-1])

                session.modified = True
                return redirect(url_for('question4'))

            if question3.back3.data:
                return redirect(url_for('question2'))

    else:
        if (session["indices_tracks"]):
                question3.track_options.data = [session["indices_tracks"][0] + 1, session["indices_tracks"][1] + 1]

        return render_template('question3.html',form=question3)


@app.route("/quiz/4", methods=['POST', 'GET'])
def question4():
    
    if request.method == 'POST' and request.form['submit_button'] == 'Next':
        energy = request.form['energy']
        session["energy_score"] = energy
        session.modified = True
        return redirect(url_for('question5'))
    
    if request.method == 'POST' and request.form['submit_button'] == 'Back':
        energy = request.form['energy']
        session["energy_score"] = energy
        session.modified = True
        return redirect(url_for('question3'))

    return render_template('question4.html', value = session["energy_score"])


@app.route("/quiz/5", methods=['POST', 'GET'])
def question5():
    
    if request.method == 'POST' and request.form['submit_button'] == 'Submit':
        dance = request.form['dance']
        session["danceability_score"] = dance
        session.modified = True
        return redirect(url_for('results'))
    
    if request.method == 'POST' and request.form['submit_button'] == 'Back':
        dance = request.form['dance']
        session["danceability_score"] = dance
        session.modified = True
        return redirect(url_for('question4'))

    return render_template('question5.html', value = session["danceability_score"])

@app.route('/download')
def download():
    offset = margin = 90

    img = PIL.Image.open('templates/saved_recs.png')
    d1 = ImageDraw.Draw(img)
    content = "Recommendations from MusicRecs" + "\n\n"

    font = ImageFont.truetype("fonts/NotoSerif-Regular.ttf", 10)

    for track in session["tracks"]:
        content += track['name'] + "-" + track['artists'][0]['name'] + '\n'

    d1.text((offset, margin), content, fill=(55, 60, 63), font = font)

    img.show()
    img.save("recommendations_musicrecs.png")
    return send_file("recommendations_musicrecs.png", as_attachment=True)

@app.route("/quiz/results", methods=['POST', 'GET'])
def results():
    
    if not session["tracks"]:
        results = sp.recommendations(seed_artists=session["fave_tracks"], seed_genres=session["fave_genres"], seed_tracks=session["fave_tracks"], limit=5, country=None, target_danceability= int(session["danceability_score"])/100, target_energy = int(session["energy_score"])/100)
        session["tracks"] = results['tracks']
        session.modified = True

    if request.method == 'POST':
        
        if request.form['submit_button'] == 'Restart':
            session.pop("fave_tracks", None)
            session.pop("artist_names", None)
            session.pop("IndentationError", None)
            session.pop("urls_tracklist", None)
            session.pop("tracklist", None)
            session.pop("fave_artists", None)
            session.pop("fave genres", None)
            session.pop("tracks", None)
            session.pop("danceability_score", None)
            session.pop("energy_score", None)
            return redirect(url_for('home'))

        elif request.form['submit_button'] == 'Save':
            flash('Image saved!')
            return redirect(url_for('download'))

        elif request.form['submit_button'] == 'search_artist':
            search_artist = request.form['search_artist'] #artist name will be searched in Wikipedia scraper
            return redirect(url_for('about_artist', search_artist=search_artist))

    return render_template('results.html', tracks = session["tracks"])


@app.route("/quiz/results/aboutartist", methods=['POST', 'GET'])
def about_artist():

    if request.method == 'POST' and request.form['submit_button'] == 'Back':
        return redirect(url_for('results'))

    search_artist = request.args['search_artist']

    artist_info = wikipedia_scraper(search_artist)

    return render_template('aboutartist.html', artist=search_artist, about_artist = artist_info)


def wikipedia_scraper(artist_name):

    try:
        artist_link = "https://wiki-scrapper.herokuapp.com/?q="  + urllib.parse.quote(artist_name)
        contents = urllib.request.urlopen(artist_link).read()
        contents_dict = json.loads(contents)

        artist_info = ""
        for content in contents_dict['message']:
            artist_info += content

    except Exception:
        artist_info = "No information available :("

    return artist_info


#route to test image scraper
@app.route("/test", methods=['POST', 'GET'])
def test():
    search_term = "music"
    images = "https://scraping-image-app.herokuapp.com/" + search_term
    contents = urllib.request.urlopen(images).read()
    contents_dict = json.loads(contents)
    image = contents_dict['message'][1]
    return render_template('test.html', image = image)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
