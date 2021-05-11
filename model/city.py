from path import Path

class City:
    def __init__(self, ID):
        #String in 'Feira_de_Santana-BR' format
        self.ID = ID
        #City bike paths list
        self.paths = list()

    def insertPath(self, ID, constructionDate, maintenanceDate, inspectionDate, creator):
        #Create new bike path object
        path = Path(ID, constructionDate, maintenanceDate, inspectionDate, creator)
        #Add in paths list
        self.paths.append(path)
        return path

    def getPathsPoints(self):
        pathsPoints = list()
        for path in self.paths:
            stretchPoints = list()
            for stretch in path.stretches:
                stretchPoints.append(stretch.P1)
            stretchPoints.append(stretch.P2)
            pathsPoints.append(stretchPoints)
        return pathsPoints
