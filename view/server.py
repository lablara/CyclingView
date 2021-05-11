from flask import Flask, render_template, Response, redirect, request
import subprocess
import os
from os import listdir
from os.path import isfile, join

app = Flask(__name__)
currentMap = None
date = None
period = None
variable = None

@app.route('/')
def index():
    print(variable)
    return render_template('index.html', periodCheck = period, variableCheck = variable, dateCheck = date)

@app.route('/dateChange/', methods=['POST'])
def dateChange():
    global date
    global period
    global variable

    date = request.form['date_change_picker']
    period = request.form['periodList']
    variable = request.form['variableList']

    processedDate = None
    if period == "daily":
        processedDate = date[8:10]+"-"+date[5:7]+"-"+date[0:4]
    elif period == "monthly":
        processedDate = date[5:7]+"-"+date[0:4]
    elif period == "yearly":
        processedDate = date[0:4]
    get_map(processedDate+"_"+variable)
    return redirect('/')

def get_map(mapName):
    global currentMap
    try:
        os.system("cp ../controller/webapplicationInput/"+mapName+".html templates/map.html")
        os.system("cp -v ../controller/webapplicationInput/stretchsHistoricalGraphs/"+mapName[0:10]+"* static/graphs/")
        currentMap = mapName
    except:
        None

def available_maps():
    mapsPath = "../controller/webapplicationInput/"
    mapsFiles = [f.replace('.html', '') for f in listdir(mapsPath) if isfile(join(mapsPath, f))]
    mapsFiles.sort()
    return mapsFiles

if __name__ == '__main__':
    mapsFiles = available_maps()
    get_map(mapsFiles[len(mapsFiles) - 1])

    app.run(host="localhost",debug=True)
