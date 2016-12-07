import math

class Angle():

    def __init__(self):
        # Initializes Angle object
        
        self.degrees = 0.0
        self.minutes = 0.0
        self.negative = False

    def setDegrees(self, degrees=0.0):
        # Sets the degrees and minutes based on received degrees numeric value
        
        x = 0
        try:
            degrees = float(degrees)
            frac, whole = math.modf(degrees)
            x = float((whole % 360) + frac) % 360
            frac, whole = math.modf(x)
            self.degrees = whole
            self.minutes = frac
        except Exception as e:
            try:
                degrees = int(degrees)
                x = float(degrees)
                self.degrees = degrees % 360
                self.minutes = 0
            except Exception as e:
                raise ValueError("Angle.setDegrees:  Invalid degrees.")

        return x
        
    def setDegreesAndMinutes(self, angleString):
        # Sets the degrees and minutes based on received angleString parameter
        # It splits string with separator "d" and validates the string
        
        self.negative = False
        
        # blank and "d"
        if angleString == "" or "d" not in angleString:
            raise ValueError("Angle.setDegreesAndMinutes:  angleString is invalid.")

        temp = angleString.split("d")

        # two parts, no decimal point in degree, no negative minutes
        if (len(temp) != 2) or ("." in temp[0]) or ("-" in temp[1]):
            raise ValueError("Angle.setDegreesAndMinutes:  angleString is invalid.")

        degrees = 0
        minutes = 0.0
        # Valid degrees and minutes
        try:
            degrees = int(temp[0])
            minutes = float(temp[1])
        except Exception as e:
            raise ValueError("Angle.setDegreesAndMinutes:  angleString is invalid.")

        # point and only single degit after point in minutes
        # if len(temp[1].split(".")[1]) > 1:
        if len(str(minutes).split(".")[1]) > 1:
            raise ValueError("Angle.setDegreesAndMinutes:  angleString is invalid.")

        if degrees < 0:
            self.negative = True
            degrees = 360 - degrees - (int(minutes % 60) if minutes > 60 else 0)

        self.degrees = (degrees + (int(minutes % 60) if minutes > 60 else 0)) % 360
        self.minutes = (minutes % 60) / 60

        x = float(self.degrees + self.minutes)
        return x if not self.negative else 360 - x

    def add(self, angle=None):
        # Adds parameters of received angle to current angle
        
        # a valid angle
        if not isinstance(angle, Angle):
            raise ValueError("Angle.add:  received angle is invalid.")

        xReceived = float(angle.degrees + angle.minutes)
        x = float(self.degrees + self.minutes)

        data = ((x - xReceived) if angle.negative else (x + xReceived)) % 360
        
        self.degrees, self.minutes = math.modf(data)
        self.negative = False

        return data

    def subtract(self, angle=None):
        # Subtracts parameters of received angle from current angle

        # a valid angle
        if not isinstance (angle, Angle):
            raise ValueError("Angle.subtract:  received angle is invalid.")

        xReceived = float(angle.degrees + angle.minutes)
        x = float(self.degrees + self.minutes)

        data = ((x + xReceived) if angle.negative else (x - xReceived)) % 360
        
        self.degrees, self.minutes = math.modf(data)
        self.negative = False

        return data

    def compare(self, angle=None):
        # Compares received angle object this angle object.
        
        # a valid angle
        if not isinstance (angle, Angle):
            raise ValueError("Angle.compare:  received angle is invalid.")

        xReceived = angle.getDegrees()
        x = self.getDegrees()
        
        return 1 if x > xReceived else -1 if x < xReceived else 0
            
    def getString(self):
        # Returns the degrees and minutes as a string
        return str(int(self.degrees)) + "d" + str(round(self.minutes * 60, 1))

    def getDegrees(self):
        # Returns the degrees and minutes as a float

        x = float(self.degrees + round(self.minutes * 60.0, 1) / 60.0) % 360
        return x if not self.negative else 360 - x
        