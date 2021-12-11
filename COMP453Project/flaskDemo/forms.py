from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import User, Gene, Protein, Paper, Authors, Ligand, Organism, ReferencedIn, BiologicalProcess, GOAnnotations, FoundIn
from wtforms.fields.html5 import DateField
import sys

#Get choices for Protein ID, GO term ID, and Qualifier
proteins = Protein.query.with_entities(Protein.UniProtEntryID, Protein.ScientificName).distinct()
results=list()
for row in proteins:
    rowDict=row._asdict()
    results.append(rowDict)
proteinChoices = [(row['UniProtEntryID'],row['ScientificName']) for row in results]

goterms = BiologicalProcess.query.with_entities(BiologicalProcess.GOTermID, BiologicalProcess.Name).distinct()
results=list()
for row in goterms:
    rowDict=row._asdict()
    results.append(rowDict)
gotermChoices = [(row['GOTermID'],row['Name']) for row in results]



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class GOAnnotationUpdateForm(FlaskForm):

    def __init__(self, startingUniProtEntryID, startingGOTermID):
        self.startingUniProtEntryID = startingUniProtEntryID
        self.startingGOTermID = startingGOTermID
        super(GOAnnotationUpdateForm, self).__init__()

    UniProtEntryID = SelectField("Protein", choices=proteinChoices)
    GOTermID = SelectField("GO Term", choices=gotermChoices)
    Qualifier = StringField("Qualifier", validators=[DataRequired()])

    submit = SubmitField('Update this GO Annotation')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        result = True
        protein = GOAnnotations.query.filter_by(UniProtEntryID=self.UniProtEntryID.data, GOTermID=self.GOTermID.data).first()
        if protein and (str(protein.UniProtEntryID)!= str(self.startingUniProtEntryID) or str(protein.GOTermID)!=str(self.startingGOTermID)):
            self.UniProtEntryID.errors.append('That combination is taken. Please choose a different one.')
            self.GOTermID.errors.append('That combination is taken. Please choose a different one.')
            return False
        return result


class AssignmentForm(GOAnnotationUpdateForm):

    submit = SubmitField('Add this GO Annotation')

    def __init__(self):
        super(AssignmentForm, self).__init__('','')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        result = True
        protein = GOAnnotations.query.filter_by(UniProtEntryID=self.UniProtEntryID.data, GOTermID=self.GOTermID.data).first()
        if protein:
            self.UniProtEntryID.errors.append('That combination is taken. Please choose a different one.')
            self.GOTermID.errors.append('That combination is taken. Please choose a different one.')
            return False
        return result
