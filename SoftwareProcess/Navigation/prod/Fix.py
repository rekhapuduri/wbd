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
        """
        Constructor
        """
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
        self.validateFilename(logFile, "Fix.__init__:  The file name violates the parameter specification.")
        self.txtFile = open(logFile, "a")
        try:
            self.logger("Log file\t" + normpath(join(os.getcwd(), logFile)))

        except Exception as eS:
            raise(ValueError("Fix.__init__:  Logfile can not be created or appended."))

    def logger(self,s):
        """
        This method receives str as string or float. Received string is 
        is written in log file.

        params: str as string
        """
        now = dt.datetime.utcnow()
        utc = now.replace(tzinfo=dt.timezone.utc)
        local = utc.astimezone()
        local = local.replace(microsecond=0)
        curdate = local.isoformat(' ')
        s = ("LOG: " + curdate + " "+  s + "\n")
        self.txtFile.write(s)

    def validateFilename(self, fileName, errorMsg):
        """
        This method validates the given fileName for its fileName length.
        
        params:
            fileName is the name of file to validate
            errorMsg is the error message 
        
        """
        if len(fileName) < 1:
            raise (ValueError(errorMsg))

    def setSightingFile(self, sightingFile):
        """
        This method sets the received file as the sighting file.
        
        params: sightingFile as string it is the name of the xml file
        
        returns: The name of sighting file 
        """
        actualFileName = sightingFile.split(".")[0]
        self.validateFilename(actualFileName, "Fix.setSightingFile:  The file name violates the parameter specification.")
        
        file_str = "Sighting file\t" + normpath(join(os.getcwd(), sightingFile))
        self.logger(file_str)
        self.sightingFile = actualFileName + ".xml"
        try:
            f = open(self.sightingFile, "r")
            f.close()

            if os.path.exists(actualFileName + ".xml"):
                return normpath(join(os.getcwd(), self.sightingFile))
            else:
                raise(ValueError("Fix.setSightingFile:  File not found"))
        except:
            raise(ValueError("Fix.setSightingFile:  A file can not be opened"))

    def setAriesFile(self, ariesFile):
        """ setAriesFile method receive text file as parameter. split it with '.' and validate file name.
            write in log.txt file that filename and full path of aries file  with current datetime.

            Parameters:
                ariesFile: aries data file.

            Returns:
                A string having the value passed as the ariesFile's full path.
            """
        fileName = ariesFile.split(".")[0]

        if (len(fileName)) < 1:
            raise (ValueError("Fix.setAriesFile:  Invalid Filename"))

        self.ariesFile = fileName + ".txt"

        try:
            f = open(self.ariesFile, "r")
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setAriesFile:  Aries file can not be opened for whatever reason"))

        file_str = "Aries file\t" + normpath(join(os.getcwd(), self.ariesFile))
        self.logger(file_str)
        return os.path.realpath(self.ariesFile)

    def setStarFile(self, starFile):
        """ Get star file from parameter.First we check filename without extension. If filename less than 1
            that raise value error "Invalid Filename".
            If filename valid than set file as global. We get full path of stars file using normpath.
            Make a string including filename, file path and  current date time.
            Write string in log.open file read mode for check that file is exist or not.

            Parameters:
                starFile: stars text file.

            Returns:
                A string having the value of the starsFile's full path.
            """
        fileName = starFile.split(".")[0]

        if (len(fileName)) < 1:
            raise (ValueError("Fix.setStarFile:  Invalid Filename"))

        self.starFile = fileName + ".txt"
        
        try:
            f = open(self.starFile, "r")
            file_str = "Star file\t" + normpath(join(os.getcwd(), self.starFile))
            self.logger(file_str)
            f.close()
        except Exception as e:
            raise (ValueError("Fix.setStarFile:  Stars file can not be opened for whatever reason"))

        return os.path.realpath(self.starFile)

    def getSightings(self):
        """
        This method processes the given sighting file. 
        Writes the processed data into the logger file.
        """
        approximateLatitude = "0d0.0"
        approximateLongitude = "0d0.0"
        listOfDict = []
        try:
            angleInstans = Angle.Angle()
            with open(self.sightingFile, 'rt') as f:
                tree = ElementTree.parse(self.sightingFile)
                self.tagFlag = False
                for node1 in tree.iter('sighting'):
                    dataDict = {}
                    for node in node1.iter():
                        try:
                            self.validateXml(node.tag, node.text,angleInstans)
                        except:
                            self.er += 1
                            self.errMsg += "Some Mandatory field are Missing "
                            continue
                    try:
                        self.processSighting(angleInstans)

                    except:
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
                    dataDict["adjustedAltitude"] = angleInstans.getString()
                    dataDict["latitude"] = self.latitude
                    dataDict["longitude"] = self.GHAobservation
                    dataDict["datetime"] = datetime.strptime(self.dt + " " + self.tm, "%Y-%m-%d %H:%M:%S")

                    listOfDict.append(dataDict)

            listOfDict.sort(key=lambda k: k['body'])
            listOfDict.sort(key=lambda k: k['datetime'])

            for dict in listOfDict:
                cal_str = (dict["body"] + "\t" + dict["date"] + "\t" + dict["time"] + "\t" + dict["adjustedAltitude"] + "\t" + dict["latitude"] + "\t" + dict["longitude"])
                self.logger(cal_str)

        except Exception as e:
            raise ValueError("Fix.getSightings:  No sighting file where found.")
        finally:
            self.logger("Sightings errors:\t" + str(self.er))
            self.txtFile.close()
            print(self.errMsg)

        return (approximateLatitude, approximateLongitude)

    def processSighting(self, angleInstans):
        """
        This method processes the current sighting.calculate adjusted altitude, latitude and longitude.        
        params : angleInstans is an object of the Angle class.
        """
        dip = 0.0
        if self.horizon.strip() == "Natural":
            dip = (-0.97 * sqrt(float(self.height))) / 60.0
        celcius = (self.temperature - 32) * 5.0 / 9.0
        altitude = angleInstans.degrees + (angleInstans.minutes / 60) % 360
        refraction = -0.00452 * float(self.pressure) / float(273 + celcius) / tan(radians(altitude))
        adjustedAltitude = altitude + dip + refraction
        angleInstans.setDegrees(adjustedAltitude)

        hh,mm,ss = self.tm.split(":")

        s = (int(mm) * 60) + int(ss)
        formatedDate = datetime.strptime(self.dt, '%Y-%m-%d').strftime('%m/%d/%y')

        angleObj = Angle.Angle()
        with open(self.starFile, 'r+') as starFile:
            # self.tagFlag = False
            for line in starFile:
                name = line.split("\t")[0]
                tempDt = line.split("\t")[1]

                if tempDt == formatedDate and name == self.body:
                    self.SHAstar = angleObj.setDegreesAndMinutes(line.split("\t")[2])
                    self.latitude = (line.split("\t")[3]).strip()
                    self.tagFlag = True


        newAngleObj1 = Angle.Angle()
        newAngleObj2 = Angle.Angle()

        with open(self.ariesFile, 'r+') as ariesFile:
            for line in ariesFile:
                fileDate = line.split("\t")[0]
                fileHour = line.split("\t")[1]

                hh = int(hh)
                fileHour = int(fileHour)
                if fileHour == hh and fileDate == formatedDate :
                    obj = line.split("\t")[2]
                    self.GHAaries1 = newAngleObj1.setDegreesAndMinutes(obj)
                    nextLine = next(ariesFile)
                    nextObservation = nextLine.split("\t")[2]
                    self.GHAaries2 = newAngleObj2.setDegreesAndMinutes(nextObservation)

        self.GHAaries = self.GHAaries1 + (self.GHAaries2 - self.GHAaries1) * (s / 3600)
        self.GHAobservation = self.GHAaries + self.SHAstar

        newAngleObj3 = Angle.Angle()
        newAngleObj3.setDegrees(self.GHAobservation)
        self.GHAobservation = newAngleObj3.getString()

    def validateXml(self,tag,text,angle):
        """
        This method validates the given tag and its value based on validation condition.
        
        params: 
            tag:    tag is string of tag name
            text:   text is the string of tag's value
            angle:  angle is the instance of Tag class
        """
        if tag == "body":
            self.body = text
        elif tag == "date":
            self.dt = text
        elif tag == "time":
            self.tm = text
        elif tag == "observation":
            angle.setDegreesAndMinutes(text)
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
    fix.setSightingFile("sight.xml")
    fix.setAriesFile("aries.txt")
    fix.setStarFile("stars.txt")
    fix.getSightings()

