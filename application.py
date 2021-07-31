from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

application = Flask(__name__)
Bootstrap(application)
application.config['SECRET_KEY'] = 'uZY3nyUwMr'
tracklist = []

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

#Home page start button, allows user to begin quiz
class BeginQuiz(FlaskForm):
    submit = SubmitField('Start Quiz')

#Question 1  
class Question1(FlaskForm):
    genres = sp.recommendation_genre_seeds()
    genre1 = SelectField(u'Genre 1', choices = genres['genres'], validators = [validators.required()])
    genre2 = SelectField(u'Genre 2', choices = genres['genres'], validators = [validators.required()])
    genre3 = SelectField(u'Genre 3', choices = genres['genres'], validators = [validators.required()])
    genre4 = SelectField(u'Genre 4', choices = genres['genres'], validators = [validators.required()])
    next1 = SubmitField('Next')
    
#Question 2
class Question2(FlaskForm):
    artist1 = StringField('Artist 1', validators=[DataRequired()])
    artist2 = StringField('Artist 2', validators=[DataRequired()])
    back2 = SubmitField('Back')
    next2 = SubmitField('Next')
    
    
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
    
#Question 3
class Question3(FlaskForm):

    example = MultiCheckboxField('', choices=[], coerce=int, render_kw={'style': 'height: fit-content; list-style: none;'})
    back3 = SubmitField('Back')
    next3 = SubmitField('Next')

    def validate(self):                                                         

        rv = FlaskForm.validate(self)                                           

        if not rv:                                                              
            return False                                                        

        print(self.example.data)                                                

        if len(self.example.data) > 5:                                          
            self.example.errors.append('Please select no more than 5 items')    
            return False                                                        

        return True

#Question 4
# class Question4(FlaskForm):
#     example = MultiCheckboxField('', coerce=int, choices = [("1", "Class 1"), ("2","Class 2")], render_kw={'style': 'height: fit-content; list-style: none;'})
#     back4 = SubmitField('Back')
#     next4 = SubmitField('Next')

#Home Page
@application.route("/", methods=['POST', 'GET'])
def home():
    form = BeginQuiz()
    if form.validate_on_submit():
        return redirect(url_for('question1'))

    return render_template('home.html',form=form)


#Quiz
@application.route("/quiz/1", methods=['POST', 'GET'])
def question1():
    question1 = Question1()

    if request.method == 'POST' and question1.validate_on_submit():
        print(question1.genre1.data)
        print(question1.genre2.data)
        print(question1.genre3.data)
        print(question1.genre4.data)
        return redirect(url_for('question2'))

    return render_template('question1.html', form=question1)


@application.route("/quiz/2", methods=['POST', 'GET'])
def question2():
    question2 = Question2()

    if question2.validate_on_submit():
        print(question2.artist1.data)
        print(question2.artist2.data)
        tracklist.clear()
        results1 = sp.search(q=question2.artist1.data, limit=4)
        results2 = sp.search(q=question2.artist2.data, limit=4)
        tracks1 = results1['tracks']['items']
        tracks2 = results2['tracks']['items']

        index = 1
        for track in tracks1:
            tracklist.append((index, track['name'] + " - " + track['artists'][0]['name']))
            index += 1

        for track in tracks2:
            tracklist.append((index, track['name'] + " - " + track['artists'][0]['name']))
            index += 1

        return redirect(url_for('question3',tracklist=tracklist))

    return render_template('question2.html',form=question2)

@application.route("/quiz/3", methods=['POST', 'GET'])
def question3():
    question3 = Question3()
    print("hello!!!")
    print(tracklist)
    question3.example.choices = tracklist

    if question3.validate_on_submit():
        print("hello!")
        print(question3.example.data)
        return redirect(url_for('question4'))
    
    return render_template('question3.html',form=question3)


@application.route("/quiz/4", methods=['POST', 'GET'])
def question4():
    
    if request.method == 'POST':
        energy = request.form['energy']
        return redirect(url_for('question5'))

    return render_template('question4.html')

@application.route("/quiz/5", methods=['POST', 'GET'])
def question5():
    
    if request.method == 'POST':
        dance = request.form['dance']
        return redirect(url_for('results'))

    return render_template('question5.html')

@application.route("/quiz/results", methods=['POST', 'GET'])
def results():
    artists = ["https://open.spotify.com/artist/12Chz98pHFMPJEknJQMWvI"]
    genres = ["k-pop"]
    tracks = ["https://open.spotify.com/track/4VqPOruhp5EdPBeR92t6lQ"]
    results = sp.recommendations(seed_artists=artists, seed_genres=genres, seed_tracks=tracks, limit=5, country=None)
    tracks = results['tracks']

    if request.method == 'POST':
        
        if request.form['submit_button'] == 'Restart':
            return redirect(url_for('home'))

        elif request.form['submit_button'] == 'Save':
            return redirect(url_for('home'))

        elif request.form['submit_button'] == 'search_artist':
            search_artist = request.form['search_artist'] #artist name will be searched in Wikipedia scraper
            print(search_artist)
            return redirect(url_for('aboutartist', search_artist=search_artist))
            #send artist name + data from Wikipedia scraper (to be implemented)
            # return render_template('aboutartist.html', artist=search_artist)

    return render_template('results.html', tracks = tracks)

@application.route("/quiz/results/aboutartist", methods=['POST', 'GET'])
def aboutartist():
    
    if request.method == 'POST' and request.form['submit_button'] == 'Back':
        return redirect(url_for('results'))
    
    search_artist = request.args['search_artist']
    return render_template('aboutartist.html', artist=search_artist)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))
