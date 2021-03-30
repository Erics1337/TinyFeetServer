from flask import Blueprint,render_template,redirect,url_for,request, jsonify, flash
from server import db
from sqlalchemy import distinct, inspect, and_, or_, desc


from server.models import Cement_and_manufacturing, Electricity, Natural_gas, Otis_transportation, Waste, Aviation, Zip_pop, Zip_data, Solutions
from server.survey.forms import RecForm
from server.emissions.views import object_as_dict, coalesce
import collections

survey_blueprint = Blueprint('survey', __name__, template_folder='../templates')


# Actions
@survey_blueprint.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    
    # form = RecForm()
    # tableData = []

    # if request.method == 'POST':
    #     if form.allSol.data & form.allSec.data:
    #         query = Solutions.query.all()
    # # query = session.query.with_entities(Solutions.recommendations_id, Solutions.section, Solutions.subsection, Solutions.solution_description, Solutions.ghg_reduction_potential).all()
    #     elif form.allSol.data == False:
    #         if form.allSec.data == True:
    #             query = Solutions.query.filter((Solutions.equity & form.equity.data) | \
    #             (Solutions.economic_sustainability & form.econSus.data) | \
    #             (Solutions.local_environmental_quality & form.envQuality.data) | \
    #             (Solutions.enhances_public_safety & form.healthSafety.data) | \
    #             (Solutions.builds_resilience & form.resilience.data))
    #         elif form.allSec.data == False:
    #             if form.transportation.data == True:
    #                 if form.energy.data == False: 
    #                     if form.waste.data == False:
    #                         query = Solutions.query.filter(((Solutions.equity & form.equity.data) | \
    #                         (Solutions.economic_sustainability & form.econSus.data) | \
    #                         (Solutions.local_environmental_quality & form.envQuality.data) | \
    #                         (Solutions.enhances_public_safety & form.healthSafety.data) | \
    #                         (Solutions.builds_resilience & form.resilience.data)) & (Solutions.vech_tran))
    #             if form.transportation.data == True:
    #                 if form.energy.data == True:
    #                     if form.waste.data == False:
    #                         query = Solutions.query.filter(((Solutions.equity & form.equity.data) | \
    #                         (Solutions.economic_sustainability & form.econSus.data) | \
    #                         (Solutions.local_environmental_quality & form.envQuality.data) | \
    #                         (Solutions.enhances_public_safety & form.healthSafety.data) | \
    #                         (Solutions.builds_resilience & form.resilience.data)) & ((Solutions.vech_tran) | (Solutions.energy)))
    #             if form.transportation.data == True:
    #                 if form.energy.data == False:
    #                     if form.waste.data == True:
    #                         query = Solutions.query.filter(((Solutions.equity & form.equity.data) | \
    #                         (Solutions.economic_sustainability & form.econSus.data) | \
    #                         (Solutions.local_environmental_quality & form.envQuality.data) | \
    #                         (Solutions.enhances_public_safety & form.healthSafety.data) | \
    #                         (Solutions.builds_resilience & form.resilience.data)) & ((Solutions.vech_tran) | (Solutions.waste)))
    #             if form.transportation.data == False:
    #                 if form.energy.data == True:
    #                     if form.waste.data == False:
    #                         query = Solutions.query.filter(((Solutions.equity & form.equity.data) | \
    #                         (Solutions.economic_sustainability & form.econSus.data) | \
    #                         (Solutions.local_environmental_quality & form.envQuality.data) | \
    #                         (Solutions.enhances_public_safety & form.healthSafety.data) | \
    #                         (Solutions.builds_resilience & form.resilience.data)) & (Solutions.energy))
    #             if form.transportation.data == False:
    #                 if form.energy.data == True:
    #                     if form.waste.data == True:
    #                         query = Solutions.query.filter(((Solutions.equity & form.equity.data) | \
    #                         (Solutions.economic_sustainability & form.econSus.data) | \
    #                         (Solutions.local_environmental_quality & form.envQuality.data) | \
    #                         (Solutions.enhances_public_safety & form.healthSafety.data) | \
    #                         (Solutions.builds_resilience & form.resilience.data)) & ((Solutions.energy) | (Solutions.waste)))
    #             if form.transportation.data == False:
    #                 if form.energy.data == False:
    #                     if form.waste.data == True:
    #                         query = Solutions.query.filter(((Solutions.equity & form.equity.data) | \
    #                         (Solutions.economic_sustainability & form.econSus.data) | \
    #                         (Solutions.local_environmental_quality & form.envQuality.data) | \
    #                         (Solutions.enhances_public_safety & form.healthSafety.data) | \
    #                         (Solutions.builds_resilience & form.resilience.data)) & (Solutions.waste))
    #     else:
    #         if form.allSol.data == True:
    #             query = Solutions.query.filter((Solutions.vech_tran & form.transportation.data) | \
    #             (Solutions.energy & form.energy.data) | \
    #             (Solutions.waste & form.waste.data))

    #     # Data is just a dictionary after conversion so can be manipulated using basic dictionary comprehension
    #     # You can comment out the pop functions to help debug
    #     for row in query:
    #         d = object_as_dict(row)
    #         # d.pop('recommendations_id')
    #         # d.pop('equity')
    #         # d.pop('economic_sustainability')
    #         # d.pop('local_environmental_quality')
    #         # d.pop('enhances_public_safety')
    #         # d.pop('builds_resilience')
    #         # d.pop('vech_tran')
    #         # d.pop('energy')
    #         # d.pop('waste')

    #         # These columns are probably unneccesary.  We should also think about displaying the data in a way other than a table
    #         # Like maybe a card with a picture or something
    #         # d.pop('section')
    #         # d.pop('subsection')
    #         # d.pop('ghg_reduction_potential')

    #         tableData.append(d.values())

    #     print(len(tableData))

    #     # Column names are the dict keys
    #     columnNames = [column.replace("_", " ").capitalize() for column in d.keys()]

    #     return render_template('/mainPages/recommendations.html', form=form, columnNames=columnNames, tableData=tableData)





    # Initialize
    form = RecForm()
    tableData = []
    if request.method == 'POST':

        tableData = []
        columnNames = []
        equity = econSus = envQuality = healthSafety = resilience = waste = energy = vech_tran = allSol = allSec = None
        
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

        if form.allSec.data:
            allSec = 1
        if form.transportation.data:
            vech_tran = 1
        if form.energy.data:
            energy = 1
        if form.waste.data:
            waste = 1

        # Error Checking for no input
        if equity == None and econSus == None and envQuality == None and healthSafety == None and resilience == None and allSol == None:
            flash("Please Select a Solution Type")
            return render_template('/mainPages/recommendations.html', form=form)

        if vech_tran == None and energy == None and waste == None and allSec == None:
            flash("Please Select an Emissions Sector")
            return redirect('/recommendations')


        # All solutions / all sector cases
        if form.allSol.data and form.allSec.data:
            query = db.session.query(Solutions).order_by(desc('ghg_reduction_potential'))

        elif form.allSol.data:
            query = db.session.query(Solutions).filter(or_(
                        Solutions.vech_tran==vech_tran,
                        Solutions.energy==energy,
                        Solutions.waste==waste
                        )).order_by(desc('ghg_reduction_potential'))

        elif form.allSec.data:
            query = db.session.query(Solutions).filter(or_(
                        Solutions.equity==equity,
                        Solutions.economic_sustainability==econSus,
                        Solutions.local_environmental_quality==envQuality,
                        Solutions.enhances_public_safety==healthSafety,
                        Solutions.builds_resilience==resilience,
                        ))
                        # .order_by(desc('ghg_reduction_potential'))



        # Specific solution/solutions and sector/sectors case
        # Combination of solutions inputs are AND case, combination of sector inputs are OR case
        else:
            query = db.session.query(Solutions).filter(or_(
                        Solutions.equity==equity,
                        Solutions.economic_sustainability==econSus,
                        Solutions.local_environmental_quality==envQuality,
                        Solutions.enhances_public_safety==healthSafety,
                        Solutions.builds_resilience==resilience,
                        )).filter(or_(                        
                        Solutions.vech_tran==vech_tran,
                        Solutions.energy==energy,
                        Solutions.waste==waste
                        ))
                        # .order_by(desc('ghg_reduction_potential'))
        
        
        # Error check no results from query
        if query.count() == 0:
            flash("No recommendations for that combination of filter settings")
            return redirect('/recommendations')


        # Data is just a dictionary after conversion so can be manipulated using basic dictionary comprehension
        # You can comment out the pop functions to help debug
        for row in query:
            d = object_as_dict(row)
            d.pop('recommendations_id')
            d.pop('equity')
            d.pop('economic_sustainability')
            d.pop('local_environmental_quality')
            d.pop('enhances_public_safety')
            d.pop('builds_resilience')
            d.pop('vech_tran')
            d.pop('energy')
            d.pop('waste')

            # These columns are probably unneccesary.  We should also think about displaying the data in a way other than a table
            # Like maybe a card with a picture or something.
            # d.pop('section')
            # d.pop('subsection')
            # d.pop('ghg_reduction_potential')

            tableData.append(d.values())

        # Column names are the dict keys
        columnNames = [column.replace("_", " ").capitalize() for column in d.keys()]

        print(len(tableData))

        # This is the POST return
        return render_template('/mainPages/recommendations.html', form=form, columnNames=columnNames, tableData=tableData)
    # Fall-through GET request case return
    return render_template('/mainPages/recommendations.html', form=form)