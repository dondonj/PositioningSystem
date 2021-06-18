from flask import Flask
from flask import request, session
import json, datetime

from server.model import AccessPoint, Location, Sample, FingerprintValue, CalibratingMobile
from server.databaseMethods import Database

from sqlalchemy.sql.expression import false

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
                sample = Sample(ap_id=database.get_ap_id(ap),source_address=key, timestamp=123,rssi=float(parameters[key]),ap=database.get_ap(ap.mac_address))
                database.add_to_database(sample)


        startCalibration = session.get("startCalibration",None)

        # startCalibration=False
        #Calibration part
        if startCalibration:
            mac_addr = session.get("mac_addr", None)
            if source_address == mac_addr:

                #Fetch the loc.id of the mac_addr in the CalibratingMobile table
                for loc in session_.query(CalibratingMobile).order_by(CalibratingMobile.mac_address):
                    if loc.mac_address == mac_addr:
                        location = loc.loc_id

                #Create a fingerprint
                fingerprint = FingerprintValue(loc_id=location , ap_id=ap_id.id, rssi=rssi)
                session_.add(fingerprint)

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

        #Fill callibrating_mobile table
        location = Location(x=x, y=y, z=z)

        cal_mobile = CalibratingMobile(mac_address=mac_addr, loc_id=location.id)
        session_.add(cal_mobile)

        sampleList=[]
        for instance in session_.query(Sample).order_by(Sample.source_address):
            if instance.source_address == mac_addr and instance.timestamp >= time.time()-1:
                
                #Share start calibration variable
                if startCalibration == false:
                    startCalibration=True
                    session["startCalibration"]=startCalibration 

                #Fill list of samples
                sampleList.add(instance)
        
        if len(sampleList)>0:
            for sample in sampleList:
                fingerprint = FingerprintValue(loc_id = location.id, ap_id = sample.ap_id, rssi=sample.rssi)
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

        startCalibration=False
        session["startCalibration"]=startCalibration

        #Delete any calibrating_mobile entry whose mac_address equal parameter mac_addr
        for instance in session_.query(CalibratingMobile).order_by(CalibratingMobile.mac_address):
            if instance.mac_address == mac_addr:
                session_.delete(instance)
        
        #Commit and close
        session_.commit()
        session_.close()
        
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

    else:
        #If request.method is equal to 'GET', fetch and return locations
        json_response = {"locations":[]}
        print("\n Location table \n")
        print("Id" +space+"X value" +space+"Y value"+space+"Z value\n")
        for instance in session_.query(Location).order_by(Location.id):
            location = {
                        "id":instance.id,
                        "x":instance.x,
                        "y":instance.y,
                        "z":instance.z
                        }
            json_response["locations"].append(location)
            print(instance.id,space, instance.x,space, instance.y,space, instance.z)
        
        json_response = json.dumps(json_response, indent=4)
        
        return json_response
