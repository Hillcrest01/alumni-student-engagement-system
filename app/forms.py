from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectMultipleField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Sign In')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=10, message="Password must be at least 10 characters")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class CompleteProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Optional()])
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), URL()])
    github_url = StringField('GitHub URL', validators=[Optional(), URL()])
    current_position = StringField('Current Position (Alumni only)', 
                                  validators=[Optional()])
    company = StringField('Company (Alumni only)', validators=[Optional()])
    graduation_year = IntegerField('Graduation Year (Students only)', 
                                  validators=[Optional()])
    interests = SelectMultipleField('Interests', coerce=int,  render_kw={"class": "d-none"})
    submit = SubmitField('Save Profile')

class AdminAddUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('student', 'Student'), 
        ('alumni', 'Alumni'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    submit = SubmitField('Add User')

class AdminEditUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('student', 'Student'), 
        ('alumni', 'Alumni'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    profile_complete = BooleanField('Profile Completed')
    is_verified = BooleanField('Email Verified')
    submit = SubmitField('Update User')