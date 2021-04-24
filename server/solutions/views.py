from flask import Blueprint,render_template,redirect,url_for,request, jsonify, flash
from server import db
from sqlalchemy import distinct, inspect, and_, or_, desc

from server.models import Cement_and_manufacturing, Electricity, Natural_gas, Otis_transportation, Waste, Aviation, Zip_pop, Zip_data, City_data, County_data, Solutions
from server.solutions.forms import RecForm
from server.emissions.views import object_as_dict, coalesce
import collections

solutions_blueprint = Blueprint('solutions', __name__, template_folder='../templates')


# Actions
@solutions_blueprint.route('/recommendations', methods=['GET', 'POST'])
def recommendations():

    form = RecForm()
    tableData = []
    if request.method == 'POST':

        # Initialize Variables
        tableData = []
        columnNames = []
        equity = econSus = envQuality = healthSafety = resilience = allSol = None
        electricity_commercial = electricity_industrial = electricity_residential = \
            naturalGas_commercial = naturalGas_industrial = naturalGas_residential = \
                transportation_PV_gas = transportation_PV_diesel = transportation_trucks_gas = \
                    transportation_trucks_diesel = aviation = waste = cement_and_manufacturing = None
        
        # Grab boolean form data
        if form.allSol.data:
            allSol = 1
        if form.equity.data:
            equity = 1
        if form.econSus.data:
            econSus = 1
        if form.envQuality.data:
            envQuality = 1
        if form.healthSafety.data:
            healthSafety = 1
        if form.resilience.data:
            resilience = 1


        # Error Checking for no input
        if equity == None and econSus == None and envQuality == None and healthSafety == None and resilience == None and allSol == None:
            flash("Please Select a Solution Type")
            return render_template('/mainPages/recommendations.html', form=form)
        if form.areaRadio.data == None and form.areaRadio.data == None and form.areaRadio.data == None:
            flash("Please Select an area filter type")
            return redirect('/recommendations')


# ------------------------- Get data for inputted zip ------------------------ #
        if form.areaRadio.data == 'zip':
            # Check for correct input
            if form.areaField.data.isdigit():
                area = form.areaField.data
            else:
                flash("Please enter a 5 digit Zip Code number")
                return redirect(f'/recommendations')

            query = db.session.query(Zip_data).filter_by(zip=int(area))
            if query.count() == 0:
                flash("That Zip Code Does Not Exist!")
                return redirect(f'/recommendations')

            # Search database for top sub-sectors for entered zip
            for row in query:
                data = object_as_dict(row)
    
            data.pop('population2018')
            data.pop('zip')
            city = data.pop('city')
            county = data.pop('county')

            sortedData = sorted(data.items(), key=lambda x: x[1], reverse=True)
            topSubSectors = (sortedData[0][0], sortedData[1][0], sortedData[2][0])

            if 'electricity_commercial' in topSubSectors:
                electricity_commercial = 1
            if 'electricity_industrial' in topSubSectors:
                electricity_industrial = 1
            if 'electricity_residential'  in topSubSectors:
                electricity_residential = 1
            if 'naturalGas_commercial' in topSubSectors:
                naturalGas_commercial = 1
            if 'naturalGas_industrial' in topSubSectors:
                naturalGas_industrial = 1
            if 'naturalGas_residential' in topSubSectors:
                naturalGas_residential = 1
            if 'transportation_PV_gas' in topSubSectors:
                transportation_PV_gas = 1
            if 'transportation_PV_diesel' in topSubSectors:
                transportation_PV_diesel = 1
            if 'transportation_trucks_gas' in topSubSectors:
                transportation_trucks_gas = 1
            if 'transportation_trucks_diesel' in topSubSectors:
                transportation_trucks_diesel = 1
            if 'aviation' in topSubSectors:
                aviation = 1
            if 'waste' in topSubSectors:
                waste = 1
            if 'cement_and_manufacturing' in topSubSectors:
                cement_and_manufacturing = 1

# ------------------------ Get data for inputted city ------------------------ #
        if form.areaRadio.data == 'city':
            # Check for correct input
            if form.areaField.data.isdigit():
                flash("Please enter a City name")
                return redirect(f'/recommendations')                
            else:
                area = form.areaField.data.capitalize()

            # Query City ORM model 
            query = db.session.query(City_data).filter_by(city=area)
            if query.count() == 0:
                flash("That City Does Not Exist!")
                return redirect(f'/recommendations')

            # Search database for top sub-sectors for entered area
            for row in query:
                data = object_as_dict(row)
    
            # Remove non-numerical data points
            city = data.pop('city')
            county = data.pop('county')

            # Sort top sectors for given area and store in tuple
            sortedData = sorted(data.items(), key=lambda x: x[1], reverse=True)
            topSubSectors = (sortedData[0][0], sortedData[1][0], sortedData[2][0])

            # Assign value to sub-sector variable if a top Sub-Sector
            if 'electricity_commercial' in topSubSectors:
                electricity_commercial = 1
            if 'electricity_industrial' in topSubSectors:
                electricity_industrial = 1
            if 'electricity_residential'  in topSubSectors:
                electricity_residential = 1
            if 'naturalGas_commercial' in topSubSectors:
                naturalGas_commercial = 1
            if 'naturalGas_industrial' in topSubSectors:
                naturalGas_industrial = 1
            if 'naturalGas_residential' in topSubSectors:
                naturalGas_residential = 1
            if 'transportation_PV_gas' in topSubSectors:
                transportation_PV_gas = 1
            if 'transportation_PV_diesel' in topSubSectors:
                transportation_PV_diesel = 1
            if 'transportation_trucks_gas' in topSubSectors:
                transportation_trucks_gas = 1
            if 'transportation_trucks_diesel' in topSubSectors:
                transportation_trucks_diesel = 1
            if 'aviation' in topSubSectors:
                aviation = 1
            if 'waste' in topSubSectors:
                waste = 1
            if 'cement_and_manufacturing' in topSubSectors:
                cement_and_manufacturing = 1
        
# ----------------------- Get data for inputted county ----------------------- #
        if form.areaRadio.data == 'county':
            # Check for correct input
            if form.areaField.data.isdigit():
                flash("Please enter a County name")
                return redirect(f'/recommendations')                
            else:
                area = form.areaField.data.capitalize()

            # Query City ORM model 
            query = db.session.query(County_data).filter_by(county=area)
            if query.count() == 0:
                flash("That County Does Not Exist!")
                return redirect(f'/recommendations')

            # Search database for top sub-sectors for entered area
            for row in query:
                data = object_as_dict(row)
    
            # Remove non-numerical data points
            data.pop('population2018')
            county = data.pop('county')

            # Sort top sectors for given area and store in tuple
            sortedData = sorted(data.items(), key=lambda x: x[1], reverse=True)
            topSubSectors = (sortedData[0][0], sortedData[1][0], sortedData[2][0])

            # Assign value to sub-sector variable if a top Sub-Sector
            if 'electricity_commercial' in topSubSectors:
                electricity_commercial = 1
            if 'electricity_industrial' in topSubSectors:
                electricity_industrial = 1
            if 'electricity_residential'  in topSubSectors:
                electricity_residential = 1
            if 'naturalGas_commercial' in topSubSectors:
                naturalGas_commercial = 1
            if 'naturalGas_industrial' in topSubSectors:
                naturalGas_industrial = 1
            if 'naturalGas_residential' in topSubSectors:
                naturalGas_residential = 1
            if 'transportation_PV_gas' in topSubSectors:
                transportation_PV_gas = 1
            if 'transportation_PV_diesel' in topSubSectors:
                transportation_PV_diesel = 1
            if 'transportation_trucks_gas' in topSubSectors:
                transportation_trucks_gas = 1
            if 'transportation_trucks_diesel' in topSubSectors:
                transportation_trucks_diesel = 1
            if 'aviation' in topSubSectors:
                aviation = 1
            if 'waste' in topSubSectors:
                waste = 1
            if 'cement_and_manufacturing' in topSubSectors:
                cement_and_manufacturing = 1


# -------------------------- Get Matching Solutions -------------------------- #
        # All solutions case
        if form.allSol.data:
            query = db.session.query(Solutions).filter(or_(
                        Solutions.electricity_commercial==electricity_commercial,
                        Solutions.electricity_industrial==electricity_industrial,
                        Solutions.electricity_residential==electricity_residential,
                        Solutions.naturalGas_commercial==naturalGas_commercial,
                        Solutions.naturalGas_industrial==naturalGas_industrial,
                        Solutions.naturalGas_residential==naturalGas_residential,
                        Solutions.transportation_PV_gas==transportation_PV_gas,
                        Solutions.transportation_PV_diesel==transportation_PV_diesel,
                        Solutions.transportation_trucks_gas==transportation_trucks_gas,
                        Solutions.transportation_trucks_diesel==transportation_trucks_diesel,
                        Solutions.aviation==aviation,
                        Solutions.waste==waste,
                        Solutions.cement_and_manufacturing==cement_and_manufacturing
                        )).order_by(desc('ghg_reduction_potential'))



        # Specific solution/solutions and sector/sectors case
        else:
            query = db.session.query(Solutions).filter(or_(
                        Solutions.equity==equity,
                        Solutions.economic_sustainability==econSus,
                        Solutions.local_environmental_quality==envQuality,
                        Solutions.enhances_public_safety==healthSafety,
                        Solutions.builds_resilience==resilience,
                        )).filter(or_(                        
                        Solutions.electricity_commercial==electricity_commercial,
                        Solutions.electricity_industrial==electricity_industrial,
                        Solutions.electricity_residential==electricity_residential,
                        Solutions.naturalGas_commercial==naturalGas_commercial,
                        Solutions.naturalGas_industrial==naturalGas_industrial,
                        Solutions.naturalGas_residential==naturalGas_residential,
                        Solutions.transportation_PV_gas==transportation_PV_gas,
                        Solutions.transportation_PV_diesel==transportation_PV_diesel,
                        Solutions.transportation_trucks_gas==transportation_trucks_gas,
                        Solutions.transportation_trucks_diesel==transportation_trucks_diesel,
                        Solutions.aviation==aviation,
                        Solutions.waste==waste,
                        Solutions.cement_and_manufacturing==cement_and_manufacturing
                        )).order_by(desc('ghg_reduction_potential'))
        
        
        # Error check no results from query
        if query.count() == 0:
            flash("No recommendations for that combination of filter settings")
            return redirect('/recommendations')


        # Data is just a dictionary after conversion so can be manipulated using basic dictionary comprehension
        # You can comment out the pop functions to help debug
        for row in query:
            d = object_as_dict(row)
            d.pop('ID')
            d.pop('equity')
            d.pop('economic_sustainability')
            d.pop('local_environmental_quality')
            d.pop('enhances_public_safety')
            d.pop('builds_resilience')

            d.pop('electricity_commercial')
            d.pop('electricity_industrial')
            d.pop('electricity_residential')
            d.pop('naturalGas_commercial')
            d.pop('naturalGas_industrial')
            d.pop('naturalGas_residential')
            d.pop('transportation_PV_gas')
            d.pop('transportation_PV_diesel')
            d.pop('transportation_trucks_gas')
            d.pop('transportation_trucks_diesel')
            d.pop('aviation')
            d.pop('waste')
            d.pop('cement_and_manufacturing')

            # These columns are probably unneccesary.  
            # d.pop('section')
            # d.pop('subsection')
            # d.pop('ghg_reduction_potential')

            tableData.append(list(d.values()))

        # Get Column names from dict keys and format
        columnNames = [column.replace("_", " ").capitalize() for column in d.keys()]

        print(type(tableData[0]))
        print(tableData)

        # Create details string
        details = 'According to our data, the sectors of highest GHG emissions for '+area+' are from '+topSubSectors[0]+', '\
            +topSubSectors[1]+', and '+topSubSectors[2]+'.  We recommend considering the following actions:'


        # This is the POST return
        return render_template('/mainPages/recommendations.html', form=form, columnNames=columnNames, tableData=tableData, details=details)
    # Fall-through GET request case return
    return render_template('/mainPages/recommendations.html', form=form)