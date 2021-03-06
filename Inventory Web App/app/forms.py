from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
from app.models import User, Item

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
    
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    manufacturer = StringField('Manufacturer')
    purchase_date = StringField('Purchase Date')
    purchase_price = StringField('Purchase Price', validators=[DataRequired()])
    warranty = StringField('Warranty', validators=[Optional()])
    insured = StringField('Insured', validators=[Optional()])
    current_value = StringField('Current Value', validators=[Optional()])
    serial = StringField('Serial', validators=[Optional()])
    submit = SubmitField('Save')
    delete = SubmitField('Delete')

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        #self.original_username = original_username

class DeleteForm(FlaskForm):
    reallyDelete = SubmitField('Really Delete')