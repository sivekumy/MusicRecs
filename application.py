from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
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

s3 = S3Connection(os.environ['SPOTIPY_CLIENT_ID'], os.environ['SPOTIPY_CLIENT_SECRET'])

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'uZY3nyUwMr'

tracklist = []
urls_tracklist = []
indices_tracks = []
fave_tracks = [] #contains urls
fave_genres = []
fave_artists = []
artist_names = []
tracks = ""
danceability_score = 24
energy_score = 24

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

#Home page start button, allows user to begin quiz
class BeginQuiz(FlaskForm):
    submit = SubmitField('Start Quiz')

class Question1(FlaskForm):
    genres = sp.recommendation_genre_seeds()
    global fave_genres
    genre1 = SelectField(u'Genre', choices = genres['genres'], validators = [validators.required()])
    next1 = SubmitField('Next')

class Question2(FlaskForm):
    artist1 = StringField('Artist 1', validators = [validators.required()])
    artist2 = StringField('Artist 2', validators = [validators.required()])
    back2 = SubmitField('Back')
    next2 = SubmitField('Next')

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    
class Question3(FlaskForm):

    track_options = MultiCheckboxField('', choices=[], coerce=int, render_kw={'style': 'height: fit-content; list-style: none;'})
    back3 = SubmitField('Back')
    next3 = SubmitField('Next')
    
    def validate(self):                                                         

        rv = FlaskForm.validate(self)                                           

        if not rv:                                                              
            return False                                                        

        if len(self.track_options.data) > 2 or len(self.track_options.data) < 2:  
            self.track_options.errors.append('Please select 2 items')    
            return False                                                        

        return True


#Home Page
@app.route("/", methods=['POST', 'GET'])
def home():
    form = BeginQuiz()
    if form.validate_on_submit():
        return redirect(url_for('question1'))

    return render_template('home.html',form=form)


@app.route("/quiz/1", methods=['POST', 'GET'])
def question1():
    question1 = Question1()
    global fave_genres
    
    if request.method == 'GET':
        
        #Set default values
        if (fave_genres):
            question1.genre1.data = fave_genres[0]

        return render_template('question1.html', form=question1)

    if request.method == 'POST' and question1.validate_on_submit():
        fave_genres.clear()
        fave_genres.insert(0, question1.genre1.data)

        return redirect(url_for('question2'))

@app.route("/quiz/2", methods=['POST', 'GET'])
def question2():
    question2 = Question2()

    if request.method == 'POST':

        if question2.validate_on_submit():
            global fave_artists, urls_tracklist, artist_names, tracklist
            tracklist.clear()
            urls_tracklist.clear()
            artist_names.clear()
            fave_artists.clear()

            artist_names.append(question2.artist1.data)
            artist_names.append(question2.artist2.data)

            if question2.next2.data:

                results1 = sp.search(q=question2.artist1.data, limit=4)
                results2 = sp.search(q=question2.artist2.data, limit=4)

                fave_artists.append(results1['tracks']['items'][0]['album']['artists'][0]['external_urls']['spotify'])
                fave_artists.append(results2['tracks']['items'][0]['album']['artists'][0]['external_urls']['spotify'])

                tracks1 = results1['tracks']['items']
                tracks2 = results2['tracks']['items']

                index = 1
                for track in tracks1:
                    urls_tracklist.append(track['uri'])
                    tracklist.append((index, track['name'] + " - " + track['artists'][0]['name']))
                    index += 1

                for track in tracks2:
                    urls_tracklist.append(track['uri'])
                    tracklist.append((index, track['name'] + " - " + track['artists'][0]['name']))
                    index += 1

                return redirect(url_for('question3',tracklist=tracklist))

            if question2.back2.data:

                if (artist_names):
                    question2.artist1.data = artist_names[0]
                    question2.artist2.data = artist_names[1]

                return redirect(url_for('question1',tracklist=tracklist))

    if request.method == 'GET':
        if (artist_names):
            question2.artist1.data = artist_names[0]
            question2.artist2.data = artist_names[1]

        return render_template('question2.html',form=question2)

@app.route("/quiz/3", methods=['POST', 'GET'])
def question3():
    question3 = Question3()
    question3.track_options.choices = tracklist

    if request.method == 'POST' and question3.validate_on_submit():

            if question3.next3.data:
                indices_tracks.clear()
                fave_tracks.clear()
                for x in question3.track_options.data:
                    indices_tracks.append(x-1)
                    fave_tracks.append(urls_tracklist[x-1])

                return redirect(url_for('question4'))

            if question3.back3.data:
                return redirect(url_for('question2'))

    else:
        if (indices_tracks):
                question3.track_options.data = [indices_tracks[0] + 1, indices_tracks[1] + 1]

        return render_template('question3.html',form=question3)


@app.route("/quiz/4", methods=['POST', 'GET'])
def question4():
    global energy_score
    
    if request.method == 'POST' and request.form['submit_button'] == 'Next':
        energy = request.form['energy']
        energy_score = energy
        return redirect(url_for('question5'))
    
    if request.method == 'POST' and request.form['submit_button'] == 'Back':
        energy = request.form['energy']
        energy_score = energy
        return redirect(url_for('question3'))

    return render_template('question4.html', value = energy_score)


@app.route("/quiz/5", methods=['POST', 'GET'])
def question5():
    global danceability_score
    
    if request.method == 'POST' and request.form['submit_button'] == 'Submit':
        dance = request.form['dance']
        danceability_score = dance
        return redirect(url_for('results'))
    
    if request.method == 'POST' and request.form['submit_button'] == 'Back':
        dance = request.form['dance']
        danceability_score = dance
        return redirect(url_for('question4'))

    return render_template('question5.html', value = danceability_score)

@app.route('/download', methods = ['POST', 'GET'])
def download(tracks):
    offset = margin = 90

    img = PIL.Image.open('templates/saved_recs.png')
    d1 = ImageDraw.Draw(img)
    content = "Recommendations from MusicRecs" + "\n\n"

    font = ImageFont.truetype("fonts/SpaceMono-Regular.ttf", 10)

    for track in tracks:
        content += track['name'] + "-" + track['artists'][0]['name'] + '\n'

    d1.text((offset, margin), content, fill=(55, 60, 63), font = font)

    img.show()
    img.save("image_text.png")

@app.route("/quiz/results", methods=['POST', 'GET'])
def results():
    global fave_artists, fave_genres, fave_tracks, danceability_score, energy_score, tracks

    if not tracks:
        results = sp.recommendations(seed_artists=fave_artists, seed_genres=fave_genres, seed_tracks=fave_tracks, limit=5, country=None, target_danceability= int(danceability_score)/100, target_energy = int(energy_score)/100)
        tracks = results['tracks']

    if request.method == 'POST':
        
        if request.form['submit_button'] == 'Restart':
            fave_tracks.clear()
            artist_names.clear()
            indices_tracks.clear()
            urls_tracklist.clear()
            tracklist.clear()
            fave_artists.clear()
            fave_genres.clear()
            tracks = ""
            danceability_score = 24
            energy_score = 24
            return redirect(url_for('home'))

        elif request.form['submit_button'] == 'Save':
            flash('Image saved!')
            download(tracks)
            return redirect(url_for('results'))

        elif request.form['submit_button'] == 'search_artist':
            search_artist = request.form['search_artist'] #artist name will be searched in Wikipedia scraper
            return redirect(url_for('about_artist', search_artist=search_artist))

    return render_template('results.html', tracks = tracks)


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
