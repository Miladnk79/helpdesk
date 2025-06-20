from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('client', 'Client'), ('operator', 'Operator')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RequestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    file = FileField('File')  # For file upload
    filename = FileField('filename')
    status = StringField('Status')
    priority = SelectField('Priority', choices=[('Normal', 'عادی'), ('Force', 'در اسرع وقت'), ('Urgent', 'اضطراری')], default='Normal')
    submit = SubmitField('Submit Request')

from wtforms import TextAreaField

class ReeditRequestForm(FlaskForm):
    changes = TextAreaField('Changes Needed', validators=[DataRequired()])
    file = FileField('File')  # Optional file upload
    submit = SubmitField('Submit Re-edit')
