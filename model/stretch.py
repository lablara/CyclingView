from shapely.geometry import LineString as shls
from shapely.geometry import Point as shpt
import haversine as hs
from haversine import Unit

class Stretch:
    def __init__(self, ID, P1, P2):
        #String in 'Feira_de_Santana-BR-P1-S1' format
        self.ID = ID
        #Float array [0.0, 0.0]
        self.P1 = P1
        #Float array [0.0, 0.0]
        self.P2 = P2
        #All monitoring data detected on stretch
        self.monitoringData = list()

    def containsPoint(self, point):
        #Gets stretch line
        stretchLine = shls([self.P1, self.P2])
        #Gets distance between point and stretch line
        pointLineDistance = shpt(point).distance(stretchLine)

        #Checks if distance is short
        if pointLineDistance <  0.00010061046804398176:
            return True
        return False

    def getDistance(self, P1 = None, P2 = None):
        #Stretch distance
        if P1 == None or P2 == None:
            P1 = self.P1
            P2 = self.P2
        return int(hs.haversine(P1, P2, unit=Unit.METERS))

    def getHistoricalData(self, size):
        time = list()
        y0 = list()
        y1 = list()
        y2 = list()
        y3 = list()
        y4 = list()
        count = list()
        for index in range(size):
            if size != 24 and index == 0:
                None
            else:
                time.append(index)
                y0.append(0)
                y1.append(0)
                y2.append(0)
                y3.append(0)
                y4.append(0)
                count.append(0)

        for sample in self.monitoringData:
            timeIndex = int(sample.time[0:2])
            if size > 24:
                timeIndex = int(sample.date[0:2]) - 1
            elif size < 24:
                timeIndex = int(sample.date[3:5]) - 1

            y0[timeIndex] += sample.data[0]
            y1[timeIndex] += sample.data[1]
            y2[timeIndex] += sample.data[2]
            y3[timeIndex] += sample.data[3]
            y4[timeIndex] += sample.data[4]
            count[timeIndex] += 1

        for index in range(len(time)):
            if count[index] > 1:
                y0[index] = y0[index]/count[index]
                y1[index] = y1[index]/count[index]
                y2[index] = y2[index]/count[index]
                y3[index] = y3[index]/count[index]
                y4[index] = y4[index]/count[index]

        return time, y0, y1, y2, y3, y4
