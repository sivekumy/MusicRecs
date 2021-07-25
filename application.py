from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators
from wtforms.validators import DataRequired
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

application = Flask(__name__)
Bootstrap(application)
application.config['SECRET_KEY'] = 'uZY3nyUwMr'

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

q1_response = ""
q2_response = ""
q3_response = ""
q4_response = ""
q5_response = ""


#Home page start button, allows user to begin quiz
class BeginQuiz(FlaskForm):
    submit = SubmitField('Start Quiz')
    
class Quiz(FlaskForm):
    genres = sp.recommendation_genre_seeds()
    genre1 = SelectField(u'Genre 1', choices = genres['genres'], validators = [validators.required()])
    genre2 = SelectField(u'Genre 2', choices = genres['genres'], validators = [validators.required()])
    genre3 = SelectField(u'Genre 3', choices = genres['genres'], validators = [validators.required()])
    genre4 = SelectField(u'Genre 4', choices = genres['genres'], validators = [validators.required()])
    Back = SubmitField('Back')
    Next = SubmitField('Next')

#Home Page
@application.route("/", methods=['POST', 'GET'])
def home():
    form = BeginQuiz()
    if form.validate_on_submit():
        return redirect(url_for('quiz'))

    return render_template('home.html',form=form)

#Quiz - Question 1
@application.route("/quiz", methods=['POST', 'GET'])
def quiz():
    form = Quiz()

    if (q1_response == ""):
        return render_template('quiz.html',form=form)
    elif (q2_response == ""):
        return render_template('question2.html',form=form)
    elif (q3_response == ""):
        return render_template('question3.html',form=form)
    elif (q4_response == ""):
        return render_template('question4.html',form=form)
    elif (q5_response == ""):
        return render_template('question5.html',form=form)

    return render_template('quiz.html',form=form)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))
