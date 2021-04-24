from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField, RadioField, TextField


class RecForm(FlaskForm):
    allSol = BooleanField('All Recommendations')
    equity = BooleanField('Equity')
    econSus = BooleanField('Economic Sustainability')
    envQuality = BooleanField('Local Environmental Quality')
    healthSafety = BooleanField('Enhancing Public Health and Safety')
    resilience = BooleanField('Building Community Resilience')

    allSec = BooleanField('All Sectors')
    transportation = BooleanField('Vechicles and Transportation')
    energy = BooleanField('Energy')
    waste = BooleanField('Waste and Land Management')

    areaRadio = RadioField('Search By:', choices=[
        ('zip', 'Zip Code'), ('city', 'City Name'), ('county', 'County Name')], default=2)
    areaField = TextField('Zip Code, City, or County')

    submit = SubmitField()
