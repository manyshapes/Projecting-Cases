from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chart1')
def chart1():
    df = pd.read_csv('all_diseases.csv')

    linefig = px.line(df, x="date", y="no_cases", color="disease")
    

    linegraphJSON = json.dumps(linefig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Counts Across Dates"
    description = """
    Have to clean up chart, should be median cases across countries.
    """

    return render_template('pg1_1.html', graphJSON=linegraphJSON, header=header,description=description)

@app.route('/chart2')
def chart2():
    df = pd.read_csv('all_diseases.csv')

    fig = px.scatter_geo(df, locations="iso_code", size="cumulative_cases", color="disease")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Cumulative Counts of Disease Across All Continents"
    description = """
    Bubble size represents counts of Covid, Dengue, Malaria, Zika
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)




    