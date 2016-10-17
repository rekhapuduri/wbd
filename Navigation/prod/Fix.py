import datetime as dt
import time
import os
from xml.etree import ElementTree
import Angle as Angle
from math import *


class Fix():
    def __init__(self, logFile="log.txt"):
        """
        Constructor
        """
           
        self.body = ""
        self.dt = ""
        self.tm = ""
        self.observation = ""
        self.height = ""
        self.temperature = ""
        self.pressure = ""
        self.horizon = ""
        self.validate_filename(logFile, "Fix.__init__:  The file name violates the parameter specification.")
        self.txtFile = open(logFile, "a")
        try:
            self.logger("Start of log")

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
        s = ("LOG:\t" + curdate + "\t"+  s + "\n")
        self.txtFile.write(s)


    def validate_filename(self, fileName, errorMsg):
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
        self.validate_filename(actualFileName, "Fix.setSightingFile:  The file name violates the parameter specification.")
        
        file_str = "Start of sighting file\t" + actualFileName + ".xml"
        self.logger(file_str)
        self.sightingFile = actualFileName + ".xml"
        try:
            if os.path.exists(actualFileName + ".xml"):
                return actualFileName + ".xml"
            else:
                raise(ValueError("Fix.setSightingFile:  File not found"))
            f = open(self.sightingFile, "r")
            f.close()
        except:
            raise(ValueError("Fix.setSightingFile:  A file can not be opened"))

    def getSightings(self):
        """
        This method processes the given sighting file. 
        Writes the processed data into the logger file.
        """
        approximateLatitude = "0d0.0"
        approximateLongitude = "0d0.0"
        try:
            angleInstans = Angle.Angle()
            with open(self.sightingFile, 'rt') as f:
                tree = ElementTree.parse(self.sightingFile)
                for node1 in tree.iter('sighting'):
                    for node in node1.iter():
                        self.validateXml(node.tag, node.text,angleInstans)
                    self.processSighting(angleInstans)
                    cal_str = ( self.body + "\t" + self.dt + "\t" + self.tm + "\t" + angleInstans.getString() )
                    self.logger(cal_str)
                self.logger("End of sighting file:\t" + self.sightingFile)
                self.txtFile.close()
        except Exception as e:
            raise ValueError("Fix.getSightings:  No sighting file where found.")
        return (approximateLatitude, approximateLongitude)

    def processSighting(self, angleInstans):
        """
        This method processes the current sighting.
        
        params : angleInstans is an object of the Angle class.
        """
        dip = 0.0
        if self.horizon.strip() == "Natural":
            dip = (-0.97 * sqrt(float(self.height.strip()))) / 60.0
        celcius = (self.temperature - 32) * 5.0 / 9.0
        altitude = angleInstans.degrees + (angleInstans.minutes / 60) % 360
        refraction = -0.00452 * float(self.pressure.strip()) / float(273 + celcius) / tan(radians(altitude))
        adjustedAltitude = altitude + dip + refraction
        angleInstans.setDegrees(adjustedAltitude)


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
        elif tag == "height":
            if text == "":
                self.height == 0
            else:
                self.height = text
        elif tag == "temperature":
            if text == "":
                self.temperature = 72
            else:
                self.temperature = float(text)
        elif tag == "pressure":
            if text == "":
                self.pressure = 1010
            else :
                self.pressure = text
        elif tag == "horizon":
            if text == "":
                self.horizon == "Natural"
            else:
                self.horizon = text



if __name__ == "__main__":
    f = Fix()
    f.setSightingFile("sight.xml")
    f.getSightings()

