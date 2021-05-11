import folium
from folium.plugins import LocateControl
from folium.plugins import Geocoder
import branca
import branca.colormap as cm

import os
from os import listdir
from os.path import isfile, join
import json
import numpy as np
from datetime import datetime
import calendar
import matplotlib.pyplot as plt

import sys
sys.path.append('../model/')
from city import City
from monitoringsample import MonitoringSample

def main():
    #Creates maps for all variables
    airPollutionMap = folium.Map(location=[-12.280265953993627, -38.96356796067759], zoom_start=3, min_zoom = 2, max_bounds=True, height = '91.5%', control_scale=True)
    noisePollutionMap = folium.Map(location=[-12.280265953993627, -38.96356796067759], zoom_start=3, min_zoom = 2, max_bounds=True, height = '91.5%', control_scale=True)
    uvMap = folium.Map(location=[-12.280265953993627, -38.96356796067759], zoom_start=3, min_zoom = 2, max_bounds=True, height = '91.5%', control_scale=True)
    temperatureMap = folium.Map(location=[-12.280265953993627, -38.96356796067759], zoom_start=3, min_zoom = 2, max_bounds=True, height = '91.5%', control_scale=True)
    luminosityMap = folium.Map(location=[-12.280265953993627, -38.96356796067759], zoom_start=3, min_zoom = 2, max_bounds=True, height = '91.5%', control_scale=True)

    #Creates color map for all variables
    airPollutionColormap  = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'], index=[0, 10, 15, 25, 70], vmin=0, vmax=70, caption='Air pollution [µg/m³]')
    noisePollutionColormap  = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'], index=[0, 50, 55, 60, 65], vmin=0, vmax=65, caption='Noise pollution [dB]')
    uvColormap  = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'], index=[0, 2, 5, 7, 10], vmin=0, vmax=14, caption='UV levels')
    temperatureColormap = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'], index=[10, 26, 32, 39, 51], vmin=10, vmax=51, caption='Thermal sensation [ºC]')
    luminosityColormap = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'orange', 'red'], index=[0, 5000, 10000, 15000, 32000], vmin=0, vmax=32000, caption='Luminosity [lux]')

    #Cities list
    cities = list()
    #Processing period [day, month or year]
    period = None

    print("\n######################################################## MAP GENERATOR ##############################################\n")
    #Load cities paths------------------------------------------------------------------------------
    print("[INFO] Importing cities data from Processor")
    processorPath = "mapgeneratorInput/"
    processorFiles = [f for f in listdir(processorPath) if isfile(join(processorPath, f))]

    #Gets each city file
    nCities = 1
    for processorFile in processorFiles:
        #Gets period from files
        if period is None:
            period = processorFile[processorFile.rfind("_")+1:].replace(".json","")
            #Historical data range [hours, days or months]
            range = 24
            if len(period) == 7:
                range = calendar.monthrange(int(period[3:7]), int(period[0:2]))[1]
                range += 1
            elif len(period) == 4:
                range = 13
        print("  "+str(nCities)+". "+processorFile.replace(".json",""))
        cities.append(importCity(processorFile))
        nCities+=1
    print("\n---------------------------------------------------------------------------------------------------------------------\n")

    print("[INFO] Plotting cities paths stretches on map")
    #Get new city----------------------------------------------------------------------------------
    nCities = 1
    for city in cities:
        print("  "+str(nCities)+". "+city.ID)
        for path in city.paths:
            for stretch in path.stretches:
                print("    > Plotting "+stretch.ID)
                #Creates historical graphs for this stretch to plot on popup
                createHistoricalGraphs(stretch.ID, period, stretch.getHistoricalData(range))
                #Creates stretchs with historical graphs
                insertBikePath(airPollutionMap, [stretch.P1, stretch.P2], getPopupLegend(stretch.ID, "static/graphs/"+period+"-"+stretch.ID+"-0.png"))
                insertBikePath(noisePollutionMap, [stretch.P1, stretch.P2], getPopupLegend(stretch.ID, "static/graphs/"+period+"-"+stretch.ID+"-1.png"))
                insertBikePath(uvMap, [stretch.P1, stretch.P2], getPopupLegend(stretch.ID, "static/graphs/"+period+"-"+stretch.ID+"-2.png"))
                insertBikePath(temperatureMap, [stretch.P1, stretch.P2], getPopupLegend(stretch.ID, "static/graphs/"+period+"-"+stretch.ID+"-3.png"))
                insertBikePath(luminosityMap, [stretch.P1, stretch.P2], getPopupLegend(stretch.ID, "static/graphs/"+period+"-"+stretch.ID+"-4.png"))

                #Draw color map points
                for sample in stretch.monitoringData:
                    print("      . Plotting sample "+sample.deviceID+"-"+sample.date+"-"+sample.time)
                    insertMonitoringSample(airPollutionMap, airPollutionColormap, sample.coordinate, sample.data[0])
                    insertMonitoringSample(noisePollutionMap, noisePollutionColormap, sample.coordinate, sample.data[1])
                    insertMonitoringSample(uvMap, uvColormap, sample.coordinate, sample.data[2])
                    insertMonitoringSample(temperatureMap, temperatureColormap, sample.coordinate, sample.data[3])
                    insertMonitoringSample(luminosityMap, luminosityColormap, sample.coordinate, sample.data[4])
        nCities+=1

    #Inserts colormaps on maps
    airPollutionColormap.add_to(airPollutionMap)
    noisePollutionColormap.add_to(noisePollutionMap)
    uvColormap.add_to(uvMap)
    temperatureColormap.add_to(temperatureMap)
    luminosityColormap.add_to(luminosityMap)

    #Inserts location control on maps
    folium.plugins.LocateControl().add_to(airPollutionMap)
    folium.plugins.LocateControl().add_to(noisePollutionMap)
    folium.plugins.LocateControl().add_to(uvMap)
    folium.plugins.LocateControl().add_to(temperatureMap)
    folium.plugins.LocateControl().add_to(luminosityMap)

    #Inserts search bar on maps
    folium.plugins.Geocoder().add_to(airPollutionMap)
    folium.plugins.Geocoder().add_to(noisePollutionMap)
    folium.plugins.Geocoder().add_to(uvMap)
    folium.plugins.Geocoder().add_to(temperatureMap)
    folium.plugins.Geocoder().add_to(luminosityMap)

    #Saves maps html
    airPollutionMap.save("webapplicationInput/"+period+"_air.html")
    noisePollutionMap.save("webapplicationInput/"+period+"_noise.html")
    uvMap.save("webapplicationInput/"+period+"_uv.html")
    temperatureMap.save("webapplicationInput/"+period+"_temperature.html")
    luminosityMap.save("webapplicationInput/"+period+"_luminosity.html")

#Creates popup with historical graph and stretch ID
def getPopupLegend(stretchID, graphPathName):
    popupLegend="""
    <font size="2"><b>{id}</b></font><br>
    <img src="{graphPath}" alt="graph">
    """.format(id=stretchID, graphPath=graphPathName)

    return popupLegend

#Creates historical graph
def createHistoricalGraphs(stretchID, period, data):
    #Computes x axis title by monitoring period
    xLabel = "Hour"
    title = "Daily history graph ("+period+")"
    if len(period) == 7:
        xLabel = "Day"
        title = "Monthly history graph ("+period+")"
    elif len(period) == 4:
        xLabel = "Month"
        title = "Yearly history graph ("+period+")"

    #Sets y axis title by monitoring variable and plots the graph
    for index in range(6):
        yLabel = 'Air pollution (µg/m³)'
        if index == 2:
            yLabel = 'Noise pollution (dB)'
        elif index == 3:
            yLabel = 'UV level'
        elif index == 4:
            yLabel = 'Thermal sensation (°C)'
        elif index == 5:
            yLabel = 'Luminosity (lux)'

        #Plot
        if index > 0:
            plt.xticks(data[0], fontsize=7, rotation=45)
            plt.bar(data[0], data[index])
            plt.title(title)
            plt.xlabel(xLabel)
            plt.ylabel(yLabel)
            plt.savefig("webapplicationInput/stretchsHistoricalGraphs/"+period+"-"+stretchID+"-"+str(index - 1)+".png")
            plt.clf()

#Draws bike path
def insertBikePath(map, path, popupLegend):
    popup = folium.Popup(popupLegend, max_width=180,min_width=180)
    folium.PolyLine(path, color="black",  weight=4, opacity=0.5, popup=popup).add_to(map)

#Draws monitoring points by color
def insertMonitoringSample(map, colormap, coordinate, value):
    color = colormap(value)
    folium.PolyLine([coordinate, coordinate], color=color,  weight=20, opacity=0.7).add_to(map)

def importCity(cityFileName):
    #City file name
    fileName = "mapgeneratorInput/"+cityFileName
    #City object
    city = None

    with open(fileName) as infile:
        #Loads city JSON file
        cityData = json.load(infile)

        #Loads city info by JSON data
        city = City(cityFileName[:cityFileName.rfind("_")])

        pathCount = 1
        for pathData in cityData['paths']:
            print("    > Path "+str(pathCount)+": "+pathData['ID'])
            print("      - Construction date: "+pathData['constructionDate'])
            print("      - Maintenance date: "+pathData['maintenanceDate'])
            print("      - Inspection date: "+pathData['inspectionDate'])
            print("      - Creator: "+str(pathData['creator']))

            #Loads path info by JSON dataself.location
            path = city.insertPath(pathData['ID'], pathData['constructionDate'], pathData['maintenanceDate'], pathData['inspectionDate'], pathData['creator'])
            stretchCount = 1
            #Loads stretch info by JSON data
            for stretchData in pathData['stretches']:
                print("      - Stretch "+str(stretchCount)+": "+stretchData['ID'])
                print("        . Points connection: "+str(stretchData['P1'])+" - "+str(stretchData['P2']))
                stretch = path.insertStretch(stretchData['ID'], stretchData['P1'], stretchData['P2'])

                for sampleData in stretchData['monitoringData']:
                    sample = MonitoringSample(sampleData["deviceID"], sampleData["date"], sampleData["time"], sampleData["coordinate"], sampleData["data"])
                    stretch.monitoringData.append(sample)
                    print("        . Sample "+sample.deviceID+"-"+sample.date+"-"+sample.time+": "+str(sample.data))

                stretchCount+=1
            pathCount+=1

    os.system("rm "+fileName)
    return city

if __name__ == "__main__":
    main()
