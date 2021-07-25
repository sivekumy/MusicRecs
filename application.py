from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators, BooleanField
from wtforms.validators import DataRequired
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

application = Flask(__name__)
Bootstrap(application)
application.config['SECRET_KEY'] = 'uZY3nyUwMr'

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

#Home page start button, allows user to begin quiz
class BeginQuiz(FlaskForm):
    submit = SubmitField('Start Quiz')

#Question 1  
class Quiz(FlaskForm):
    genres = sp.recommendation_genre_seeds()
    genre1 = SelectField(u'Genre 1', choices = genres['genres'], validators = [validators.required()])
    genre2 = SelectField(u'Genre 2', choices = genres['genres'], validators = [validators.required()])
    genre3 = SelectField(u'Genre 3', choices = genres['genres'], validators = [validators.required()])
    genre4 = SelectField(u'Genre 4', choices = genres['genres'], validators = [validators.required()])
    Next = SubmitField('Next')
    
#Question 2
class Question2(FlaskForm):
    artist1 = StringField('Artist 1', validators=[DataRequired()])
    artist2 = StringField('Artist 2', validators=[DataRequired()])
    Back = SubmitField('Back')
    Next = SubmitField('Next')
    
#Question 3
class Question3(FlaskForm):
    checkbox = BooleanField('Agree?', validators=[DataRequired(), ])
    Back = SubmitField('Back')
    Next = SubmitField('Next')

#Home Page
@application.route("/", methods=['POST', 'GET'])
def home():
    form = BeginQuiz()
    if form.validate_on_submit():
        return redirect(url_for('quiz'))

    return render_template('home.html',form=form)

#Quiz
@application.route("/quiz", methods=['POST', 'GET'])
def quiz():
    form = Quiz()
    question2 = Question2()
    question3 = Question3()

    
    if request.method == 'POST' and form.validate():
        print(form.genre1.data)
        print(form.genre2.data)
        print(form.genre3.data)
        print(form.genre4.data)
        return render_template('question2.html',form=question2)
    
    if request.method == 'POST' and question2.validate():
        print(question2.artist1.data)
        print(question2.artist2.data)
        results1 = sp.search(q=question2.artist1.data, limit=4)
        results2 = sp.search(q=question2.artist2.data, limit=4)
        tracks1 = results1['tracks']['items']
        tracks2 = results2['tracks']['items']
        return render_template('question3.html',form=question3, tracks = tracks1)



    return render_template('quiz.html',form=form)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))
