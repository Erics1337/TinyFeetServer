from flask import Blueprint,render_template,redirect,url_for,request, jsonify, flash
from server import db
from server.emissions.forms import CityCountyZipDropDown, tableSelectForm
from server.models import Cement_and_manufacturing, Electricity, Natural_gas, Otis_transportation, Waste, Aviation, Zip_pop, Zip_data
from sqlalchemy import distinct, inspect
import collections
# import flask_excel as excel

emissions_blueprint = Blueprint('emissions', __name__, template_folder='../templates')

# ----------------------------- Helper Functions ----------------------------- #

# This function replaces Null or 'None' values with 0 to play nice with google charts
def coalesce(*arg): return next((a for a in arg if a is not None), 0)

# This function converts query result to dict
def object_as_dict(obj):
    return {c.key: coalesce(getattr(obj, c.key))
        for c in inspect(obj).mapper.column_attrs}


# ------------------------------ Read page route ----------------------------- #

@emissions_blueprint.route('/read', methods=['GET', 'POST'])
def read():
    form = tableSelectForm()

    if request.method == 'POST':
        tableName = form.tables.data
        print(tableName)
        if tableName == "Select A Table To Read":
            flash("Please Select A Table To Read")
        # Redirect with POST
        # elif form.download.data:
        #     return redirect(f'read/{tableName}', code=307)
        else:
            tableName = form.tables.data
            return redirect(f'/emissions/read/{tableName}')

    form.tables.data = "Select A Table to Read"
    return render_template('/mainPages/read.html', form=form)


@emissions_blueprint.route('/read/<tableName>', methods=['GET', 'POST'])
def readTable(tableName):
    form = tableSelectForm()

    if tableName == "waste":
        columnNames = Waste.__table__.columns.keys()
        query = Waste.query.all()
    elif tableName == "cement_and_manufacturing":
        columnNames = Cement_and_manufacturing.__table__.columns.keys()
        query = Cement_and_manufacturing.query.all()
    elif tableName == "electricity":
        columnNames = Electricity.__table__.columns.keys()
        query = Electricity.query.all()
    elif tableName == "natural_gas":
        columnNames = Natural_gas.__table__.columns.keys()
        query = Natural_gas.query.all()
    elif tableName == "zip_pop":
        columnNames = Zip_pop.__table__.columns.keys()
        query = Zip_pop.query.all()
    elif tableName == "aviation":
        columnNames = Aviation.__table__.columns.keys()
        query = Aviation.query.all()
    else:
        flash("Table Name Not Recognized")
        return redirect(url_for('emissions.read'))

    tableData = []
    for row in query:
        d = object_as_dict(row)
        tableData.append(d.values())

    # Convert data to excel and download
    # if request.method == 'POST':
    #     tableData.insert(0, columnNames)
    #     print(tableData)
    #     # return excel.make_response_from_array([[1, 2], [3, 4]], "csv", file_name="export_data")
    #     # return excel.make_response_from_array(tableData, "csv", file_name=f"{tableName}")


    form.tables.data = tableName
    return render_template('/mainPages/read.html', form=form, tableName=tableName, columnNames=columnNames, tableData=tableData)


# ------- Select page GET route and POST form handling to load table chart ------- #

@emissions_blueprint.route('/select', methods=['GET', 'POST'])
def select():
    form = CityCountyZipDropDown()
    county = form.county.data
    city = form.city.data
    zip = form.zip.data
    
    if request.method == 'POST':
        if form.countySubmit.data:
            if county == "Select Option":
                flash("Please Select a County Option")
            else:
                return redirect(f'select/county/{county}')
        elif form.citySubmit.data:
            if city == "Select Option":
                flash("Please Select a City Option")
            else:
                return redirect(f'select/city/{city}')
        elif form.zipSubmit.data:
            if zip == "Select Option":
                flash("Please Select a Zip Option")
            else:
                return redirect(f'select/zip/{zip}')
        else:
            zip = request.form.get('zipInput')
            if (db.session.query(Zip_data).filter_by(zip=zip)).count() == 0:
                flash("Please Enter a Valid Zip Code")
            else:
                return redirect(f'select/zip/{zip}')
        return redirect(f'/emissions/select')
    
    if request.method == 'GET':
        form.county.choices = ["Select Option"] + [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.city.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).distinct(Zip_pop.city).order_by(Zip_pop.city)]
        form.zip.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).distinct(Zip_pop.zip).order_by(Zip_pop.zip)]

    return render_template('mainPages/select.html', form=form)


# -------------------------- Generate Chart From Zip ------------------------- #

@emissions_blueprint.route('/select/zip/<zip>')
def chartZip(zip):
    form = CityCountyZipDropDown()
    query = db.session.query(Zip_data).filter_by(zip=zip)
    
    for row in query:
        data = (object_as_dict(row))

    # Remove zip and pop non-numerical data points
    data.pop('zip')
    city = data.pop('city')
    county = data.pop('county')
    # Must remove aviation data point for now because google charts does not like decimal data type
    aviation = data.pop('aviation')
    # Convert to list of lists and add labels
    zipData = list(map(list, data.items()))
    zipData.insert(0, ['Sector', 'Emissions'])

    form.county.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
    form.city.choices = [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county).distinct(Zip_pop.county).order_by(Zip_pop.city)]
    form.zip.choices = [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city).all()]
    form.zip.data = zip
    form.city.data = city
    form.county.data = county

    return render_template('mainPages/select.html', form=form, zipData=zipData, area=zip)


# -------------------------- Generate Chart From City ------------------------- #

@emissions_blueprint.route('/select/city/<city>')
def chartCity(city):
    form = CityCountyZipDropDown()

    query = db.session.query(Zip_data).filter_by(city=city)
    if query.count() == 0:
        flash("That City Does Not Exist!")
        return render_template('mainPages/select.html', form=form,)

    else:
        rows = []
        for row in query:
            d = object_as_dict(row)
            d.pop('zip')
            city = d.pop('city')
            county = d.pop('county')
            # Must remove aviation data point for now because google charts does not like decimal data type
            d.pop('aviation')
            rows.append(d)
        
        # sum the values with same keys 
        counter = collections.Counter() 
        for d in rows:  
            counter.update(d)
        data = dict(counter) 

        # Convert to list of lists and add labels
        zipData = list(map(list, data.items()))
        zipData.insert(0, ['Sector', 'Emissions'])

        form.county.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.city.choices = [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county).distinct(Zip_pop.county).order_by(Zip_pop.city)]
        form.zip.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city).all()]
        form.zip.data = ["Select Option"]
        form.city.data = city
        form.county.data = county

        return render_template('mainPages/select.html', form=form, zipData=zipData, area=city)


# -------------------------- Generate Chart From County ------------------------- #

@emissions_blueprint.route('/select/county/<county>')
def chartCounty(county):
    form = CityCountyZipDropDown()
    query = db.session.query(Zip_data).filter_by(county=county)

    if query.count() == 0:
        flash("That Zip Code Does Not Exist!")
        return render_template('mainPages/select.html', form=form,)

    else:
        rows = []
        for row in query:
            d = object_as_dict(row)
            d.pop('zip')
            city = d.pop('city')
            county = d.pop('county')
            # Must remove aviation data point for now because google charts does not like decimal data type
            d.pop('aviation')
            rows.append(d)
        
        # sum the values with same keys 
        counter = collections.Counter() 
        for d in rows:  
            counter.update(d)
        data = dict(counter) 

        # Convert to list of lists and add labels
        zipData = list(map(list, data.items()))
        zipData.insert(0, ['Sector', 'Emissions'])

        form.county.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.city.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county).distinct(Zip_pop.county).order_by(Zip_pop.city)]
        form.zip.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city).all()]
        form.zip.data = ["Select Option"]
        form.city.data = ["Select Option"]
        form.county.data = county

        return render_template('mainPages/select.html', form=form, zipData=zipData, area=county)


# --------------------- Dynamic Dropdown Option Changing for Select page--------------------- #

@emissions_blueprint.route('/<county>')
def city(county):
    rows = db.session.query(Zip_pop.city).filter_by(county=county).distinct(Zip_pop.county).order_by(Zip_pop.city)
    cityArray = []
    for row in rows:
        cityObj = {}
        cityObj['option'] = row.city
        cityArray.append(cityObj)
    return jsonify({'cities' : cityArray})


@emissions_blueprint.route('/<county>/<city>')
def zip(county, city):
    rows = db.session.query(Zip_pop.zip).filter_by(city=city).all()
    zipArray = []
    for row in rows:
        zipObj = {}
        zipObj['option'] = row.zip
        zipArray.append(zipObj)
    return jsonify({'zip_codes' : zipArray})


@emissions_blueprint.route('/map')
def googleMap():
    return render_template('mainPages/map.html')
