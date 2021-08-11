from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash, session, send_file
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired

#Home page start button, allows user to begin quiz
class BeginQuiz(FlaskForm):
    submit = SubmitField('Start Quiz')

class Question1(FlaskForm):
    genre1 = SelectField(u'Genre', choices = "", validators = [validators.required()])
    next1 = SubmitField('Next')

class Question2(FlaskForm):
    artist1 = StringField('Artist 1')
    artist2 = StringField('Artist 2')
    back2 = SubmitField('Back')
    next2 = SubmitField('Next')

    def validate(self):                                                         

        rv = FlaskForm.validate(self)                                           

        if not rv:                                                              
            return False
        
        if len(self.artist1.data) == 0 and len(self.artist2.data) == 0 and self.next2.data:
            self.artist1.errors.append('Please add an artists')
            self.artist2.errors.append('Please add an artists')    
            return False

        elif len(self.artist1.data) == 0 and self.next2.data:
            self.artist1.errors.append('Please add an artist')    
            return False
        
        elif len(self.artist2.data) == 0 and self.next2.data:  
            self.artist1.errors.append('Please add an artist')    
            return False

        return True

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

        if len(self.track_options.data) != 2 and self.next3.data:  
            self.track_options.errors.append('Please select 2 items')    
            return False                                                        

        return True

