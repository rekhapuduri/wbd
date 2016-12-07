import datetime as dt
import time
import os
from datetime import datetime
from xml.etree import ElementTree
import Angle as Angle
from math import *
from os.path import normpath, join
from os import path


class Fix():
    def __init__(self, logFile="log.txt"):
        # Initializes Fix object
        
        self.errMsg = ""
        self.er = 0
        self.body = ""
        self.dt = ""
        self.tm = ""
        self.observation = ""
        self.height = 0
        self.temperature = 0
        self.pressure = 0
        self.horizon = ""
        self.direction = ""
        self.assumedLatitudeObj = Angle.Angle()
        self.assumedLongitudeObj = Angle.Angle()
        self.assumedLatitude = 0.0
        self.assumedLongitude = 0.0
        self.assumedLatitudeStr = ""
        self.assumedLongitudeStr = ""
        self.distanceAdjustment = None
        self.azimuthAdjustmentStr = ""
        self.azimuthAdjustment = None
        self.validateFilename(logFile, ".txt", "Fix.__init__:  The file name violates the parameter specification.")
        self.txtFile = open(logFile, "a")
        
        try:
            self.logger("Log file\t" + normpath(join(os.getcwd(), logFile)))

        except Exception as eS:
            raise(ValueError("Fix.__init__:  Logfile can not be created or appended."))

    def logger(self,s):
        # Logs the entry to the log file with current date time in UTC format.
        
        now = dt.datetime.utcnow()
        utc = now.replace(tzinfo=dt.timezone.utc)
        local = utc.astimezone()
        local = local.replace(microsecond=0)
        curdate = local.isoformat(' ')
        s = ("LOG: " + curdate + " "+  s + "\n")
        self.txtFile.write(s)

    def validateFilename(self, fileName, extension, errorMsg):
        # Validates the filename and raises an error
        
        if not isinstance(fileName, str) or fileName.strip() == "":
            raise ValueError(errorMsg)

        if not fileName.endswith(extension):
            raise ValueError(errorMsg)
            
        if len(fileName) < 5:
            raise (ValueError(errorMsg))

    def setSightingFile(self, sightingFile):
        # Validates the name and sets the sighting file

        self.validateFilename(sightingFile, ".xml", "Fix.setSightingFile:  The file name violates the parameter specification.")
        
        file_str = "Sighting file\t" + normpath(join(os.getcwd(), sightingFile))
        self.logger(file_str)
        self.sightingFile = sightingFile
        try:
            f = open(self.sightingFile, "r")
            f.close()

            if os.path.exists(self.sightingFile):
                return normpath(join(os.getcwd(), self.sightingFile))
            else:
                raise(ValueError("Fix.setSightingFile:  File not found"))
        except:
            raise(ValueError("Fix.setSightingFile:  A file can not be opened"))

    def setAriesFile(self, ariesFile):
        # Validates the name and sets the aries file

        self.validateFilename(ariesFile, ".txt", "Fix.setAriesFile:  Invalid Filename")
        self.ariesFile = ariesFile

        try:
            f = open(self.ariesFile, "r")
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setAriesFile:  Aries file can not be opened"))

        file_str = "Aries file\t" + normpath(join(os.getcwd(), self.ariesFile))
        self.logger(file_str)
        return os.path.realpath(self.ariesFile)

    def setStarFile(self, starFile):
        # Validates the name and sets the star file
        
        self.validateFilename(starFile, ".txt", "Fix.setStarFile:  Invalid Filename")
        self.starFile = starFile
        
        try:
            f = open(self.starFile, "r")
            file_str = "Star file\t" + normpath(join(os.getcwd(), self.starFile))
            self.logger(file_str)
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setStarFile:  Stars file can not be opened for whatever reason"))

        return os.path.realpath(self.starFile)

    def getSightings(self, assumedLatitude="0d0.0", assumedLongitude="0d0.0"):
        # Performs calculations and loggings for each sighting
        
        if not self.sightingFile or not self.ariesFile or not self.starFile:
            raise ValueError("Fix.getSightings: ariesFile or sightingFile or starFile not exist.")

        if not isinstance(assumedLatitude, str):
            raise ValueError("Fix.getSightings: assumedLatitude is not valid.")

        if "S" in assumedLatitude:
            self.direction = "S"
            assumedLatitude = assumedLatitude.replace("S","")
            self.assumedLatitudeObj.setDegreesAndMinutes(assumedLatitude)
            self.assumedLatitude = -self.assumedLatitudeObj.getDegrees()

        elif "N" in assumedLatitude:
            self.direction = "N"
            assumedLatitude = assumedLatitude.replace("N", "")
            self.assumedLatitudeObj.setDegreesAndMinutes(assumedLatitude)
            self.assumedLatitude = self.assumedLatitudeObj.getDegrees()
        else:
            self.assumedLatitudeObj.setDegreesAndMinutes(assumedLatitude)
            self.assumedLatitude = self.assumedLatitudeObj.getDegrees()

        self.assumedLongitudeObj.setDegreesAndMinutes(assumedLongitude)
        self.assumedLongitude = self.assumedLongitudeObj.getDegrees()

        approximateLatitude = "0d0.0"
        approximateLongitude = "0d0.0"
        listOfDict = []
        try:
            altitudeObj = Angle.Angle()
            with open(self.sightingFile, 'rt') as f:
                tree = ElementTree.parse(self.sightingFile)
                self.tagFlag = False
                for node1 in tree.iter('sighting'):
                    dataDict = {}
                    for node in node1.iter():
                        try:
                            self.validateXml(node.tag, node.text,altitudeObj)
                        except:
                            self.er += 1
                            self.errMsg += "Some Mandatory field are Missing "
                            continue
                            
                    try:
                        self.processSighting(altitudeObj)
                    except Exception as e:
                        print(e)
                        self.errMsg += "Sighting File - Body or date not Match"
                        
                    try:
                        if (not self.tagFlag):
                            self.er += 1
                            continue
                    except:
                        self.er += 1

                    dataDict["body"] = self.body
                    dataDict["date"] = self.dt
                    dataDict["time"] = self.tm
                    dataDict["adjustedobservation"] = self.observation
                    dataDict["adjustedAltitude"] = altitudeObj.getString()
                    dataDict["latitude"] = self.latitude
                    dataDict["longitude"] = self.GHAobservation
                    dataDict["datetime"] = datetime.strptime(self.dt + " " + self.tm, "%Y-%m-%d %H:%M:%S")
                    dataDict["assumedLatitude"] = self.assumedLatitudeStr
                    dataDict["assumedLongitude"] = self.assumedLongitudeStr
                    dataDict["distanceAdj"] = self.distanceAdjustment
                    dataDict["azimuthAdj"] = self.azimuthAdjustment
                    dataDict["azimuthAdjStr"] = self.azimuthAdjustmentStr

                    listOfDict.append(dataDict)

            listOfDict.sort(key=lambda k: k['body'])
            listOfDict.sort(key=lambda k: k['datetime'])

            tempLatitude = 0.0
            tempLongitude = 0.0

            for dict in listOfDict:
                cal_str = (dict["body"] + "\t" + dict["date"] + "\t" + dict["time"] + "\t" + dict["adjustedAltitude"] + "\t" + dict["latitude"] + "\t" + dict["longitude"] +"\t" + dict['assumedLatitude'] + "\t" + dict['assumedLongitude'] + "\t" + dict['azimuthAdjStr'] + "\t" + str(dict['distanceAdj']))
                self.logger(cal_str)
                tempLatitude += (dict['distanceAdj'] * cos(radians(dict['azimuthAdj']))) / 60
                tempLongitude += (dict['distanceAdj'] * sin(radians(dict['azimuthAdj']))) / 60

            approximateLatitude = self.assumedLatitude + tempLatitude
            approximateLongitude = self.assumedLongitude + tempLongitude

            appLatObj = Angle.Angle()
            appLatObj.setDegrees(abs(approximateLatitude))
            approximateLatitudeStr = appLatObj.getString()
            if approximateLatitude < 0:
                approximateLatitudeStr = "S" + approximateLatitudeStr
            elif approximateLatitude > 0:
                approximateLatitudeStr = "N" + approximateLatitudeStr

            approximateLongitudeObj = Angle.Angle()
            approximateLongitudeObj.setDegrees(approximateLongitude)
            approximateLongitudeStr = approximateLongitudeObj.getString()

            self.logger("Sighting errors:" + "\t" + str(self.er))
            self.logger("Approximate latitude:\t" + approximateLatitudeStr + "\tApproximate longitude:\t" + approximateLongitudeStr)
            self.logger("End of sighting file " + self.sightingFile)

        except Exception as e:
            print (e)
            raise ValueError("Fix.getSightings:  Error while processing sightings")

        return (approximateLatitude, approximateLongitude)

    def processSighting(self, altitudeObj):
        # Process each sighting and performs related calculations
        
        dip = 0.0
        if self.horizon.strip() == "natural":
            dip = (-0.97 * sqrt(float(self.height))) / 60.0
        celcius = (self.temperature - 32) * 5.0 / 9.0
        altitude = altitudeObj.getDegrees()
        refraction = (-0.00452 * float(self.pressure)) / float(273 + celcius) / tan(radians(altitude))
        adjustedAltitude = altitude + dip + refraction
        adjustedAltitudeObj = Angle.Angle()
        adjustedAltitudeObj.setDegrees(adjustedAltitude)

        hh,mm,ss = self.tm.split(":")

        s = (int(mm) * 60) + int(ss)
        formatedDate = datetime.strptime(self.dt, '%Y-%m-%d').strftime('%m/%d/%y')

        angleObj = Angle.Angle()
        with open(self.starFile, 'r+') as starFile:
            # self.tagFlag = False
            for line in starFile:
                name = line.split("\t")[0]
                tempDt = line.split("\t")[1]

                if tempDt <= formatedDate and name == self.body:
                    self.SHAstar = angleObj.setDegreesAndMinutes(line.strip().split("\t")[2])
                    self.latitude = (line.split("\t")[3]).strip()
                    self.tagFlag = True

        GHAariesObj1 = Angle.Angle()
        GHAariesObj2 = Angle.Angle()

        with open(self.ariesFile, 'r+') as ariesFile:
            for line in ariesFile:
                fileDate = line.split("\t")[0]
                fileHour = line.split("\t")[1]

                hh = int(hh)
                fileHour = int(fileHour)
                if fileHour == hh and fileDate == formatedDate :
                    obj = line.strip().split("\t")[2]
                    self.GHAaries1 = GHAariesObj1.setDegreesAndMinutes(obj)
                    nextLine = next(ariesFile)
                    nextObservation = nextLine.strip().split("\t")[2]
                    self.GHAaries2 = GHAariesObj2.setDegreesAndMinutes(nextObservation)

        self.GHAaries = self.GHAaries1 + (self.GHAaries2 - self.GHAaries1) * (s / 3600)
        self.GHAobservation = self.GHAaries + self.SHAstar

        newAngleObj3 = Angle.Angle()
        newAngleObj3.setDegrees(self.GHAobservation)
        self.GHAobservation = newAngleObj3.getString()


        LHAObj = Angle.Angle()
        LHAObj.setDegreesAndMinutes(self.GHAobservation)
        LHAObj.add(self.assumedLongitudeObj)
        LHA = LHAObj.getDegrees()

        latitudeObj = Angle.Angle()
        latitudeObj.setDegreesAndMinutes(self.latitude)

        sinLatitude = sin(radians(latitudeObj.getDegrees())) * sin(radians(self.assumedLatitude))
        cosLatitude = cos(radians(latitudeObj.getDegrees())) * cos(radians(self.assumedLatitude)) * cos(radians(LHA))
        interDistance = sinLatitude + cosLatitude
        correctedAltitude = degrees(asin(interDistance))

        distanceAdjustment = int(round((correctedAltitude - adjustedAltitudeObj.getDegrees()) * 60, 0))
        self.distanceAdjustment = distanceAdjustment
        numerator = sin(radians(latitudeObj.getDegrees())) - sin(radians(self.assumedLatitude)) * interDistance
        denominator = cos(radians(self.assumedLatitude)) * cos(radians(correctedAltitude))
        interAzimuth = numerator / denominator
        azimuthAdjustment = degrees(acos(interAzimuth))
        azimuthAdjObj = Angle.Angle()
        azimuthAdjObj.setDegrees(abs(azimuthAdjustment))
        self.azimuthAdjustment = azimuthAdjObj.getDegrees()
        if azimuthAdjustment < 0 :
            self.azimuthAdjustmentStr = "-" + azimuthAdjObj.getString()
        else:
            self.azimuthAdjustmentStr = azimuthAdjObj.getString()

        if self.direction == "S":
            self.assumedLatitudeStr = self.direction + self.assumedLatitudeObj.getString()
        else:
            self.assumedLatitudeStr = self.assumedLatitudeObj.getString()

        self.assumedLongitudeStr = self.assumedLongitudeObj.getString()

    def validateXml(self, tag, text, angle):
        # Validates XML record for sighting
        
        if tag == "body":
            self.body = text
        elif tag == "date":
            self.dt = text
        elif tag == "time":
            self.tm = text
        elif tag == "observation":
            angle.setDegreesAndMinutes(text.strip())
            if angle.degrees < 0 or angle.degrees > 90:
                raise (ValueError("observation:  Degrees are invalid"))
            elif angle.minutes < 0 or angle.minutes > 60:
                raise (ValueError("observation:  Minutes are invalid"))
            else:
                self.observation = text

        try:
            if tag == "height":
                self.height = float(text)
        except:
            self.height = 0

        try:
            if tag == "temperature":
                self.temperature = float(text)
        except:
            self.temperature = 72

        try:
            if tag == "pressure" :
                self.pressure = float(text)
        except:
            self.pressure = 1010

        try:
            if tag == "horizon" :
                self.horizon = text
        except:
            self.horizon = "Natural"

if __name__ == "__main__":
    fix = Fix()
    #     fix.setSightingFile("sightings1.xml")
    fix.setSightingFile("sightings2.xml")
    fix.setAriesFile("aries.txt")
    fix.setStarFile("stars.txt")
    #     fix.getSightings("N27d59.5", "85d33.4") # for sightings1.xml
    fix.getSightings("S53d38.4", "74d35.3")  # for sightings2.xml
