import math
import re


class Angle:

    def __init__(self):
        """
        Constructor.
        """
        self.degrees = 0
        self.minutes = 0

    def setDegrees(self, degrees=0):
        """
        This method receives degrees as integer or float. Received degrees is 
        divided and set as degrees and minutes.

        params: degrees as integer or float. Defaults to zero.

        returns: degrees and minutes
        """

        try:
            deg = float(degrees)
            values = divmod(deg, 1)
            
            self.degrees = values[0]
            self.minutes = values[1] * 60

            return self.getDegrees()

        except Exception as e:
            raise ValueError("Angle.setDegrees:  Invalid degrees.")

    def setDegreesAndMinutes(self, angleString):
        """This method receives angleString. angleString must contain "d" 
        separator between degrees and minutes. This method validates the string 
        part using regular expression and sets degrees and minutes.

        params: angleSting as string

        returns: degrees and minutes
        """

        try:
            pattern = '^(\-?\d+)d(\d+(.\d)?)$'
            match = re.match(pattern, angleString)

            if match:
                angleString = angleString.split("d")
                self.degrees = int(match.group(1))
                self.minutes = float(match.group(2)) % 60
                
                return self.getDegrees()
            else:
                raise ValueError("Angle.setDegreesAndMinutes:  Invalid angleString.")
        except Exception as e:
            raise ValueError("Angle.setDegreesAndMinutes:  Invalid angleString.")

    def add(self, angle):
        """This method receives angle which must be an instance of Angle class 
        and adds degrees and minutes from received angle to current object.

        params: angle as Angle

        returns: degrees and minutes
        """
        
        try:
            if isinstance(angle, Angle):
                self.degrees = self.degrees + self.getObjDeg(angle)
                self.minutes = self.minutes + self.getObjMin(angle)
                return self.getDegrees()
            else:
                raise ValueError("Angle.add:  Invalid angle object.")
        except Exception as e:
            raise ValueError("Angle.add:  Invalid angle object.")

    def subtract(self, angle):
        """This method receives angle which must be an instance of Angle class 
        and subtracts degrees and minutes of received angle from current object.

        params: angle as Angle

        returns: degrees and minutes
        """

        try:
            if isinstance(angle, Angle):
                self.degrees = self.degrees - self.getObjDeg(angle)
                self.minutes = self.minutes - self.getObjMin(angle)
                return self.getDegrees()
            else:
                raise ValueError("Angle.subtract:  Invalid angle object.")
        except Exception as e:
            raise ValueError("Angle.subtract:  Invalid angle object.")

    def compare(self, angle):
        """This method receives angle which must be an instance of Angle class 
        and compares degrees and minutes of received angle with degrees and 
        minutes of current object.

        params: angle as Angle

        returns: int (-1 or 0 or 1)
        """

        try:
            if isinstance(angle, Angle):
                deg = self.getDegrees()
                angleDeg = angle.getDegrees()

                if deg < angleDeg:
                    return -1
                elif deg == angleDeg:
                    return 0
                else:
                    return 1
            else:
                raise ValueError("Angle.compare:  Invalid angle object.")
        except Exception as e:
            raise ValueError("Angle.compare:  Invalid angle object.")

    def getString(self):
        """This method converts and returns degrees and minutes to string.

        returns: formated string
        """

        return ("{0}{1}{2}".format(int(self.degrees % 360), "d", round(self.minutes, 1)))

    def getDegrees(self):
        """This method returns degrees and minutes as a floating point number.

        returns: degrees and number as a floating point number
        """

        return (self.degrees + (round(self.minutes / 60, 1))) % 360

    def getObjDeg(self, angle):
        """This method receives angle which must be an instance of Angle class 
        and returns degrees part.

        params: angle as Angle

        returns: degrees integer
        """

        try:
            if isinstance(angle, Angle):
                values = angle.getString()
                values = values.split("d")
                return int(values[0])
            else:
                raise ValueError("Angle.getObjDeg:  Invalid angle object.")
        except Exception as e:
            raise ValueError("Angle.getObjDeg:  Invalid angle object.")

    def getObjMin(self, angle):
        """This method receives angle which must be an instance of Angle class 
        and returns minutes part.

        params: angle as Angle

        returns: minutes floating point number
        """

        try:
            if isinstance(angle, Angle):
                values = angle.getString()
                values = values.split("d")
                return float(values[1])
            else:
                raise ValueError("Angle.getObjMin:  Invalid angle object.")
        except Exception as e:
            raise ValueError("Angle.getObjMin:  Invalid angle object.")
