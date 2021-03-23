from flask import Blueprint,render_template,redirect,url_for,request, jsonify, flash
from server import db
from sqlalchemy import distinct, inspect
from server.emissions.forms import CityCountyZipDropDown, tableSelectForm
from server.models import Cement_and_manufacturing, Electricity, Natural_gas, Otis_transportation, Waste, Aviation, Zip_pop, Zip_data, Zip_Data_Schema, County_data, County_Data_Schema
# from server.models import *
import collections
from flask_marshmallow import Marshmallow

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
    elif tableName == "otis_transportation":
        columnNames = Otis_transportation.__table__.columns.keys()
        query = Otis_transportation.query.all()
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


# -------------------------------- Google Maps ------------------------------- #

# For some reason, for google map to load it cannot be in top level directory
@emissions_blueprint.route('/map')
def googleMap():
    return render_template('mainPages/map.html')


@emissions_blueprint.route('/getZipData')
def getZipData():
    ghgData = Zip_data.query.all()
    output = Zip_Data_Schema(many=True).dump(ghgData)
    return jsonify(output)


@emissions_blueprint.route('/getCountyData')
def getCountyData():
    ghgData = County_data.query.all()
    output = County_Data_Schema(many=True).dump(ghgData)
    return jsonify(output)


# --------------------- Dynamic Dropdown Option Changing for chart page--------------------- #

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




# --------------------------------- Route to handle chart page home and redict form input for Compare ------------------------------------- #

@emissions_blueprint.route('/chart', methods=['GET', 'POST'])
def chart():
    form = CityCountyZipDropDown()
    county = form.countyField.data
    city = form.cityField.data
    zip = form.zipField.data
    county2 = form.countyField2.data
    city2 = form.cityField2.data
    zip2 = form.zipField2.data
    
    # Single select case
    if request.method == 'POST':
        if form.singleSubmit.data:
            pass
        elif form.compareSubmit.data:

            form.countyField.choices = ["Select Option"] + [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
            form.cityField.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).distinct(Zip_pop.city).order_by(Zip_pop.city)]
            form.zipField.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).distinct(Zip_pop.zip).order_by(Zip_pop.zip)]

            form.countyField2.choices = ["Select Option"] + [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
            form.cityField2.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).distinct(Zip_pop.city).order_by(Zip_pop.city)]
            form.zipField2.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).distinct(Zip_pop.zip).order_by(Zip_pop.zip)]

            return render_template('mainPages/chart.html', form=form, compare=True)

        elif form.countySubmit.data:
            if county == "Select Option":
                flash("Please Select a County Option")
            else:
                return redirect(f'chart/county/{county}')
        elif form.citySubmit.data:
            if city == "Select Option":
                flash("Please Select a City Option")
            else:
                return redirect(f'chart/city/{city}')
        elif form.zipSubmit.data:
            if zip == "Select Option":
                flash("Please Select a Zip Option")
            else:
                return redirect(f'chart/zip/{zip}')

        # diffChart compare cases
        elif form.countyCompareSubmit.data:
            if county == "Select Option" or county2 == "Select Option":
                flash("Please Select a County Option")
            else:
                return redirect(f'chart/county/{county}/{county2}')
        elif form.cityCompareSubmit.data:
            if city == "Select Option" or city2 == "Select Option":
                flash("Please Select a City Option")
            else:
                return redirect(f'chart/city/{city}/{city2}')
        elif form.zipCompareSubmit.data:
            if zip == "Select Option" or zip2 == "Select Option":
                flash("Please Select a Zip Option")
            else:
                return redirect(f'chart/zip/{zip}/{zip2}')

        # navbar search input case
        else:
            zip = request.form.get('zipInput')
            if (db.session.query(Zip_data).filter_by(zip=zip)).count() == 0:
                flash("Please Enter a Valid Zip Code")
            else:
                return redirect(f'chart/zip/{zip}')
        return redirect(f'/emissions/chart')
    
    if request.method == 'GET':
        form.countyField.choices = ["Select Option"] + [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.cityField.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).distinct(Zip_pop.city).order_by(Zip_pop.city)]
        form.zipField.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).distinct(Zip_pop.zip).order_by(Zip_pop.zip)]

        form.countyField2.choices = ["Select Option"] + [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.cityField2.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).distinct(Zip_pop.city).order_by(Zip_pop.city)]
        form.zipField2.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).distinct(Zip_pop.zip).order_by(Zip_pop.zip)]

    return render_template('mainPages/chart.html', form=form)


# -------------------------- Route to handle zip uri variable(s) and compare two zip codes ------------------------- #

@emissions_blueprint.route('/chart/zip/<zip>')
@emissions_blueprint.route('/chart/zip/<zip>/<zip2>')
def chartZip(zip, zip2=None):

    form = CityCountyZipDropDown()
    query = db.session.query(Zip_data).filter_by(zip=zip)
    if zip2 != None:
        query2 = db.session.query(Zip_data).filter_by(zip=zip2)
        if query2.count() == 0:
            flash("That Zip Code Does Not Exist!")
            return redirect(f'/emissions/chart')


    if query.count() == 0:
        flash("That Zip Code Does Not Exist!")
        return redirect(f'/emissions/chart')
    
    # Table 1
    for row in query:
        data = object_as_dict(row)

    # Remove zip and pop non-numerical data points
    data.pop('population2018')
    data.pop('zip')
    city = data.pop('city')
    county = data.pop('county')

    # Convert to list of lists and add labels
    chartData = list(map(list, data.items()))
    chartData.insert(0, ['Sector', 'GHG Emissions'])

    form.countyField.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
    form.cityField.choices = [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county).distinct(Zip_pop.county).order_by(Zip_pop.city)]
    form.zipField.choices = [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city).all()]
    form.zipField.data = zip
    form.cityField.data = city
    form.countyField.data = county

    if zip2 != None:
        for row in query2:
            data2 = (object_as_dict(row))

        # Remove unneeded and pop non-numerical data points
        data2.pop('population2018')
        data2.pop('zip')
        city2 = data2.pop('city')
        county2 = data2.pop('county')

        # Convert to list of lists and add labels
        chartData2 = list(map(list, data2.items()))
        chartData2.insert(0, ['Sector', 'GHG Emissions'])

        form.countyField2.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.cityField2.choices = [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county2).distinct(Zip_pop.county).order_by(Zip_pop.city)]
        form.zipField2.choices = [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city2).all()]
        form.zipField2.data = zip2
        form.cityField2.data = city2
        form.countyField2.data = county2
        return render_template('mainPages/chart.html', form=form, chartData1=chartData, chartData2=chartData2, area1=zip, area2=zip2, compare=True)
    return render_template('mainPages/chart.html', form=form, chartData=chartData, area=zip)


# -------------------------- Route to handle city uri variable(s) and compare ------------------------- #

@emissions_blueprint.route('/chart/city/<city>')
@emissions_blueprint.route('/chart/city/<city>/<city2>')
def chartCity(city, city2=None):
    form = CityCountyZipDropDown()

    query = db.session.query(Zip_data).filter_by(city=city)
    if city2 != None:    
        query2 = db.session.query(Zip_data).filter_by(city=city2)
        if query2.count() == 0:
            flash("That City Does Not Exist!")
            return redirect(f'/emissions/chart')


    if query.count() == 0:
        flash("That City Does Not Exist!")
        return redirect(f'/emissions/chart')

    else:
        rows = []
        for row in query:
            d = object_as_dict(row)
            d.pop('population2018')
            d.pop('zip')
            city = d.pop('city')
            county = d.pop('county')

            rows.append(d)
        
        # sum the values with same keys 
        counter = collections.Counter() 
        for d in rows:  
            counter.update(d)
        data = dict(counter) 

        # Convert to list of lists and add labels
        chartData = list(map(list, data.items()))
        chartData.insert(0, ['Sector', 'GHG Emissions'])

        form.countyField.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.cityField.choices = [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county).distinct(Zip_pop.county).order_by(Zip_pop.city)]
        form.zipField.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city).all()]
        form.zipField.data = ["Select Option"]
        form.cityField.data = city
        form.countyField.data = county

        if city2 != None:
            rows = []
            for row in query2:
                d = object_as_dict(row)
                d.pop('population2018')
                d.pop('zip')
                city2 = d.pop('city')
                county2 = d.pop('county')
                rows.append(d)
            
            # sum the values with same keys 
            counter = collections.Counter() 
            for d in rows:  
                counter.update(d)
            data2 = dict(counter) 

            # Convert to list of lists and add labels
            chartData2 = list(map(list, data2.items()))
            chartData2.insert(0, ['Sector', 'GHG Emissions'])

            form.countyField2.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
            form.cityField2.choices = [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county2).distinct(Zip_pop.county).order_by(Zip_pop.city)]
            form.zipField2.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city2).all()]
            form.zipField2.data = ["Select Option"]
            form.cityField2.data = city2
            form.countyField2.data = county2
            return render_template('mainPages/chart.html', form=form, chartData1=chartData, chartData2=chartData2, area1=city, area2=city2, compare=True)
        return render_template('mainPages/chart.html', form=form, chartData=chartData, area=city)


# -------------------------- Route to handle county uri variable(s) and compare ------------------------- #

@emissions_blueprint.route('/chart/county/<county>')
@emissions_blueprint.route('/chart/county/<county>/<county2>')
def chartCounty(county, county2=None):
    form = CityCountyZipDropDown()
    query = db.session.query(Zip_data).filter_by(county=county)
    if county2 != None:
        query2 = db.session.query(Zip_data).filter_by(county=county2)
        if query2.count() == 0:
            flash("That Zip Code Does Not Exist!")
            return redirect(f'/emissions/chart')

    if query.count() == 0:
        flash("That Zip Code Does Not Exist!")
        return redirect(f'/emissions/chart')

    else:
        rows = []
        for row in query:
            d = object_as_dict(row)
            d.pop('population2018')
            d.pop('zip')
            city = d.pop('city')
            county = d.pop('county')
            rows.append(d)
        
        # sum the values with same keys 
        counter = collections.Counter() 
        for d in rows:  
            counter.update(d)
        data = dict(counter) 

        # Convert to list of lists and add labels
        chartData = list(map(list, data.items()))
        chartData.insert(0, ['Sector', 'GHG Emissions'])

        print(chartData)

        form.countyField.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
        form.cityField.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county).distinct(Zip_pop.county).order_by(Zip_pop.city)]
        form.zipField.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city).all()]
        form.zipField.data = ["Select Option"]
        form.cityField.data = ["Select Option"]
        form.countyField.data = county

        if county2 != None:
            rows = []
            for row in query2:
                d = object_as_dict(row)
                d.pop('population2018')
                d.pop('zip')
                city2 = d.pop('city')
                county2 = d.pop('county')

                rows.append(d)
            
            # sum the values with same keys 
            counter = collections.Counter() 
            for d in rows:  
                counter.update(d)
            data2 = dict(counter) 

            # Convert to list of lists and add labels
            chartData2 = list(map(list, data2.items()))
            chartData2.insert(0, ['Sector', 'GHG Emissions'])


            form.countyField2.choices = [(row.county) for row in db.session.query(Zip_pop.county).distinct(Zip_pop.county).order_by(Zip_pop.county)]
            form.cityField2.choices = ["Select Option"] + [(row.city) for row in db.session.query(Zip_pop.city).filter_by(county=county2).distinct(Zip_pop.county).order_by(Zip_pop.city)]
            form.zipField2.choices = ["Select Option"] + [(row.zip) for row in db.session.query(Zip_pop.zip).filter_by(city=city2).all()]
            form.zipField2.data = ["Select Option"]
            form.cityField2.data = ["Select Option"]
            form.countyField2.data = county2

            return render_template('mainPages/chart.html', form=form, chartData1=chartData, chartData2=chartData2, area1=county, area2=county2, compare=True)
        return render_template('mainPages/chart.html', form=form, chartData=chartData, area=county)
