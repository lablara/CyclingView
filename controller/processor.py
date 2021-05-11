import sys
import json
import csv
import reverse_geocode
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from datetime import datetime

sys.path.append('../model/')
from city import City
from monitoringsample import MonitoringSample

def main(period):
    cities = list()
    monitoringSamples = list()
    statisticSamples = list()

    print("\n######################################################## PROCESSOR ##############################################\n")
    #Load cities paths------------------------------------------------------------------------------
    print("[INFO] Importing cities data from BikePathGenerator module")
    bikePathGenPath = "processorInput/BikePathGenerator/"
    bikePathGenFiles = [f for f in listdir(bikePathGenPath) if isfile(join(bikePathGenPath, f))]
    #Gets each city file
    nCities = 1
    for bikePathGenFile in bikePathGenFiles:
        print("  "+str(nCities)+". "+bikePathGenFile.replace(".json",""))
        cities.append(importCity(bikePathGenFile))
        nCities+=1

    print("\n---------------------------------------------------------------------------------------------------------------------\n")
    #Load monitoring samples------------------------------------------------------------------------
    print("[INFO] Importing monitoring samples from BikeSensor module")
    bikeSensorPath = "processorInput/BikeSensor/"
    bikeSensorFiles = [f for f in listdir(bikeSensorPath) if isfile(join(bikeSensorPath, f))]
    #Gets each MMS sample file
    nCities = 1
    for bikeSensorFile in bikeSensorFiles:
        bikeSensorFileName = bikeSensorFile.replace(".csv","")
        bikeSensorFileDate = bikeSensorFileName[bikeSensorFileName.find("_") + 1:]

        if period in bikeSensorFileDate:
            print("  "+str(nCities)+". "+bikeSensorFileName)
            fileMonitoringSamples = importMonitoringSample(bikeSensorFile).copy()
            for fileMonitoringSample in fileMonitoringSamples:
                monitoringSamples.append(fileMonitoringSample)

    print("\n---------------------------------------------------------------------------------------------------------------------\n")

    print("[INFO] Processing cities monitoring samples")
    #Get new city----------------------------------------------------------------------------------
    nCities = 1
    for city in cities:
        print("  "+str(nCities)+". "+city.ID)
        statisticData = list()
        detectedPoints = list()
        undetectedPoints = list()

        #Process monitoring data-------------------------------------------------------------------
        nSamples = 1
        for monitoringSample in monitoringSamples:

            #Gets city by GPS coordinate
            coordinate = [float(monitoringSample.coordinate[0]), float(monitoringSample.coordinate[1])],[0, 0]
            reverseCoordinate = reverse_geocode.search(coordinate)[0]
            monitoringSampleCity = reverseCoordinate['city'] + "-" + reverseCoordinate['country_code']
            monitoringSampleCity = monitoringSampleCity.replace(' ', '_')

            if monitoringSampleCity == city.ID:
                nStretches = 1
                for path in city.paths:
                    for stretch in path.stretches:
                        if stretch.containsPoint(monitoringSample.coordinate):
                            detectedPoints.append(monitoringSample.coordinate)
                            stretch.monitoringData.append(monitoringSample)
                            print("    > Sample "+str(nSamples)+": "+monitoringSample.deviceID+"-"+monitoringSample.date+"-"+monitoringSample.time)
                            print("      - Stretch "+str(nStretches)+": "+stretch.ID)
                            break
                        else:
                            undetectedPoints.append(monitoringSample.coordinate)
                        nStretches+=1
            nSamples+=1
        #Export processed city data------------------------------------------------------------------
        exportCity(period, city)
        exportCityGraph(period, city.ID,city.getPathsPoints(), detectedPoints, undetectedPoints)
        nCities+=1

def exportCityGraph(period, cityID, cityPathsPoints, detectedPoints, undetectedPoints):
    for cityPathPoints in cityPathsPoints:
        x = list()
        y = list()
        for cityPathPoint in cityPathPoints:
            x.append(cityPathPoint[1])
            y.append(cityPathPoint[0])
        plt.plot(x, y, marker = 'o', color = 'black')

    for undetectedPoint in undetectedPoints:
        plt.plot(undetectedPoint[1], undetectedPoint[0], marker = 'o', color = 'red')

    for detectedPoint in detectedPoints:
        plt.plot(detectedPoint[1], detectedPoint[0], marker = 'o', color = 'green')

    fileName = "processorInput/citiesSamplesGraphs/"+cityID+"_"+period+".png"

    plt.legend(loc="upper left")
    plt.title(cityID+"_"+period)
    plt.xlabel('Longitude (°)')
    plt.ylabel('Latitude (°)')
    plt.grid()
    plt.savefig(fileName)
    plt.clf()

def exportCity(period, city):
    #File name
    fileName = "mapgeneratorInput/"+city.ID+"_"+period+".json"
    #File JSON data
    fileData = {}

    fileData['paths'] = list()
    for path in city.paths:

        pathStretches = list()
        for stretch in path.stretches:
            stretchMonitoringData = list()
            for sample in stretch.monitoringData:
                stretchMonitoringData.append({
                    'deviceID': sample.deviceID,
                    'date': sample.date,
                    'time': sample.time,
                    'coordinate': sample.coordinate,
                    'data': sample.data
                })
            #Insert stretch data in JSON
            pathStretches.append({
                'ID': stretch.ID,
                'P1': stretch.P1,
                'P2': stretch.P2,
                'monitoringData': stretchMonitoringData
            })
        #Insert path data in JSON
        fileData['paths'].append({
            'ID': path.ID,
            'constructionDate': path.constructionDate,
            'maintenanceDate': path.maintenanceDate,
            'inspectionDate': path.inspectionDate,
            'creator': path.creator,
            'stretches': pathStretches
        })

    with open(fileName, 'w') as outfile:
        json.dump(fileData, outfile, indent=2)

def importCity(cityFileName):
    #City file name
    fileName = "processorInput/BikePathGenerator/"+cityFileName
    #City object
    city = None

    with open(fileName) as infile:
        #Loads city JSON file
        cityData = json.load(infile)

        #Loads city info by JSON data
        city = City(cityFileName.replace(".json", ''))

        pathCount = 1
        for pathData in cityData['paths']:
            print("    > Path "+str(pathCount)+": "+pathData['ID'])
            print("      - Construction date: "+pathData['constructionDate'])
            print("      - Maintenance date: "+pathData['maintenanceDate'])
            print("      - Inspection date: "+pathData['inspectionDate'])
            print("      - Creator: "+str(pathData['creator']))

            #Loads path info by JSON data
            path = city.insertPath(pathData['ID'], pathData['constructionDate'], pathData['maintenanceDate'], pathData['inspectionDate'], pathData['creator'])
            stretchCount = 1
            #Loads stretch info by JSON data
            for stretchData in pathData['stretches']:
                print("      - Stretch "+str(stretchCount)+": "+stretchData['ID'])
                print("        . Points connection: "+str(stretchData['P1'])+" - "+str(stretchData['P2']))

                path.insertStretch(stretchData['ID'], stretchData['P1'], stretchData['P2'])
                stretchCount+=1
            pathCount+=1

    return city

def importMonitoringSample(monitoringSampleFileName):
    #Monitoring samples file name
    fileName = "processorInput/BikeSensor/"+monitoringSampleFileName
    #Monitoring samples list
    monitoringSamples = list()
    #Max of possible variables in monitoring system
    maxMonitoringData = 5
    #Identification sample data number
    nSampleIDdata = 3

    with open(fileName) as infile:
        sampleData = csv.reader(infile, delimiter='\t')
        #Variable code
        dataTypes = list()
        nSample = 1
        #Gets device ID and date from filename
        deviceID = monitoringSampleFileName[0:monitoringSampleFileName.find("_")]
        date = monitoringSampleFileName[(monitoringSampleFileName.find("_") + 1):len(monitoringSampleFileName)]
        date = date.replace(".csv", "")
        date = date.replace("-", "/")

        for sample in sampleData:
            #First read, variables codes
            if len(dataTypes) == 0:
                dataTypes = sample.copy()
                dataTypes = [int(type) for type in dataTypes]
                print("    > Variables types: "+str(dataTypes))
            #Samples data
            else:
                coordinate = [float(sample[1]), float(sample[2])]
                #Creates a data list with each variable on its position code
                auxData = sample[nSampleIDdata:maxMonitoringData+nSampleIDdata]
                data = [None]*maxMonitoringData
                dataPosition = 0
                for index in dataTypes:
                    data[int(index) - 1] = float(auxData[dataPosition])
                    dataPosition += 1

                print("    > Sample "+str(nSample)+": "+sample[0])
                print("      - Coordinate: "+str(coordinate))
                print("      - Data: "+str(data))
                monitoringSamples.append(MonitoringSample(deviceID, date, sample[0], coordinate, data))
                nSample += 1

    return monitoringSamples

if __name__ == "__main__":
    #GARANTIR A CAPTURA APENAS DOS DADOS NO PERÍODO CERTO
    main("27-04-2021")
