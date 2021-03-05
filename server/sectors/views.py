from flask import Blueprint,render_template,redirect,url_for,request, jsonify, flash
from server import db
from server.sectors.forms import CityCountyZipDropDown
from server.models import cement_and_manufacturing, electricity, natural_gas, otis_transportation, waste, aviation, zip_pop, Zip_data
from sqlalchemy import distinct, inspect

sectors_blueprint = Blueprint('sectors', __name__, template_folder='../templates')


# ----------------------------- Helper Functions ----------------------------- #
# This function replaces Null or 'None' values with 0 to play nice with google charts
def coalesce(*arg): return next((a for a in arg if a is not None), 0)

# This function converts query result to dict
def object_as_dict(obj):
    return {c.key: coalesce(getattr(obj, c.key))
        for c in inspect(obj).mapper.column_attrs}


# ------------------------------ Read page route ----------------------------- #
@sectors_blueprint.route('/read')
def read():
    Cement_And_Manufacturing = cement_and_manufacturing.query.all()
    Electricity = electricity.query.all()
    Natural_gas = natural_gas.query.all()
    OTIS_Transportation = otis_transportation.query.all()
    Waste = waste.query.all()
    Aviation = aviation.query.all()
    Zip_pop = zip_pop.query.all()
    return render_template('/mainPages/read.html', 
        Cement_And_Manufacturing=Cement_And_Manufacturing, 
        Electricity=Electricity,
        Natural_gas=Natural_gas,
        OTIS_Transportation=OTIS_Transportation,
        Waste=Waste,
        Aviation=Aviation,
        Zip_pop=Zip_pop
        )


# ------- Select page GET route and POST form handling to load table chart ------- #
@sectors_blueprint.route('/emissions', methods=['GET', 'POST'])
def emissions():
    form = CityCountyZipDropDown()
    form.county.choices = [(row.county) for row in db.session.query(zip_pop.county).distinct(zip_pop.county).order_by(zip_pop.county)]
    form.city.choices=["Select Option"]
    form.zip.choices=["Select Option"]
    city = form.city.data
    zip = form.zip.data

    if request.method == 'POST':
        if city == "Select Option" or zip=="Select Option":
            flash("Please Select a County Option")
        else:
            return redirect(f'emissions/{zip}')

        return render_template('mainPages/emissions.html', form=form)
    return render_template('mainPages/emissions.html', form=form)


# ------------------------------ navbar redirect ----------------------------- #
@sectors_blueprint.route('', methods=['POST'])
def search():
    zip = request.form.get('zipInput')
        
    return redirect(f'sectors/emissions/{zip}')


# -------------------------- Generate Chart From Zip ------------------------- #

@sectors_blueprint.route('/emissions/<zip>', methods=['GET', 'POST'])
def chart(zip):

    form = CityCountyZipDropDown()

    query = db.session.query(Zip_data).filter_by(zip=zip)
    print(query)
    if query.count() == 0:
        flash("That Zip Code Does Not Exist!")
        return render_template('mainPages/emissions.html', form=form,)

    else:
        for row in query:
            data = (object_as_dict(row))


        data.pop('zip')

        city = data.pop('city')
        county = data.pop('county')
        zipData = {'sector':'Emissions'}
        zipData.update(data)
        

        # Change back dropdown options after they reset on page reload
        form.county.choices = [(row.county) for row in db.session.query(zip_pop.county).distinct(zip_pop.county).order_by(zip_pop.county)]
        form.county.default = county
        form.city.choices = [(row.city, row.city) for row in db.session.query(zip_pop.city).filter_by(county=county).distinct(zip_pop.county).order_by(zip_pop.city)]
        form.zip.choices = [(row.zip, row.zip) for row in db.session.query(zip_pop.zip).filter_by(city=city).all()]
        
        return render_template('mainPages/emissions.html', form=form, zipData=zipData)


# --------------------- Dynamic Dropdown Option Changing for Select page--------------------- #
@sectors_blueprint.route('/county/<county>')
def city(county):
    rows = db.session.query(zip_pop.city).filter_by(county=county).distinct(zip_pop.county).order_by(zip_pop.city)
    cityArray = []
    for row in rows:
        cityObj = {}
        cityObj['option'] = row.city
        cityArray.append(cityObj)
    return jsonify({'cities' : cityArray})


@sectors_blueprint.route('/county/<county>/city/<city>')
def zip(county, city):
    rows = db.session.query(zip_pop.zip).filter_by(city=city).all()
    zipArray = []
    for row in rows:
        zipObj = {}
        zipObj['option'] = row.zip
        zipArray.append(zipObj)
    return jsonify({'zip_codes' : zipArray})

