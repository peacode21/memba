from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,Length
from flask_wtf.file import FileField,FileRequired,FileAllowed

class ContactForm(FlaskForm):
    screenshot =  FileField("upload screenshot", validators=[FileRequired(),FileAllowed(['png','jpg','jpeg','webp'],"Ensure you upload the right extension!")])
    email = StringField("Your Email: ",validators=[Email('Your Email must be a valid email'),DataRequired(message="You cannot submit and empty field")])
    message = TextAreaField("Message:", validators=[DataRequired(),Length(min=10)])
    submit = SubmitField("Send Message:")
