from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class GameForm(FlaskForm):
    slug = StringField(
        "Slug",
        validators=[
            DataRequired(),
            Length(max=50),
            Regexp(
                r"^[a-z0-9-]+$",
                message="Use lowercase letters, numbers, and hyphens only.",
            ),
        ],
    )

    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(),
            Length(max=500),
        ],
    )

    thumbnail = StringField(
        "Thumbnail URL",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")
