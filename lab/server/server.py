from flask import Flask
from flask import request, session

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import time

from sqlalchemy.sql.expression import false

SECRET_KEY = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

app = Flask(__name__)
app.config['SECRET_KEY']= SECRET_KEY

engine = create_engine('sqlite:///server/rssi.db', echo=True)
base = declarative_base()
base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session_ = Session()

# startCalibration=False
# session["startCalibration"]=startCalibration

class AccessPoint(base):
    __tablename__ = "accesspoint"
    id = Column(Integer, primary_key=True)
    mac_address = Column(String)

class Location(base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

class Sample(base):
    __tablename__ = "sample"
    ap_id = Column(Integer, ForeignKey("accesspoint.id"))
    source_address = Column(String, nullable=False, primary_key=True)
    timestamp = Column(Float, nullable=False, primary_key=True)
    rssi = Column(Float, nullable=False)
    ap = relationship("AccessPoint", backref="sample")

    def values(self, src, t, _rssi, _ap):
        source_address = src
        timestamp = t
        rssi = _rssi
        ap = _ap

class FingerprintValue(base):
    __tablename__ = "fingerprint_value"
    id = Column(Integer, primary_key=True)
    loc_id = Column(Integer, ForeignKey("location.id"))
    ap_id = Column(Integer, ForeignKey("accesspoint.id"))
    rssi = Column(Float, nullable=False)
    location = relationship("Location", backref="fingerprint_value")
    ap = relationship("AccessPoint", backref="fingerprint_value")

class CalibratingMobile(base):
    __tablename__ = "calibrating_mobile"
    mac_address = Column(String, primary_key=True)
    loc_id = Column(Integer, ForeignKey("location.id"))
    location = relationship("Location", backref="calibrating_mobile")

@app.route("/rssi", methods=['GET', 'POST'])
def rssi():
    """
	ToDO: Implement this function
	It receives data from the access points on the path /rssi
	with a parameter ap whose value is the sending AP MAC address
	and a series of pairs XX:XX:XX:XX:XX:XX=-YY.YYYY
	where the X's are the measured devices MAC addresses
		  and the Y's are the avg RSSI values for the corresponding
		  MAC address over the last second
	You have to put these information in the sqlite3 database
	named rssi.db whose schema can be displayed from the sqlite3
	prompt through the command .schema
	SQL Alchemy ORM classes and initialization are available above
	"""

    if request.method == 'POST':
        ap = request.args.get('ap')
        source_address = request.args.get('source_address')
        rssi = request.args.get('rssi')

        #Check parameters
        if not ap:
            return "No Access point parameters"
        if not source_address:
            return "No source adress parameters"
        if not rssi:
            return "No rssi parameters"
        
        #Convert data into the right type
        ap = str(ap)
        source_address = str(source_address)
        rssi = float(rssi)

        #Create an access point
        ap_id = AccessPoint(mac_address=ap)
        session_.add(ap_id)
        session_.flush()

        #Create a Sample
        rssi_avrg = Sample(ap_id=ap_id.id,source_address=source_address , timestamp=time.time(),rssi=rssi)

        
        session_.add(rssi_avrg)

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
        session_.commit()
        session_.close()
        return "\n\rPOST ok\n"
    else:
        print("\n Sample table \n")
        for instance in session_.query(Sample).order_by(Sample.rssi):
            print(instance.source_address, instance.ap_id, instance.timestamp, instance.rssi)

        print("\n AccessPoint table \n")
        for instance in session_.query(AccessPoint).order_by(AccessPoint.id):
            print(instance.id, instance.mac_address)
        return "\n\rGET ok\n"



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
        session_.add(location)
        session_.flush()

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
                session_.add(fingerprint)

        #Commit and close
        session_.commit()
        session_.close()
        return "\n\rPOST ok\n"

    else:
        print("\n Location table \n")
        for instance in session_.query(Location).order_by(Location.id):
            print(instance.id, instance.x, instance.y, instance.z)

        print("\n Calibrating mobile table \n")
        for instance in session_.query(CalibratingMobile).order_by(CalibratingMobile.mac_address):
            print(instance.mac_address, instance.loc_id)
        
        print("\n Fingerprint value table \n")
        for instance in session_.query(FingerprintValue).order_by(FingerprintValue.id):
            print(instance.id, instance.loc_id, instance.ap_id, instance.rssi)

        return "\n\rGET ok\n"


@app.route("/stop_calibration", methods=['GET', 'POST'])
def stop_calibration():
    """
        TODO: implement this function
        It receives one parameter: mac_addr (string)
        It must delete any calibrating_mobile entry whose mac_address equal parameter mac_addr
    """
    # Your code here
    return "ok"


@app.route("/locate", methods=['GET', 'POST'])
def locate():
    """
        TODO: implement this function
        It receives one parameter: mac_addr (string)
        Must locate the device based on samples less than 1 second old, whose source address equals mac_addr
        These samples are compared to the content of fingerprint_value table
        Use the closest in RSSI algorithm to find a fingerprint sample matching current sample and return its location
    """
    # Your code here
    return None

