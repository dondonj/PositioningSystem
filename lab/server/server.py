from flask import Flask
from flask import request, session

import json
from math import sqrt
from datetime import datetime

from server.model import AccessPoint, Location, Sample, FingerprintValue, CalibratingMobile
from server.databaseMethods import Database


SECRET_KEY = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

app = Flask(__name__)
app.config['SECRET_KEY']= SECRET_KEY

database=Database()

space = "    |    "



@app.route("/rssi", methods=['GET', 'POST'])
def rssi():
    """
	ToDO: Implement this function
	It receives data from the access points on the path /rssi
	with a parameter ap whose value is the sending AP MAC address
	and a series of pairs XX:XX:XX:XX:XX:XX=-YY.YYYY
	where the X's ModuleNotFoundError: No module named 'server.models'; 'server' is not a packageare the measured devices MAC addresses
		  and the Y's are the avg RSSI values for the corresponding
		  MAC address over the last second
	You have to put these information in the sqlite3 database
	named rssi.db whose schema can be displayed from the sqlite3
	prompt through the command .schema
	SQL Alchemy ORM classes and initialization are available above
	"""

    if request.method == 'POST':
        parameters = request.args.to_dict()
        #Check parameters
        if not parameters['ap']:
                return "No Access point parameters"
        for param in parameters:
            if param != 'ap':
                #Check the source_adress
                if not param:
                    return "No source adress parameters"
                #Check rssi values
                if not parameters[param]:
                    return "No rssi parameters"

        print(parameters)
        #Create an access point
        ap = AccessPoint(mac_address=parameters['ap'])

        #Create a Sample for each pairs of mac_address and rssi
        for key in parameters:
            #Look at the pairs (not the access point value)
            if key != 'ap':
            #If the ap does not exist in the database, create it
                if not database.get_ap(ap.mac_address):
                    database.add_to_database(ap)

                #Create and add the sample to the database using pairs
                sample = Sample(ap_id=database.get_ap_id(ap),source_address=key, timestamp=datetime.now().strftime("%H:%M:%S"),rssi=float(parameters[key]),ap=database.get_ap(ap.mac_address))
                database.add_to_database(sample)


        #Commit and close   
        return "\n\rPOST ok\n"
    else:
        #If request.method is equal to 'GET', fetch and return samples and access points in the database
        json_response = {"samples":[],"access points":[]}

        #Return all samples
        for instance in database.get_sample_all():
            sample = {
                        "source adress":instance.source_address,
                        "access point id":instance.ap_id,
                        "timestamp":instance.timestamp,
                        "rssi":instance.rssi
                    }
            json_response["samples"].append(sample)
        
        #Return all access_points
        for instance in database.get_ap_all():
            access_point = {
                        "id":instance.id,
                        "mac address":instance.mac_address,
                        }
            json_response["access points"].append(access_point)
        
        
        json_response = json.dumps(json_response, indent=4)
        
        return json_response



@app.route("/start_calibration", methods=['GET', 'POST'])
def start_calibration():
    """
        ToDO: implement this function
        It receives 4 parameters: mac_addr (string), x (float), y (float), and z (float)
        then must trigger 3 tasks:
        (1) Add MAC address and location to table calibrating_mobile
        (2) Find all samples in table sample, and whose source address matches mac_addr
            and whose timestamp is less than 1 second in the past.
            With those samples, insert into table fingerprint_value all entries with
            ap_id matching the AP that forwared the RSSI sample, location the device location
            and RSSI the RSSI from table sample
        (3) In /rssi route: add instructions that process all incoming RSSI samples like
            step (2) when received.
    """
    if request.method == 'POST':
        mac_addr = request.args.get('mac_addr')
        session["mac_addr"] = mac_addr              #Share mac address between routes
        x = request.args.get('x')
        y = request.args.get('y')
        z = request.args.get('z')

        #Check parameters
        if not mac_addr:
            return "No mac address parameters provided"
        if not x:
            return "No x parameters provided"
        if not y:
            return "No y parameters provided"
        if not z:
            return "No z parameters prodided"
        
        #Convert data into the right type
        mac_addr = str(mac_addr)
        x = float(x)
        y = float(y)
        z = float(z)

        #Make and add the location instance to the database
        location = Location(x=x, y=y, z=z)
        if not database.exist_loc(location):
            print("add location §§§§§§!§§§§!!!!")
            database.add_to_database(location)
        print("LOCATION ????")
        #Make and add the calibrating mobile instance to the database
        cal_mobile = CalibratingMobile(mac_address=mac_addr, loc_id=database.get_loc_id(loc=location))
        if not database.exist_calib(cal_mobile):
            print(database.exist_calib(cal_mobile))
            database.add_to_database(cal_mobile)
        
        #Get all matching samples (all samples that match the mac_addr and which are less that 1s old)
        sampleMatchingList=database.get_matching_samples(mac_addr)
        for sample in sampleMatchingList:
            fingerprint = FingerprintValue(loc_id = database.get_loc_id(loc=location), ap_id = sample.ap_id, rssi=sample.rssi, location=location, ap=sample.ap)

            if not database.exist_fingerprint(fingerprint):
                database.add_to_database(fingerprint)

        return "\n\rPOST ok\n"

    else:
        #If request.method is equal to 'GET', fetch and return locations, calibrating mobiles and fingerprints in the database
        json_response = {"locations":[],"calibrating mobiles":[],"fingerprints":[]}

        #Return all locations
        for instance in database.get_location_all():
            location = {
                        "id":instance.id,
                        "x":instance.x,
                        "y":instance.y,
                        "z":instance.z
                        }
            json_response["locations"].append(location)

        #Return all calibration
        for instance in database.get_calibrating_all():
            calibrating = {
                            "mac_address":instance.mac_address,
                            "location id":instance.loc_id
                            }
            json_response["calibrating mobiles"].append(calibrating)
        
        #Return all fingerprint
        for instance in database.get_fingerprint_all():
            fingerprint = {
                        "id":instance.id,
                        "location id":instance.loc_id,
                        "access point id":instance.ap_id,
                        "rssi":instance.rssi
                        }
            json_response["fingerprints"].append(fingerprint)
        
        json_response = json.dumps(json_response, indent=4)
        
        return json_response


@app.route("/stop_calibration", methods=['GET', 'POST'])
def stop_calibration():
    """
        TODO: implement this function
        It receives one parameter: mac_addr (string)
        It must delete any calibrating_mobile entry whose mac_address equal parameter mac_addr
    """

    if request.method == 'POST':

        #Fetch data
        mac_addr = request.args.get('mac_addr')

        #Check if data are given
        if not mac_addr:
            return "No mac address provided"
        
        #Convert data into the right type
        mac_addr = str(mac_addr)


        #Delete any calibrating_mobile entry whose mac_address equal parameter mac_addr
        database.del_calibrating_all(mac_addr)
 
        return "\n\rPOST ok No content\n"

    else:
        #If request.method is equal to 'GET', fetch and return locations, calibrating mobiles and fingerprints in the database
        json_response = {"locations":[],"calibrating mobiles":[],"fingerprints":[]}

        #Return all locations
        for instance in database.get_location_all():
            location = {
                        "id":instance.id,
                        "x":instance.x,
                        "y":instance.y,
                        "z":instance.z
                        }
            json_response["locations"].append(location)

        #Return all calibration
        for instance in database.get_calibrating_all():
            calibrating = {
                            "mac_address":instance.mac_address,
                            "location id":instance.loc_id
                            }
            json_response["calibrating mobiles"].append(calibrating)
        
        #Return all fingerprint
        for instance in database.get_fingerprint_all():
            fingerprint = {
                        "id":instance.id,
                        "location id":instance.loc_id,
                        "access point id":instance.ap_id,
                        "rssi":instance.rssi
                        }
            json_response["fingerprints"].append(fingerprint)
        
        json_response = json.dumps(json_response, indent=4)
        
        return json_response


@app.route("/locate", methods=['GET', 'POST'])
def locate():
    """
        ToDO: implement this function
        It receives one parameter: mac_addr (string)
        Must locate the device based on samples less than 1 second old, whose source address equals mac_addr
        These samples are compared to the content of fingerprint_value table
        Use the closest in RSSI algorithm to find a fingerprint sample matching current sample and return its location
    """

    if request.method == 'POST':
        
        #Fetch data
        mac_addr = request.args.get('mac_addr')

        #Check if data are given
        if not mac_addr:
            return "No mac address provided"
        
        #Convert data into the right type
        mac_addr = str(mac_addr)

        # Get all matching samples from the database
        matching_samples = database.get_matching_samples(mac_addr)
        # Get all fingerprint values from the database
        reference_points = database.get_all_fp()

        d_min = 200 #Random value (not too high and not too low, reasonable)
        location = Location() #Initialise an empty location
        # Iterate through all the fingerprinting values to find the minimum distance 
        for point in reference_points:
            distance = rssi_distance(point, matching_samples) # Compute distance between the tested point and the mobile device
            if distance < d_min:
                d_min = distance
                location = point.location

        return location

    else:
        #If request.method is equal to 'GET', fetch and return locations
        json_response = {"locations":[]}

        for instance in database.get_location_all():
            location = {
                        "id":instance.id,
                        "x":instance.x,
                        "y":instance.y,
                        "z":instance.z
                        }
            json_response["locations"].append(location)
        
        json_response = json.dumps(json_response, indent=4)
        
        return json_response


def rssi_distance(point, samples):
        """
        Compute distances between a fingerprinting value and a list of samples
        Taken from td's lessons
        """
        count = 0
        qsum = 0.0
        for sample in samples:
            i = sample.ap_id
            if i != -1:
                count += 1
                qsum += (sample.rssi - point.rssi)**2
        qsum += (95**2) * (1 + len(samples) - 2*count)
        return sqrt(qsum)
