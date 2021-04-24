from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class CityCountyZipDropDown(FlaskForm):
    countyField = SelectField('County')
    cityField = SelectField('City')
    zipField = SelectField('Zip')
    countyField2 = SelectField('County')
    cityField2 = SelectField('City')
    zipField2 = SelectField('Zip')
    countySubmit = SubmitField('Get Data By County')
    citySubmit = SubmitField('Get Data By City')
    zipSubmit = SubmitField('Get Data By Zip')

    compareSubmit = SubmitField('Compare Two Areas')
    singleSubmit = SubmitField('Select a Single Area')
    clearCompareSubmit = SubmitField('Clear Fields')
    clearSingleSubmit = SubmitField('Clear Fields')


    countyCompareSubmit = SubmitField('Compare these Counties')
    cityCompareSubmit = SubmitField('Compare these Cities')
    zipCompareSubmit = SubmitField('Compare these Zip Codes')


class tableSelectForm(FlaskForm):
    download = SubmitField('Download Table Data')
    tables = SelectField('', choices=[ "Select A Table To Read",
                                        'cement_and_manufacturing',
                                        'waste',
                                        'otis_transportation',
                                        'electricity',
                                        'natural_gas',
                                        'aviation',
                                        'zip_pop'
                                        ])



