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

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

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
    
#Question 3
class Question3(FlaskForm):
    example = MultiCheckboxField('', choices=[], coerce=int, render_kw={'style': 'height: fit-content; list-style: none;'})

    # example = MultiCheckboxField('', choices = [("1", "Class 1"), ("2","Class 2")], render_kw={'style': 'height: fit-content; list-style: none;'})
    back3 = SubmitField('Back')
    next3 = SubmitField('Next')
    
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
        return redirect(url_for('quiz'))

    return render_template('home.html',form=form)

#Quiz
@application.route("/quiz", methods=['POST', 'GET'])
def quiz():
    question1 = Question1()
    question2 = Question2()
    question3 = Question3()
    
    if request.method == 'POST' and question1.validate_on_submit():
        print(question1.genre1.data)
        print(question1.genre2.data)
        print(question1.genre3.data)
        print(question1.genre4.data)
        return render_template('question2.html',form=question2)
    
    elif request.method == 'POST' and question2.validate_on_submit():
        print(question2.artist1.data)
        print(question2.artist2.data)
        results1 = sp.search(q=question2.artist1.data, limit=4)
        results2 = sp.search(q=question2.artist2.data, limit=4)
        tracks1 = results1['tracks']['items']
        tracks2 = results2['tracks']['items']
        
        index = 0
        tracklist = []
        for track in tracks1:
            tracklist.append((index, track['name'] + " - " + track['artists'][0]['name']))
            index += 1
        
        for track in tracks2:
            tracklist.append((index, track['name'] + " - " + track['artists'][0]['name']))
            index += 1

        question3.example.choices = tracklist

        return render_template('question3.html',form=question3)

    elif request.method == 'POST' and question3.validate_on_submit():
        print("hello!")
        print(question3.example.data)
        return render_template('question4.html')

    if request.method == 'GET':
        return render_template('question1.html',form=question1)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))
